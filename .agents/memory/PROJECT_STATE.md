<!-- agents-memory v1 | project: jarvis | updated: 2026-07-07 -->

# PROJECT_STATE — jarvis

> Stato generale del progetto. Aggiornare solo su cambi architetturali, DB, servizi o procedure di avvio.

## Cos'è

Questo repository contiene `homeassistant`, il core di Home Assistant: fork orientato a **monitoring evoluto multi-bus** (KNX, Lutron, DALI) per impianti domotici. Il codice principale vive in `homeassistant/`, test in `tests/`, script in `script/`, config locale in `config/`.

**Piano di sviluppo monitoring**: `.agents/memory/MONITORING_PLAN.md` (fonte di verità per implementazione).

## Stack e struttura

| Servizio | Tecnologia | Porta | Percorso |
|----------|-----------|-------|----------|
| Core applicativo | Python 3.14 / Home Assistant Core | variabile | `homeassistant/` |
| Monitoring (da implementare) | `jarvis_monitor` integration | n/a | `homeassistant/components/jarvis_monitor/` |
| Frontend monitoring | TypeScript/React (build npm) | servito da HA | `jarvis_monitor/frontend/` → `jarvis_monitor/www/` |
| Test suite | `pytest` | n/a | `tests/` |
| Tooling sviluppo | `uv`, `prek`, `pylint`, `ruff` | n/a | `script/`, `.pre-commit-config.yaml` |
| Config locale | Home Assistant config dir | runtime | `config/` |

## Come si avvia

```bash
script/setup
uv run python -m homeassistant -c ./config
```

Build frontend monitoring (quando implementato):

```bash
cd homeassistant/components/jarvis_monitor/frontend
npm install && npm run build
```

## Database

| DB | Percorso | Scopo | Retention |
|----|----------|-------|-----------|
| **jarvis_monitor usage** (da implementare) | `config/.storage/jarvis_monitor/usage.db` | Utilizzo impianto, presenza, aggregati | Eventi 60gg; aggregati 2 anni |
| **KNX telegrams** (esistente) | `config/.storage/knx/telegrams.db` | Traffico bus KNX grezzo | Configurabile in opzioni KNX |
| **HA Recorder** (standard) | `config/home-assistant_v2.db` | Entity states HA | Configurazione recorder |

Schema dettagliato: `MONITORING_PLAN.md` §5.

## Test

```bash
uv run pytest
uv run pytest tests/components/jarvis_monitor   # quando esiste
uv run pytest tests/components/knx
uv run prek run --all-files
```

## Git

- Branch principale: `dev`
- Branch sviluppo monitoring: `neven/jarvis`
- Vincolo: mai commit/push senza consenso esplicito

## Obiettivo prodotto (monitoring)

Sistema di monitoring evoluto per impianti domotici, appoggiato a Home Assistant:

| Area | Scelta |
|------|--------|
| Architettura | 3 livelli: collector → `jarvis_monitor` → UI (ADR-001) |
| Store dati | SQLite unificato, eventi normalizzati (ADR-002) |
| Collector | Ibrido: entity bridge default; nativo solo presenza e punti senza entità (ADR-004) |
| Retention | Eventi grezzi 60 giorni; aggregati giornalieri 2 anni |
| Soglie numeriche | Globali in config `jarvis_monitor` |
| UI principale | Web custom in-repo (`frontend/` → `www/`) |
| UI avanzata | Pannello HA opzionale (`advanced_panel_enabled`) |
| Alerting | Telegram, email, WhatsApp (adapter) |

### Codice esistente rilevante

- `homeassistant/components/knx/monitoring.py` — presenza KNX (prototipo, da refactor Phase 1)
- `homeassistant/components/knx/telegrams.py` — store telegram bus (non duplicare)
- `homeassistant/components/lutron_leap_custom/` — LEAP monitor (Phase 4)

## Documentazione chiave

| File | Contenuto |
|------|-----------|
| `.agents/memory/MONITORING_PLAN.md` | **Piano implementazione monitoring** |
| `.agents/memory/DECISIONS.md` | ADR-001–004 |
| `.agents/memory/TODO.md` | Backlog operativo per phase |
| `AGENTS.md` | Costituzione operativa repo |
| `.agents/skills/collaborative-project-memory/SKILL.md` | Protocollo SYNC/CHECKPOINT |
