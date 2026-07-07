<!-- agents-memory v1 | project: jarvis | updated: 2026-07-07 -->

# MONITORING_PLAN — Sistema di monitoring evoluto jarvis

> **Fonte di verità per lo sviluppo del prodotto monitoring.**
> Leggere insieme a `DECISIONS.md` (ADR-001–004), `PROJECT_STATE.md` e `TODO.md`.
> Gli agenti possono proporre migliorie, ma devono partire da quanto documentato qui e negli ADR; eventuali deviazioni vanno documentate come nuovo ADR prima di implementare.

---

## 1. Visione e obiettivi

### Prodotto

Sistema di **monitoring evoluto per impianti domotici** (KNX, Lutron, DALI e futuri bus), costruito come fork di Home Assistant Core, con:

| Area | Obiettivo |
|------|-----------|
| **Utilizzo impianto** | Tracciare tempo on/off di luci, motori e attuatori; variazioni di temperature, setpoint, velocità aria, posizioni |
| **Presenza bus** | Sapere se un dispositivo risponde sul bus (KNX individual address, LEAP status, ecc.) |
| **UI principale** | Interfaccia web **completamente custom** e configurabile: dashboard, time-series storiche, report |
| **UI avanzata opzionale** | Pannello nativo HA (`panel_custom`), abilitabile solo per utenti evoluti (`advanced_panel_enabled`) |
| **Alerting** | Regole configurabili con notifiche Telegram, email, WhatsApp (adapter REST) |
| **Multi-bus** | Stessa architettura dati e API per qualsiasi protocollo integrato |

### Principio architetturale

**Nessun bus scrive SQLite direttamente.** Ogni integrazione espone un *adapter* che emette eventi normalizzati verso l'API di ingestion centrale di `jarvis_monitor`.

---

## 2. Stato attuale del codice (baseline)

### Già presente nel repo

| Percorso | Stato | Note |
|----------|-------|------|
| `homeassistant/components/knx/monitoring.py` | Prototipo WIP | Presenza via `nm_individual_address_check`; scan full 30 min / retry 2 min; evento `knx_device_status_changed`; notifiche persistenti hardcoded in italiano; **nessun test, nessuno storico, intervalli hardcoded** |
| `homeassistant/components/knx/knx_module.py` | Integrato | Istanzia `KNXDeviceMonitor`, start/stop nel lifecycle |
| `homeassistant/components/knx/telegrams.py` | Produzione HA | Store SQLite telegram bus (`knx/telegrams.db`); **non** è lo store utilizzo — resta per debug/analisi traffico |
| `homeassistant/components/knx/websocket.py` | Produzione HA | API `knx/query_telegrams`, pannello `knx-frontend` via `panel_custom` |
| `homeassistant/components/lutron_leap_custom/` | Prototipo WIP | LEAP client + monitor presenza; da collegare a `jarvis_monitor` in Phase 4 |
| `homeassistant/components/sunricher_dali/`, `lunatone/` | Stock HA | Nessuna customizzazione monitoring rilevata |

### Non ancora presente

- Integrazione `jarvis_monitor`
- Store SQLite utilizzo
- Entity bridge collector
- Frontend custom
- Test per monitoring

---

## 3. Architettura a three layers

```
┌─────────────────────────────────────────────────────────────────┐
│  LIVELLO 3 — Interfaccia                                        │
│  • Web UI custom (primaria) — jarvis_monitor/frontend/ → www/   │
│  • Pannello HA opzionale — panel_custom se advanced_panel_enabled│
└────────────────────────────┬────────────────────────────────────┘
                             │ REST / WebSocket + auth HA (long-lived token)
┌────────────────────────────▼────────────────────────────────────┐
│  LIVELLO 2 — jarvis_monitor (orchestratore)                     │
│  • UsageStore (SQLite)                                          │
│  • Ingestion API (NormalizedUsageEvent)                         │
│  • Interval engine (sessioni on/off, presenza)                  │
│  • Retention job (rollup + eviction)                            │
│  • Alert engine + notify adapters                               │
│  • REST/WS API per UI e automazioni                             │
└────────────────────────────┬────────────────────────────────────┘
                             │ eventi normalizzati (non scrittura diretta DB)
┌────────────────────────────▼────────────────────────────────────┐
│  LIVELLO 1 — Collector / Adapter per protocollo                 │
│  • Entity bridge (DEFAULT) — state_changed su entità HA mappate   │
│  • KNX presence — knx/monitoring.py refactor → ingestion        │
│  • KNX telegram (opzionale) — GA senza entità HA                  │
│  • Lutron LEAP — lutron_leap_custom/monitor.py (Phase 4)         │
│  • DALI — entity bridge + eventuale poll nativo (futuro)        │
└─────────────────────────────────────────────────────────────────┘
```

