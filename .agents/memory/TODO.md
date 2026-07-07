<!-- agents-memory v1 | project: jarvis | updated: 2026-07-07 -->

# TODO — jarvis

> **Ultimo aggiornamento**: 2026-07-07
> **Branch**: `dev`

---

## Alta Priorità

- [ ] Sbloccare l'ambiente di sviluppo per i commit: `script/setup` fallisce per assenza di `python3.14-venv` e il hook pre-commit non trova `prek`
- [ ] Decidere se consolidare in un commit dedicato le modifiche a `.agents/`, `CODEOWNERS` e `script/hassfest/codeowners.py`

---

## Media Priorità

- [ ] Arricchire `TODO.md` con backlog di sviluppo reale del repo quando emergono task funzionali oltre alla pulizia della memoria

---

## Bassa Priorità / Idee Future

- [ ] Valutare se automatizzare ulteriormente la sincronizzazione della memoria tramite script o hook locali

---

## Completati

- [x] Creato il primo `SESSION_SUMMARY.md` come checkpoint iniziale della memoria condivisa
- [x] Eseguita la validazione della memoria condivisa con `python3 .agents/scripts/validate_memory.py` (esito OK; manca solo un checkpoint iniziale)
- [x] Compilato `PROJECT_STATE.md` con contesto reale del repository: stack, avvio, test, branch e documentazione chiave
- [x] Rimosse dalla root la cartella legacy `.agent` e gli artefatti `SETUP.md` / `collaborative-project-memory-kit.tar.gz`; resta solo la skill in `.agents`
- [x] Rimossi i riferimenti legacy a `.agent` da `CODEOWNERS` e `script/hassfest/codeowners.py`

---

*Sincronizzato con `.agents/sessions/SESSION_SUMMARY.md`*
