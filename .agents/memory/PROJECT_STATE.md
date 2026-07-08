<!-- agents-memory v1 | project: jarvis-core | updated: 2026-07-08 | status: ARCHIVED -->

# PROJECT_STATE — jarvis-core

> **REPO ARCHIVIATO (2026-07-08)** — Non sviluppare nuove feature qui.
> Il progetto jarvis prosegue come **custom integration** nel repository dedicato **`jarvis-monitor`** (`/home/neven/dev/jarvis-monitor`).
> Questo fork di `home-assistant/core` resta in **sola lettura** come riferimento storico fino a completa migrazione, poi da archiviare su GitHub.

## Dove lavorare ora

| Domanda | Risposta |
|---------|----------|
| Repo attivo | `jarvis-monitor` — custom integration HA |
| Piano implementazione | `/home/neven/dev/jarvis-monitor/.agents/memory/MONITORING_PLAN.md` |
| Decisioni architetturali | ADR-001–005 in entrambi i repo; **ADR-005** definisce il pivot |
| Bootstrap migrazione | [`JARVIS_BOOTSTRAP.md`](../../JARVIS_BOOTSTRAP.md) (questo repo) |
| Memoria agenti attiva | `/home/neven/dev/jarvis-monitor/.agents/` |

## Cos'era questo repository

Fork di Home Assistant Core (branch `neven/jarvis`) per prototipare monitoring multi-bus (KNX, Lutron, DALI). Il codice di riferimento utile per la migrazione:

| Sorgente (qui) | Destinazione (`jarvis-monitor`) |
|----------------|--------------------------------|
| `homeassistant/components/knx/monitoring.py` | `custom_components/jarvis_monitor/collectors/knx_presence.py` (Phase 1) |
| `homeassistant/components/lutron_leap_custom/` | `custom_components/lutron_leap_custom/` (già migrato) |
| `.agents/memory/MONITORING_PLAN.md` | copiato invariato |
| `.agents/skills/collaborative-project-memory/` | copiato |

## Stack (storico — solo per consultazione)

| Componente | Percorso nel fork |
|------------|-------------------|
| HA Core fork | `homeassistant/` |
| Prototipo KNX presence | `homeassistant/components/knx/monitoring.py` |
| Lutron LEAP custom | `homeassistant/components/lutron_leap_custom/` |
| Devcontainer | `.devcontainer/devcontainer.json` + `Dockerfile.dev` |
| Config HA locale | `config/` |

## Avvio (solo se serve consultare il fork)

```bash
script/setup
uv run python -m homeassistant -c ./config
```

Vedi anche [`DEV_ENVIRONMENT.md`](DEV_ENVIRONMENT.md) per il setup devcontainer (obsoleto per nuovo sviluppo).

## Git

- Branch sviluppo storico: `neven/jarvis`
- **Nessun nuovo sviluppo** su questo repo senza decisione esplicita
- Vincolo: mai commit/push senza consenso esplicito

## Documentazione chiave (questo repo)

| File | Contenuto |
|------|-----------|
| [`JARVIS_BOOTSTRAP.md`](../../JARVIS_BOOTSTRAP.md) | Istruzioni migrazione fork → custom integration |
| `.agents/memory/DECISIONS.md` | ADR-001–005 |
| `.agents/memory/MONITORING_PLAN.md` | Piano (copia; fonte operativa in `jarvis-monitor`) |
| `.agents/memory/DEV_ENVIRONMENT.md` | Setup devcontainer fork (storico) |