### Due dimensioni di monitoring (non confondere)

| Dimensione | Cosa misura | Esempio |
|------------|-------------|---------|
| **Presenza bus** | Il dispositivo risponde sul bus? | KNX `1.1.5` offline |
| **Utilizzo operativo** | Come viene usato l'impianto? | Luce accesa 3h; setpoint 20→22°C |

---

## 4. Strategia collector (ADR-004 — ibrido)

### Default: Entity bridge

Ascolta `state_changed` su entità HA recorded in `monitored_points`. Funziona per **qualsiasi bus** che espone entità HA (KNX, Lutron, DALI, altro).

| Dominio HA | Metriche tracciate |
|------------|-------------------|
| `light` | `power` (on/off), `brightness` |
| `cover` | `power`/`movement`, `position` |
| `climate` | `temperature`, `target_temperature`, `fan_mode` |
| `fan` | `power`, `percentage` |
| `switch`, `binary_sensor` | `power` generico |

Flusso: `Bus → integrazione HA → entità → state_changed → jarvis_monitor → SQLite`

### Bridge nativo bus (solo dove serve)

| Caso | Adapter |
|------|---------|
| Presenza dispositivo sul bus | KNX `monitoring.py`, Lutron LEAP monitor |
| Group address / punto senza entità HA | KNX telegram decode (opzionale) |
| Diagnostica traffico bus | `knx/telegrams.db` + `knx/query_telegrams` (già esistente, non duplicare) |

**Regola per agenti**: non implementare collector nativi per metriche già coperte da entity bridge.

---

## 5. Modello dati SQLite

**Percorso DB**: `config/.storage/jarvis_monitor/usage.db` (o sotto `STORAGE_DIR` HA, da definire in implementazione).

### 5.1 Catalogo punti monitorati

```sql
CREATE TABLE monitored_points (
    point_id        TEXT PRIMARY KEY,
    protocol        TEXT NOT NULL,       -- knx | lutron | dali | ha (informativo)
    source_type     TEXT NOT NULL,       -- entity | knx_device | knx_ga | leap_href
    source_ref      TEXT NOT NULL,       -- entity_id o riferimento nativo
    device_class    TEXT,                -- light | cover | climate | fan | actuator
    label           TEXT,
    config_entry_id TEXT,
    metrics         TEXT NOT NULL,       -- JSON array: ["power","brightness",...]
    enabled         INTEGER NOT NULL DEFAULT 1,
    metadata        TEXT                 -- JSON opzionale
);
```

### 5.2 Event sourcing (hot — 60 giorni)

```sql
CREATE TABLE usage_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    point_id        TEXT NOT NULL,
    protocol        TEXT NOT NULL,
    event_type      TEXT NOT NULL,       -- presence | binary_transition | metric_change
    payload         TEXT NOT NULL,       -- JSON
    recorded_at     TEXT NOT NULL        -- ISO8601 UTC
);
CREATE INDEX idx_usage_events_point_time ON usage_events(point_id, recorded_at);
CREATE INDEX idx_usage_events_type_time ON usage_events(event_type, recorded_at);
```

**Esempi payload**:

```json
{"online": false, "native_id": "1.1.5", "scan_type": "retry"}
{"metric": "power", "from": "off", "to": "on", "entity_id": "light.soggiorno"}
{"metric": "temperature", "from": 20.0, "to": 22.0, "unit": "°C"}
{"metric": "fan_speed", "from": 30, "to": 50, "unit": "%"}
{"metric": "position", "from": 0, "to": 40, "unit": "%"}
```

### 5.3 Intervalli binari (sessioni on/off)

```sql
CREATE TABLE usage_intervals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    point_id        TEXT NOT NULL,
    protocol        TEXT NOT NULL,
    metric          TEXT NOT NULL,       -- power | movement | relay
    value           TEXT NOT NULL,       -- on | off | open | closed | moving
    started_at      TEXT NOT NULL,
    ended_at        TEXT,                -- NULL = ancora attivo
    duration_sec    REAL
);
CREATE INDEX idx_usage_intervals_point ON usage_intervals(point_id, started_at);
```

