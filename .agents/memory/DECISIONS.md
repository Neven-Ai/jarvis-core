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
