# Istruzioni per agenti AI

> Se stai lavorando in `.agents/`, leggi subito queste regole. Non attendere istruzioni dall'utente.

## Avvio automatico

1. Leggi `../AGENTS.md` (costituzione progetto)
2. Leggi `skills/collaborative-project-memory/SKILL.md` (protocollo SYNC / CHECKPOINT / INIT)
3. Esegui **SYNC** prima della prima risposta: `.agents/memory/ACTIVE_WORK.md`, `PROJECT_STATE.md`, `WORKLOG.md`, `BUGS.md`, `TODO.md`

## Durante il lavoro

- Aggiorna `memory/WORKLOG.md` e `memory/TODO.md` **dopo ogni operazione completata**, nello stesso turno, senza che l'utente lo chieda.
- Claim in `memory/ACTIVE_WORK.md` per task > 30 min.
- Checkpoint su richiesta utente: `sessions/SESSION_SUMMARY.md` (modulo CHECKPOINT della skill).