### 5.4 Campioni numerici

```sql
CREATE TABLE metric_samples (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    point_id        TEXT NOT NULL,
    protocol        TEXT NOT NULL,
    metric          TEXT NOT NULL,
    value           REAL NOT NULL,
    unit            TEXT,
    recorded_at     TEXT NOT NULL
);
CREATE INDEX idx_metric_samples_point_time ON metric_samples(point_id, metric, recorded_at);
```

### 5.5 Presenza bus (intervalli)

```sql
CREATE TABLE presence_intervals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    point_id        TEXT NOT NULL,
    protocol        TEXT NOT NULL,
    online          INTEGER NOT NULL,
    started_at      TEXT NOT NULL,
    ended_at        TEXT
);
CREATE INDEX idx_presence_intervals_point ON presence_intervals(point_id, started_at);
```

### 5.6 Aggregati giornalieri (cold — 2 anni)

```sql
CREATE TABLE daily_aggregates (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    point_id        TEXT NOT NULL,
    protocol        TEXT NOT NULL,
    metric          TEXT NOT NULL,
    agg_date        TEXT NOT NULL,       -- YYYY-MM-DD
    -- Per metriche binarie (es. power=on):
    total_on_sec    REAL,
    transition_count INTEGER,
    -- Per metriche numeriche:
    min_value       REAL,
    max_value       REAL,
    avg_value       REAL,
    sample_count    INTEGER,
    -- Per presenza:
    uptime_pct      REAL,
    UNIQUE(point_id, metric, agg_date)
);
CREATE INDEX idx_daily_aggregates_date ON daily_aggregates(agg_date);
```

### 5.7 Retention (ADR-004)

| Dato | Retention | Azione |
|------|-----------|--------|
| `usage_events` | **60 giorni** | Eliminazione dopo rollup |
| `usage_intervals`, `metric_samples`, `presence_intervals` | **60 giorni** | Eliminazione dopo rollup (o conservare interval chiusi se referenziati da aggregati — da valutare in 0c) |
| `daily_aggregates` | **2 anni (730 giorni)** | Eliminazione |

**Job notturno** (es. 03:00 local time):
1. Calcola `daily_aggregates` per il giorno precedente
2. Elimina record grezzi più vecchi di 60 giorni
3. Elimina aggregati più vecchi di 730 giorni

---

## 6. Contratto evento normalizzato

```python
@dataclass
class NormalizedUsageEvent:
    point_id: str
    protocol: str           # knx | lutron | dali | ha
    event_type: str         # presence | binary_transition | metric_change
    recorded_at: datetime   # UTC
    payload: dict[str, Any]
```

### Pipeline ingestion

1. Valida `point_id` esiste in `monitored_points` ed è `enabled`
2. Applica **soglie numeriche globali** (solo `metric_change`)
3. Inserisce in `usage_events`
4. Aggiorna tabelle derivate:
   - `binary_transition` → apre/chiude `usage_intervals` o `presence_intervals`
   - `metric_change` → inserisce in `metric_samples` se sopra soglia
5. Emette evento HA `jarvis_usage_event` (per automazioni/alert)
6. Opzionale: push WebSocket verso UI connesse

### Evento HA per automazioni

```python
# jarvis_usage_event
{
    "point_id": "soggiorno_luce",
    "protocol": "knx",
    "event_type": "binary_transition",
    "metric": "power",
    "from": "off",
    "to": "on",
    "recorded_at": "2026-07-07T10:00:00+00:00",
}
```

---

## 7. Configurazione

### Opzioni integrazione `jarvis_monitor`

```yaml
# config entry options (schema da implementare in config_flow)
metric_thresholds:          # GLOBALI (ADR-004)
  temperature: 0.5          # °C
  fan_speed: 5              # % o step
  position: 2               # %
  brightness: 5             # %

retention:
  raw_events_days: 60
  aggregates_days: 730

advanced_panel_enabled: false

monitored_points:
  - point_id: soggiorno_luce
    protocol: knx
    source_type: entity
    source_ref: light.soggiorno
    device_class: light
    metrics: [power, brightness]

  - point_id: camera_tapparella
    protocol: knx
    source_type: entity
    source_ref: cover.camera_tapparella
    device_class: cover
    metrics: [power, position]

  - point_id: climatizzatore_zone1
    protocol: knx
    source_type: entity
    source_ref: climate.zone_1
    device_class: climate
    metrics: [temperature, target_temperature, fan_mode]

  - point_id: knx_attuatore_1_1_5
    protocol: knx
    source_type: knx_device
    source_ref: "1.1.5"
    device_class: actuator
    metrics: [presence]

  - point_id: lutron_dimmer_sala
    protocol: lutron
    source_type: entity
    source_ref: light.lutron_sala
    device_class: light
    metrics: [power, brightness]
```

