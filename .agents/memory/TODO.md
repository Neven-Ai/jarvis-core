<!-- agents-memory v1 | project: jarvis | updated: 2026-07-07 -->

# TODO — jarvis

> **Ultimo aggiornamento**: 2026-07-07
> **Branch**: `neven/jarvis`
> **Piano dettagliato**: `.agents/memory/MONITORING_PLAN.md`

---

## Come usare questo backlog

Seguire le fasi in ordine (0a → 0b → 0c → 1 → …). Ogni task ha criteri di accettazione in `MONITORING_PLAN.md` §10. Migliorie architetturali → nuovo ADR in `DECISIONS.md` prima di implementare.

---

## Phase 0a — Store e ingestion (BLOCCANTE)

- [ ] Creare `homeassistant/components/jarvis_monitor/` — manifest, const, config_flow base
- [ ] Implementare schema SQLite v1 (`store/schema.py`) — tabelle §5 di MONITORING_PLAN
- [ ] Implementare `UsageStore` — insert/query eventi, intervalli, campioni
- [ ] Definire `NormalizedUsageEvent` e pipeline ingestion (`ingestion/`)
- [ ] Config entry: `metric_thresholds` globali, `retention` (60gg / 730gg)
- [ ] Test: `tests/components/jarvis_monitor/test_store.py`, `test_ingestion.py`

## Phase 0b — Entity bridge (collector default)

- [ ] Caricare `monitored_points` da config entry
- [ ] Listener `state_changed` con mapping per dominio (light, cover, climate, fan, switch)
- [ ] Emettere `NormalizedUsageEvent` verso pipeline ingestion
- [ ] Test: `test_entity_bridge.py` con mock `state_changed`

## Phase 0c — Interval engine, retention, API

- [ ] Interval engine: transizioni binarie → `usage_intervals` / `presence_intervals`
- [ ] Job notturno rollup → `daily_aggregates` + eviction 60gg/730gg
- [ ] REST API base: points, intervals, aggregates, health
- [ ] WebSocket: `jarvis_monitor/subscribe`
- [ ] Test: `test_interval_engine.py`, `test_retention.py`

## Phase 1 — KNX presence adapter

- [ ] Refactor `knx/monitoring.py` — intervalli configurabili, i18n, no SQLite diretto
- [ ] `collectors/knx_presence.py` — adapter verso ingestion `jarvis_monitor`
- [ ] Opzionale: `binary_sensor` presenza per device progetto KNX
- [ ] Opzionale: bridge telegram per GA senza entità HA
- [ ] Test KNX monitoring (assenti oggi in `tests/components/knx/`)

## Phase 2 — Alert engine + notify

- [ ] Motore regole: condizione, debounce, severity
- [ ] Adapter Telegram (`notify.telegram`) e email (`notify.smtp`)
- [ ] Adapter WhatsApp (REST / CallMeBot / webhook)
- [ ] Sostituire notifiche hardcoded IT in `knx/monitoring.py`
- [ ] Test alert engine

## Phase 3 — Frontend in-repo MVP

- [ ] Scaffold `jarvis_monitor/frontend/` + `package.json`
- [ ] `npm run build` → `jarvis_monitor/www/`
- [ ] Registrazione static path HA
- [ ] Dashboard: health impianto, device offline, ultimi eventi
- [ ] Grafici: intervalli on/off e aggregati giornalieri
- [ ] Auth long-lived token

## Phase 4 — Lutron + pannello HA opzionale

- [ ] Adapter `lutron_leap_custom/monitor.py` → ingestion presenza
- [ ] `panel_custom` solo se `advanced_panel_enabled: true`
- [ ] Vista compatta health + link a UI custom

## Phase 5 — DALI e estensioni

- [ ] Entity bridge per `sunricher_dali` / `lunatone`
- [ ] Bridge nativo DALI solo se necessario

---

## Bassa Priorità — Repo / tooling

- [x] Allineato `script/hassfest/codeowners.py` a `CODEOWNERS` (commit `592cd6e8ebd`, 2026-07-07)
- [ ] Automatizzare check `www/` aggiornato vs sorgenti frontend in CI
- [ ] Valutare hook locali per sync memoria

---

## Completati

- [x] Piano monitoring consolidato in `MONITORING_PLAN.md` (2026-07-07)
- [x] Commit `d9aff946766` e push branch `neven/jarvis` (2026-07-07)
- [x] ADR-001–004 registrati in `DECISIONS.md`
- [x] Decisioni utente: ibrido, retention 60gg/2anni, soglie globali, frontend in-repo
- [x] Aggiunta e verificata chiave SSH dedicata per push su `jarvis-core`
- [x] Push branch `neven/jarvis` via SSH dedicato
- [x] Commit memoria condivisa e rimozione legacy `.agent/`
- [x] `PROJECT_STATE.md` compilato con contesto reale del repo

---

*Sincronizzato con `.agents/sessions/SESSION_SUMMARY.md` e `MONITORING_PLAN.md`*
