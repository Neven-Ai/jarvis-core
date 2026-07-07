---
name: collaborative-project-memory
description: Memoria persistente multiagente e multi-utente per progetti software. ESEGUI AUTOMATICAMENTE all'inizio di ogni sessione (SYNC) e dopo ogni operazione completata (aggiorna WORKLOG/TODO/BUGS) senza che l'utente lo chieda. Usa CHECKPOINT a fine sessione; INIT per nuovi progetti. Leggi AGENTS.md e .agents/memory/ prima di rispondere.
---

# Collaborative Project Memory

Skill unificata per **memoria condivisa**, **handover tra agenti** e **coordinamento asincrono multi-utente**.

Agnostica rispetto all'agente (Cursor, Claude Code, Copilot, ecc.): solo file Markdown nel workspace.

## Comportamento autonomo

**Esegui senza che l'utente lo chieda.** Non chiedere "vuoi che aggiorni il WORKLOG?" — fallo nello stesso turno.

| Trigger | Azione |
|---------|--------|
| Primo messaggio della sessione | **SYNC**: leggi memoria, riassumi, controlla `ACTIVE_WORK.md` |
| Dopo feature, fix, migrazione, config, decisione | **SYNC**: aggiorna `WORKLOG.md` (+ `TODO`/`BUGS`/`DECISIONS` se serve) |
| Task > ~30 min | Claim in `ACTIVE_WORK.md` |
| "checkpoint" / fine giornata | **CHECKPOINT** |
| Repo senza `.agents/memory/` | **INIT** con script |

Scoperta automatica: `AGENTS.md` (root), `.github/copilot-instructions.md`, `CLAUDE.md`, `.agents/AGENTS.md`.

---

## Layout standard

```
.agents/
├── README.md
├── memory/
│   ├── PROJECT_STATE.md    # enciclopedia: stack, avvio, DB, test
│   ├── WORKLOG.md          # diario append-only (voce recente in alto)
│   ├── BUGS.md             # bug tracciati con evidenze
│   ├── TODO.md             # backlog prioritizzato
│   ├── ACTIVE_WORK.md      # claim in corso (multi-utente)
│   └── DECISIONS.md        # ADR leggeri (decisioni immutabili)
├── sessions/
│   ├── SESSION_SUMMARY.md  # snapshot sessione corrente
│   └── archive/            # storico checkpoint
├── scripts/
│   ├── init_project_memory.sh
│   └── validate_memory.py
└── skills/
    └── collaborative-project-memory/   # questa skill
```

`AGENTS.md` (root) è la **costituzione** del progetto: regole permanenti + puntatore a questa skill.

## Fonti di verità

| Domanda | File autorevole |
|---------|-----------------|
| Come si avvia / come è fatto? | `PROJECT_STATE.md` |
| Cosa è successo di recente? | `WORKLOG.md` (prime 3 voci) |
| Cosa fare dopo? | `TODO.md` |
| Chi sta lavorando su cosa? | `ACTIVE_WORK.md` |
| Perché abbiamo scelto X? | `DECISIONS.md` |
| Stato runtime ora (git, servizi)? | `SESSION_SUMMARY.md` |
| Bug noti? | `BUGS.md` |

Non duplicare: il checkpoint rimanda al WORKLOG per il dettaglio storico.

---

## Modulo 1: SYNC (ogni sessione e ogni operazione)

### Inizio sessione (OBBLIGATORIO)

1. Leggi `ACTIVE_WORK.md` — evita sovrapposizioni; registra un claim se inizi lavoro significativo
2. Leggi `PROJECT_STATE.md`, `WORKLOG.md` (2–3 voci), `BUGS.md`, `TODO.md`
3. Se esiste, leggi `SESSION_SUMMARY.md` per WIP e stato runtime
4. Riassumi in 2–3 frasi all'utente, poi procedi

### Claim multi-utente (`ACTIVE_WORK.md`)

Prima di un task > ~30 minuti:

```markdown
- [YYYY-MM-DD HH:MM] **autore** — breve descrizione — branch `branch-name` — scade YYYY-MM-DD HH:MM
```