---

## 8. Struttura file target

```
homeassistant/components/jarvis_monitor/
├── __init__.py
├── manifest.json
├── const.py
├── config_flow.py
├── strings.json
├── store/
│   ├── __init__.py
│   ├── schema.py          # DDL + migrazioni
│   ├── usage_store.py     # CRUD + query
│   └── retention.py       # rollup + eviction job
├── ingestion/
│   ├── __init__.py
│   ├── models.py          # NormalizedUsageEvent
│   └── pipeline.py        # validazione → store → eventi HA
├── collectors/
│   ├── __init__.py
│   ├── entity_bridge.py   # state_changed (DEFAULT)
│   ├── knx_presence.py    # adapter da knx/monitoring.py (Phase 1)
│   └── knx_telegram.py    # opzionale (Phase 1)
├── api/
│   ├── __init__.py
│   ├── rest.py
│   └── websocket.py
├── alerts/
│   ├── __init__.py
│   ├── engine.py
│   └── notify_adapters.py # telegram, smtp, whatsapp
├── frontend/
│   ├── package.json
│   ├── src/
│   └── ...                # sorgente TypeScript/React
└── www/                   # output npm run build (servito da HA)

tests/components/jarvis_monitor/
├── conftest.py
├── test_store.py
├── test_ingestion.py
├── test_entity_bridge.py
├── test_interval_engine.py
└── test_retention.py
```

### Build frontend (ADR-003, ADR-004)

```bash
cd homeassistant/components/jarvis_monitor/frontend
npm install
npm run build    # → ../www/
```

Pattern di servizio statico: come `knx/websocket.py` (`StaticPathConfig` + `panel_custom` opzionale).

---

## 9. API previste (Livello 2)

### REST (autenticazione: long-lived access token HA)

| Metodo | Path | Scopo |
|--------|------|-------|
| GET | `/api/jarvis_monitor/points` | Lista `monitored_points` con stato corrente |
| GET | `/api/jarvis_monitor/presence/history` | Storico presenza (filtri: point_id, from, to) |
| GET | `/api/jarvis_monitor/usage/intervals` | Sessioni on/off (filtri: point_id, metric, from, to) |
| GET | `/api/jarvis_monitor/metrics/samples` | Campioni numerici |
| GET | `/api/jarvis_monitor/aggregates/daily` | Aggregati giornalieri |
| GET | `/api/jarvis_monitor/health` | Stato impianto aggregato |

### WebSocket

| Command | Scopo |
|---------|-------|
| `jarvis_monitor/subscribe` | Push real-time su `jarvis_usage_event` |
| `jarvis_monitor/query_intervals` | Query intervalli con paginazione |
| `jarvis_monitor/query_aggregates` | Query aggregati |

### Riuso API esistenti (non duplicare)

- `knx/query_telegrams` — analisi traffico bus KNX (già in `knx/websocket.py`)
- HA `history` API — fallback per entità non ancora in `monitored_points`

---

## 10. Roadmap e criteri di accettazione

### Phase 0a — Store e ingestion (PRIMA di tutto il resto)

**Obiettivo**: fondamenta dati indipendenti dal bus.

| Task | Criterio di accettazione |
|------|-------------------------|
| Scaffold `jarvis_monitor` | `manifest.json`, config flow base, domain caricabile |
| Schema SQLite | Tutte le tabelle §5 create con migrazione v1 |
| `UsageStore` | Insert/query su `usage_events`, `usage_intervals`, `metric_samples` |
| `NormalizedUsageEvent` + pipeline | Test unitari: evento → store → tabelle derivate |
| Config globale | `metric_thresholds` e `retention` in config entry |

**Non iniziare** refactor `knx/monitoring.py` prima del completamento 0a.

### Phase 0b — Entity bridge

