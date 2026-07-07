# Istruzioni per agenti AI

> Se stai lavorando in `.agents/`, leggi subito queste regole. Non attendere istruzioni dall'utente.

## Avvio automatico

1. Leggi `../AGENTS.md` (costituzione progetto)
2. Leggi `skills/collaborative-project-memory/SKILL.md` (protocollo SYNC / CHECKPOINT / INIT)
3. Esegui **SYNC** prima della prima risposta:
   - `memory/ACTIVE_WORK.md`
   - `memory/PROJECT_STATE.md`
   - `memory/WORKLOG.md` (2–3 voci)
   - `memory/BUGS.md`
   - `memory/TODO.md`
4. **Se il task riguarda monitoring / jarvis_monitor / KNX presence / UI custom**:
   - Leggi **`memory/MONITORING_PLAN.md`** per intero (o le sections pertinenti alla phase)
   - Leggi `memory/DECISIONS.md` (ADR-001–004 minimo)

## Durante il lavoro

- Rispetta l'ordine delle fasi in `MONITORING_PLAN.md` §10 (0a → 0b → 0c → 1 → …)
- Migliorie architetturali: nuovo ADR in `memory/DECISIONS.md` **prima** di deviare dal piano
- Aggiorna `memory/WORKLOG.md` e `memory/TODO.md` **dopo ogni operazione completata**
- Claim in `memory/ACTIVE_WORK.md` per task > 30 min
- Checkpoint su richiesta: `sessions/SESSION_SUMMARY.md`
