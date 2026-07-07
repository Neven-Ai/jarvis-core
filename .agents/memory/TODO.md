<!-- agents-memory v1 | project: jarvis | updated: 2026-07-07 -->

# TODO — jarvis

> **Ultimo aggiornamento**: 2026-07-07
> **Branch**: `neven/jarvis`

---

## Alta Priorità

- [ ] Valutare se allineare anche `script/hassfest/codeowners.py` al riferimento rimosso da `CODEOWNERS`

---

## Media Priorità

- [ ] Arricchire `TODO.md` con backlog di sviluppo reale del repo quando emergono task funzionali oltre alla pulizia della memoria

---

## Bassa Priorità / Idee Future

- [ ] Valutare se automatizzare ulteriormente la sincronizzazione della memoria tramite script o hook locali

---

## Completati

- [x] Aggiunta e verificata la nuova chiave SSH dedicata per il push su `jarvis-core`
- [x] Eseguito il push del branch `neven/collaborative-memory-cleanup` verso `origin` via SSH dedicato
- [x] Creata la chiave SSH dedicata `~/.ssh/id_ed25519_github_jarvis_nevendev` senza passphrase
- [x] Sbloccato il commit locale creando una `.venv` minima con `pip` e `prek`, spostando il lavoro su un branch dedicato
- [x] Creato il commit `8605cf072fb` su `neven/collaborative-memory-cleanup` per `.agents/`, `CODEOWNERS` e la rimozione di `/.agent/skills`
- [x] Creato il primo `SESSION_SUMMARY.md` come checkpoint iniziale della memoria condivisa
- [x] Eseguita la validazione della memoria condivisa con `python3 .agents/scripts/validate_memory.py` (esito OK; manca solo un checkpoint iniziale)
- [x] Compilato `PROJECT_STATE.md` con contesto reale del repository: stack, avvio, test, branch e documentazione chiave
- [x] Rimosse dalla root la cartella legacy `.agent` e gli artefatti `SETUP.md` / `collaborative-project-memory-kit.tar.gz`; resta solo la skill in `.agents`
- [x] Rimossi i riferimenti legacy a `.agent` da `CODEOWNERS` e `script/hassfest/codeowners.py`

---

*Sincronizzato con `.agents/sessions/SESSION_SUMMARY.md`*