| Task | Criterio di accettazione |
|------|-------------------------|
| Mapping `monitored_points` | Caricamento da config entry |
| Listener `state_changed` | Rileva transizioni light/cover/climate/fan |
| Mapping metriche per dominio | `power`, `brightness`, `position`, `temperature`, ecc. |
| Test | Simulazione `state_changed` → eventi in store |

### Phase 0c — Interval engine + retention + API query

| Task | Criterio di accettazione |
|------|-------------------------|
| Interval engine | Apertura/chiusura `usage_intervals` su transizioni binarie |
| Job retention | Rollup giornaliero + eviction 60gg/2anni |
| API query base | REST endpoints per intervals e aggregates |
| Test retention | Verifica eviction e rollup su dati sintetici |

### Phase 1 — KNX presence adapter

| Task | Criterio di accettazione |
|------|-------------------------|
| Refactor `knx/monitoring.py` | Intervalli configurabili; i18n; nessuna scrittura SQLite diretta |
| Adapter → ingestion | Presenza emette `NormalizedUsageEvent` type `presence` |
| `binary_sensor` opzionale | Entità HA per presenza device |
| Test KNX | Scan full/retry, transizioni, bus disconnesso |
| Rimuovere notifiche hardcoded IT | Alert delegati a `jarvis_monitor` (Phase 2) o evento HA |

### Phase 2 — Alert engine + notify

| Task | Criterio di accettazione |
|------|-------------------------|
| Regole alert | Condizione, debounce (`for`), severity, canali |
| Telegram + email | Via `notify.*` esistenti |
| WhatsApp | Adapter REST (CallMeBot o webhook) |
| Test | Regola offline → notify chiamato dopo debounce |

### Phase 3 — Frontend in-repo MVP

| Task | Criterio di accettazione |
|------|-------------------------|
| Scaffold `frontend/` | `npm run build` → `www/` |
| Dashboard health | % device online, ultimi allarmi |
| Grafici storici | Intervalli on/off e aggregati giornalieri |
| Auth | Long-lived token HA |

### Phase 4 — Lutron + pannello HA opzionale

| Task | Criterio di accettazione |
|------|-------------------------|
| Adapter `lutron_leap_custom/monitor.py` | Presenza → ingestion |
| Entity bridge | Luci/dimmer Lutron già coperti da 0b se esposti come entità |
| `panel_custom` | Registrato solo se `advanced_panel_enabled: true` |

### Phase 5 — DALI e bridge nativi aggiuntivi

| Task | Criterio di accettazione |
|------|-------------------------|
| Entity bridge DALI | Copertura `sunricher_dali` / `lunatone` |
| Bridge nativo DALI | Solo se richiesto per punti senza entità |

---

## 11. Regole per agenti in sessioni future

1. **SYNC obbligatorio**: leggere questo file + `DECISIONS.md` + `TODO.md` prima di implementare.
2. **Ordine fasi**: rispettare 0a → 0b → 0c → 1 → 2 → 3 → 4 → 5 salvo nuovo ADR.
3. **Migliorie benvenute** se documentate: aprire ADR-NNN in `DECISIONS.md` prima di deviare dal piano.
4. **Non duplicare**: usare `knx/query_telegrams` per traffico bus; non creare secondo store telegram.
5. **Test obbligatori**: ogni phase include test; parametri tipizzati; preferire `@pytest.mark.parametrize`.
6. **Git**: mai commit/push senza consenso esplicito utente.
7. **Claim**: task > 30 min → riga in `ACTIVE_WORK.md`.
8. **Handover**: aggiornare `WORKLOG.md` e `TODO.md` a fine sessione.

---

## 12. Riferimenti incrociati

| Documento | Contenuto |
|-----------|-----------|
| `DECISIONS.md` | ADR-001 (architettura 3 layers), ADR-002 (store SQLite), ADR-003 (frontend in-repo), ADR-004 (ibrido + retention + soglie) |
| `PROJECT_STATE.md` | Stack, avvio, test, sintesi obiettivo prodotto |
| `TODO.md` | Backlog operativo spuntabile |
| `WORKLOG.md` | Storico sessioni |
| `homeassistant/components/knx/monitoring.py` | Baseline presence KNX |
| `homeassistant/components/knx/telegrams.py` | Store telegram bus (standalone) |
| `homeassistant/components/knx/websocket.py` | Pattern panel + WS API |

---

*Ultimo aggiornamento: 2026-07-07 — Piano consolidato e approvato dall'utente.*