- **autore**: identificativo utente, handle git, o identificativo agente
- Rimuovi la riga a task completato o scaduto
- Non modificare claim altrui; se in conflitto, chiedi all'utente

### Dopo ogni operazione completata (OBBLIGATORIO)

Aggiorna nello **stesso turno**, senza che l'utente lo chieda:

1. **WORKLOG.md** — arricchisci la voce della sessione corrente (una voce per sessione)
2. **BUGS.md** — nuovo bug o risoluzione
3. **TODO.md** — spunta completati, aggiungi emersi
4. **DECISIONS.md** — solo decisioni architetturali nuove (ADR-NNN)
5. **PROJECT_STATE.md** — solo se cambiano architettura, schema DB, servizi, porte, avvio
6. **ACTIVE_WORK.md** — rimuovi claim se hai finito

Non aggiornare per sole letture o domande.

### Template WORKLOG

```markdown
## [YYYY-MM-DD] Titolo sessione (agente: agent-id)
**Richieste**: sintesi 1–3 punti
**Modifiche**:
- `path/file` — cosa e perché
**Decisioni**: (se non già in DECISIONS.md)
**Esito**: completato | parziale | bloccato su X
```

### Template BUG

```markdown
## BUG-NNN: Titolo
- **Stato**: aperto | in analisi | risolto (YYYY-MM-DD)
- **Sintomo**:
- **Evidenze**:
- **Causa**:
- **Fix**:
```

### Template ADR (`DECISIONS.md`)

```markdown
## ADR-NNN: Titolo (YYYY-MM-DD)
- **Contesto**:
- **Decisione**:
- **Alternative scartate**:
- **Conseguenze**:
```

### Regole di scrittura concorrente

- **WORKLOG**: solo prepend (nuova voce in alto); mai riscrivere voci altrui
- **TODO**: aggiunte e spunte; conflitti git risolti manualmente
- **BUGS/ADR**: ID sequenziale; non riusare numeri
- **MAI** secret o credenziali di produzione nei file memoria
- **MAI** commit/push git senza consenso esplicito dell'utente

---

## Modulo 2: CHECKPOINT (fine sessione o su richiesta)

Trigger utente: "crea checkpoint", "riassumi sessione", "salva stato", fine giornata.

### Procedura

1. **Raccogli dati** (lettura git consentita):
   ```bash
   git branch --show-current
   git log -1 --format='%h %s'
   git status --short
   ```

2. **Archivia** checkpoint precedente:
   - Se esiste `.agents/sessions/SESSION_SUMMARY.md`
   - Copia in `.agents/sessions/archive/SESSION_SUMMARY_YYYY-MM-DD_HHMM.md`

3. **Scrivi** `.agents/sessions/SESSION_SUMMARY.md` (template in `assets/SESSION_SUMMARY.example.md`)
   - Solo sezioni pertinenti; **nessun placeholder** `[Da compilare]`

4. **Sincronizza** `TODO.md` con prossimi step del summary

5. **Rimuovi** claim obsoleti da `ACTIVE_WORK.md`

Vedi `references/best-practices.md` per qualità del checkpoint.

Guida installazione multi-IDE: `references/INSTALL.md`.

---

## Modulo 3: INIT (nuovo progetto)

**Guida utente**: `references/INSTALL.md` — installazione e init usando i file presenti in `.agents/`.

Per bootstrap su un repo senza `.agents/`:

```bash
.agents/scripts/init_project_memory.sh [nome-progetto]
```

Oppure manualmente: copia template da `assets/` nelle risposte corrette e crea `AGENTS.md` da `assets/AGENTS.md.template`.

Dopo init, personalizza `PROJECT_STATE.md` (stack, avvio, test).

---

## Validazione

```bash
python3 .agents/scripts/validate_memory.py
```

Segnala file mancanti, `PROJECT_STATE` obsoleto, claim scaduti, formato WORKLOG.

---

## Header file (opzionale)

In cima ai file memoria, per tracciabilità:

```markdown
<!-- agents-memory v1 | project: ProjectName | updated: YYYY-MM-DD -->
```
