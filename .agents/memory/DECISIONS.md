# DECISIONS — jarvis

> Architecture Decision Records (ADR). Non riscrivere decisioni passate.

---

## ADR-001 — Architettura monitoring multi-protocollo (2026-07-07)

**Contesto**: serve un sistema di monitoring evoluto per impianti KNX/Lutron/DALI, con UI web custom come percorso principale e pannello HA nativo opzionale per utenti avanzati.

**Decisione**: approccio ibrido a three layers.

1. **Collector per protocollo** — estendere i monitor esistenti (`knx/monitoring.py`, futuro `lutron_leap_custom`) per emettere eventi e HA states standardizzati e persistere transizioni di presenza.
2. **Integrazione orchestratore `jarvis_monitor`** — nuovo dominio dedicato ad API (REST/WebSocket), regole di allarme, report e notifiche (Telegram, email, WhatsApp via adapter).
3. **UI** — frontend web custom (primario) che consuma le API HA; pannello nativo opzionale registrato solo se abilitato in config.

**Motivazione**: separa raccolta dati di bus da UX e alerting; riusa infrastruttura HA (auth, recorder, notify, websocket); evita di inquinare l'integrazione KNX upstream con logica prodotto.

**Conseguenze**: `knx/monitoring.py` va rifattorizzato (configurabile, testato, entità HA); serve store storico presenza; WhatsApp richiede integrazione custom o servizio esterno.

## ADR-002 — Store SQLite unificato per utilizzo impianto (2026-07-07)

**Contesto**: oltre alla presenza bus, serve tracciare utilizzo reale (tempo on/off luci e motori, variazioni temperature/velocità aria, ecc.) con schema replicabile su KNX, Lutron, DALI e futuri bus.

**Decisione**: un unico database SQLite gestito da `jarvis_monitor`, con modello a eventi normalizzati + tabelle derivate per intervalli binari e campioni numerici. I collector per protocollo non scrivono SQLite direttamente: emettono eventi verso un'API di ingestion centrale.

**Motivazione**: evita N database per bus; query/report uniformi; nuovo protocollo = nuovo adapter, stesso store.

**Conseguenze**: Phase 1a KNX posticipata fino a schema store + contratto ingestion; collector generico su `state_changed` HA come primo adapter universale.

## ADR-003 — Frontend custom in-repo (2026-07-07)

**Contesto**: chiarito che non servono due UI diverse né un repository Git separate.

**Decisione**: una sola UI web custom, sorgenti e build dentro `jarvis-core` sotto `homeassistant/components/jarvis_monitor/frontend/` (sorgente) e asset statici serviti da HA come per il pannello KNX.

**Motivazione**: deploy unico, stesso ciclo di release del core fork, nessuna dipendenza pip esterna per il frontend.

## ADR-004 — Collector ibrido e policy dati (2026-07-07)

**Contesto**: scelte operative confermate dall'utente prima della Phase 0.

**Decisioni**:

| Tema | Scelta |
|------|--------|
| Percorso dati utilizzo | **Ibrido**: entity bridge come default; bridge nativo bus solo per presenza e punti senza entità HA |
| Retention eventi grezzi | **60 giorni** (`usage_events`, transizioni puntuali) |
| Retention aggregati | **2 anni** (rollup giornalieri: durate on/off, min/max/avg metriche) |
| Soglie numeriche | **Globali** in config `jarvis_monitor` (es. Δ temperatura minima prima di registrare) |
| Build frontend | **`npm run build`** in `jarvis_monitor/frontend/` → output in `jarvis_monitor/www/` servito da HA |

**Conseguenze**: job notturno di eviction + rollup; una sola sezione config per soglie; documentare `npm run build` nel workflow dev.

## ADR-005 — jarvis_monitor come custom integration, non fork (2026-07-08)

**Contesto**: il progetto era nato come fork di `home-assistant/core` (repo `jarvis-core`, branch `neven/jarvis`). Dopo analisi è stato deciso di riconvertirlo in **custom integration** in un repository dedicato (`jarvis-monitor`).

**Decisione**: tutto il codice jarvis vive in `custom_components/jarvis_monitor/` (+ `custom_components/lutron_leap_custom/`); Home Assistant è una dipendenza pip pinnata (`homeassistant==2026.7.1` al bootstrap). Il fork `jarvis-core` resta in sola lettura come riferimento, poi si archivia.

**Motivazione**:

1. Nulla nel piano richiede modifiche al core: entity bridge (`state_changed`), store SQLite proprio, REST/WS API custom, `StaticPathConfig` + `panel_custom` sono tutti disponibili alle custom integration.
2. L'accesso al bus KNX per la presenza avviene tramite l'oggetto `xknx` dell'integrazione KNX ufficiale, via `hass.data` — senza patchare `homeassistant/components/knx/`.
3. Il fork impone rebase mensili su `dev` e accoppia gli aggiornamenti jarvis agli aggiornamenti HA; la custom integration si aggiorna in modo indipendente su HA stock.

**Regola permanente**: se emerge un requisito che sembra richiedere modifiche al core, NON tornare al fork. Documentare in `DECISIONS.md` e valutare una PR upstream a `home-assistant/core`.

**Mappa di traduzione percorsi** (ovunque `MONITORING_PLAN.md` citi percorsi del fork):

| Nel piano (fork) | Nel nuovo repo (`jarvis-monitor`) |
|------------------|-----------------------------------|
| `homeassistant/components/jarvis_monitor/` | `custom_components/jarvis_monitor/` |
| `homeassistant/components/knx/monitoring.py` | `custom_components/jarvis_monitor/collectors/knx_presence.py` |
| `homeassistant/components/lutron_leap_custom/` | `custom_components/lutron_leap_custom/` |
| `tests/components/jarvis_monitor/` | `tests/jarvis_monitor/` |
| `script/setup`, `hass -c config` | `scripts/setup`, `scripts/develop` |
| Branch `neven/jarvis` | `main` / `feat/<phase>-<slug>` |

**Conseguenze**: `jarvis-core` archiviato; sviluppo attivo solo in `jarvis-monitor`. ADR-003 (frontend in-repo) resta valido con percorso aggiornato: `custom_components/jarvis_monitor/frontend/` → `www/`.
