# Istruzioni per agenti AI — jarvis-core (ARCHIVED)

> **Repo archiviato (ADR-005, 2026-07-08).** Non implementare feature jarvis qui.
> Repo attivo: **`jarvis-monitor`** — memoria in `/home/neven/dev/jarvis-monitor/.agents/`.

## Avvio automatico

1. Leggi `memory/PROJECT_STATE.md` — se il task è sviluppo, **reindirizza a jarvis-monitor**
2. Leggi `skills/collaborative-project-memory/SKILL.md` (protocollo SYNC / CHECKPOINT / INIT)
3. SYNC (solo se consulti questo repo come riferimento):
   - `memory/PROJECT_STATE.md`, `memory/WORKLOG.md`, `memory/DECISIONS.md`
4. Bootstrap migrazione: [`../JARVIS_BOOTSTRAP.md`](../JARVIS_BOOTSTRAP.md)

## Durante il lavoro

- **Non** avviare Phase 0a+ su questo fork
- Codice di riferimento utile: `knx/monitoring.py`, `lutron_leap_custom/` (già migrati o da portare)
- Aggiorna `memory/WORKLOG.md` solo per modifiche a questa memoria o al bootstrap
- Checkpoint su richiesta: `sessions/SESSION_SUMMARY.md`
