<!-- agents-memory v1 | project: jarvis-core | updated: 2026-07-08 | status: ARCHIVED -->

# TODO — jarvis-core

> **REPO ARCHIVIATO (2026-07-08)** — Questo backlog non è più attivo.
> Seguire il backlog operativo in **`/home/neven/dev/jarvis-monitor/.agents/memory/TODO.md`**.
> Piano di riferimento: `MONITORING_PLAN.md` (percorsi tradotti via ADR-005 in `DECISIONS.md`).

---

## Stato migrazione

- [x] Decisione ADR-005: custom integration invece di fork
- [x] Bootstrap repo `jarvis-monitor` completato (scaffold, devcontainer, migrazione file)
- [x] Memoria `jarvis-core` aggiornata per archiviazione
- [ ] Phase 0a+ — **da eseguire in `jarvis-monitor`**, non qui

---

## Backlog storico (fork — non eseguire)

Il backlog sotto riflette il piano originale su `homeassistant/components/`. È conservato solo come riferimento storico.

<details>
<summary>Phase 0a–5 (fork, obsoleto)</summary>

### Phase 0a — Store e ingestion

- [ ] Creare `homeassistant/components/jarvis_monitor/` — **spostato in jarvis-monitor**
- [ ] Schema SQLite, UsageStore, ingestion — **jarvis-monitor Phase 0a**

### Phase 0b–5

Vedi versione storica in git o in `jarvis-monitor/.agents/memory/TODO.md` per il backlog attivo con percorsi corretti.

</details>

---

## Completati (fork)

- [x] Piano monitoring in `MONITORING_PLAN.md` (2026-07-07)
- [x] ADR-001–004 registrati
- [x] Devcontainer funzionante (`DEV_ENVIRONMENT.md`)
- [x] Skill `collaborative-project-memory` installata in `.agents/skills/`
- [x] Pivot a custom integration documentato (`JARVIS_BOOTSTRAP.md`, ADR-005)
