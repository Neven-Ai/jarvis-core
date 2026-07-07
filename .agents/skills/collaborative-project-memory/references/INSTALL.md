# Installazione e utilizzo — Collaborative Project Memory

Guida per installare e usare la skill su **qualsiasi IDE e agente AI**.  
La skill non dipende da API o plugin: funziona con **file Markdown nel repository**, leggibili da tutti gli agenti.

---

## Dove sono le istruzioni

| Documento | Percorso | Contenuto |
|-----------|----------|-----------|
| **Questa guida** | `.agents/skills/collaborative-project-memory/references/INSTALL.md` | Installazione, IDE, uso quotidiano |
| **Protocollo operativo** | `.agents/skills/collaborative-project-memory/SKILL.md` | SYNC, CHECKPOINT, INIT (per gli agenti) |
| **Best practices** | `.agents/skills/collaborative-project-memory/references/best-practices.md` | Qualità checkpoint e claim |
| **Panoramica progetto** | `.agents/README.md` | Layout file memoria |
| **Regole permanenti** | `AGENTS.md` (root repo) | Cosa deve fare ogni agente su questo progetto |

---

## Principio

```
Repository Git
├── AGENTS.md              ← l'agente lo legge sempre (se configurato)
├── .agents/memory/        ← memoria condivisa (commitata nel repo)
└── .agents/skills/...     ← definizione della skill (commitata nel repo)
```

Tutti gli sviluppatori e tutti gli agenti leggono e aggiornano **gli stessi file**.  
Il coordinamento multi-utente avviene via git + `ACTIVE_WORK.md`.

---

## Installazione su un nuovo progetto

### Opzione A — Copia manuale da un progetto esistente

1. Copia nel nuovo repo:
   ```
   .agents/skills/collaborative-project-memory/   (intera cartella)
   .agents/scripts/
   ```
2. Esegui init:
   ```bash
   chmod +x .agents/scripts/init_project_memory.sh
   .agents/scripts/init_project_memory.sh "ProjectName"
   ```
   Lo script crea automaticamente: `AGENTS.md`, `.github/copilot-instructions.md`, `CLAUDE.md`, `.agents/AGENTS.md`, file memoria.
3. Compila `.agents/memory/PROJECT_STATE.md` (stack, avvio, test).
4. Collega l'agente del tuo IDE (opzionale se init ha creato i file — vedi tabella sotto).
5. Commit:
   ```bash
   git add .agents/ AGENTS.md
   git commit -m "Add collaborative project memory"
   ```

### Opzione B — Skill globale (solo Cursor / editor con skill utente)

Copia la cartella `collaborative-project-memory` in:

- **Cursor**: `~/.cursor/skills/collaborative-project-memory/`
- Poi su ogni progetto esegui solo `init_project_memory.sh` per creare `.agents/memory/`.

La skill globale definisce il *come*; i dati restano in `.agents/memory/` del singolo repo.

### Validazione

```bash
python3 .agents/scripts/validate_memory.py
```

---

## Collegamento per IDE / agente

La skill si attiva **automaticamente** se esiste almeno uno dei file sotto.  
`init_project_memory.sh` li crea tutti su un nuovo progetto.

| IDE / agente | File auto-caricato | Creato da init |
|--------------|-------------------|----------------|
| **Cursor** | `AGENTS.md` (root) | sì |
| **VS Code + Copilot** | `.github/copilot-instructions.md` | sì |
| **Claude Code** | `CLAUDE.md` | sì |
| **Esplorazione `.agents/`** | `.agents/AGENTS.md` | sì |
| **Cursor (skill)** | `SKILL.md` frontmatter `description` | copia skill |

**Non serve che l'utente dica "leggi la memoria"**: le regole impongono SYNC al primo turno e aggiornamento WORKLOG dopo ogni operazione, senza chiedere conferma.

### Cursor

1. `AGENTS.md` in root è letto automaticamente.
2. Opzionale: copia la skill in `.cursor/skills/` del progetto o in `~/.cursor/skills/` per tutti i progetti.
3. In chat puoi dire: *“Segui `.agents/skills/collaborative-project-memory/SKILL.md`”*.

### VS Code (GitHub Copilot, Continue, Cody, ecc.)

1. Crea o aggiorna **`.github/copilot-instructions.md`** (Copilot) con:

   ```markdown
   # Istruzioni agente

   All'inizio di ogni sessione leggi `AGENTS.md` e i file in `.agents/memory/`.
   Protocollo completo: `.agents/skills/collaborative-project-memory/SKILL.md`
   ```

2. In alternativa molti agenti riconoscono **`AGENTS.md`** in root (standard emergente).

3. Per **Continue**: aggiungi in `.continue/config.json` un riferimento a `AGENTS.md` nelle `systemMessage` o nelle rules del progetto.

### Claude Code (CLI / Desktop)

Crea **`CLAUDE.md`** in root:

```markdown
# Claude — istruzioni progetto

Leggi e applica sempre:
- `AGENTS.md`
- `.agents/skills/collaborative-project-memory/SKILL.md`

All'avvio: leggi `.agents/memory/ACTIVE_WORK.md`, `PROJECT_STATE.md`, `WORKLOG.md` (3 voci), `BUGS.md`, `TODO.md`.
```

### Windsurf

Crea **`.windsurfrules`** con lo stesso contenuto di `AGENTS.md` + puntatore alla skill.

### OpenAI Codex / altri agenti generici

Includi nel system prompt o nel file di istruzioni del progetto:

```
Segui AGENTS.md e .agents/skills/collaborative-project-memory/SKILL.md.
Memoria in .agents/memory/. Aggiorna WORKLOG dopo ogni modifica completata.
```

### Nessun IDE specifico (solo file)

Funziona anche senza configurazione IDE: basta che l'umano o l'agente apra `AGENTS.md` e la skill.  
Utile per handover via git tra persone che usano IDE diversi.

---

## Template `AGENTS.md` (root)

```markdown
# Istruzioni per agenti AI — ProjectName

Memoria: `.agents/` — skill: `.agents/skills/collaborative-project-memory/SKILL.md`

## Regole obbligatorie

1. **Inizio sessione**: leggi `.agents/memory/ACTIVE_WORK.md`, `PROJECT_STATE.md`,
   `WORKLOG.md` (voci recenti), `BUGS.md`, `TODO.md`. Riassumi in 2–3 frasi.
2. **Task lunghi**: registra un claim in `ACTIVE_WORK.md`.
3. **Dopo ogni operazione completata**: aggiorna WORKLOG, BUGS, TODO; ADR se serve;
   PROJECT_STATE solo su cambi strutturali; rimuovi claim se finito.
4. **Mai** commit/push senza consenso esplicito dell'utente.
5. **Mai** secret o credenziali reali nei file memoria.

## Contesto rapido

<!-- stack, comandi avvio, test -->
```

Template completo: `assets/AGENTS.md.template`.

---

## Utilizzo quotidiano

### Per lo sviluppatore

| Azione | Esempio / frase all'agente |
|--------|---------------------------|
| Iniziare sessione | L'agente legge memoria automaticamente se `AGENTS.md` è configurato |
| Claim su un task | Modifica `.agents/memory/ACTIVE_WORK.md` o chiedi all'agente |
| Fine giornata | *"Crea un checkpoint"* → scrive `SESSION_SUMMARY.md` |
| Verificare layout | `python3 .agents/scripts/validate_memory.py` |
| Vedere backlog | Apri `.agents/memory/TODO.md` |
| Vedere storico | Apri `.agents/memory/WORKLOG.md` |

### Per l'agente (automatico se segue la skill)

| Trigger | Cosa fa |
|---------|---------|
| Inizio sessione | SYNC: legge memoria, riassume, evita conflitti con ACTIVE_WORK |
| Dopo ogni fix/feature | Aggiorna WORKLOG + TODO (+ BUGS/ADR se serve) |
| Fine sessione | CHECKPOINT su richiesta |
| Nuovo progetto | INIT con script |

### Coordinamento team (2+ persone / agenti in parallelo)

1. **Prima di iniziare**: `git pull` + leggi `ACTIVE_WORK.md`
2. **Registra claim** per task > 30 min
3. **Commit frequenti** su `.agents/memory/` insieme al codice
4. **Conflitti su WORKLOG**: unisci entrambe le voci (prepend), non cancellare

---

## Cosa committare in git

| Committare | Non committare |
|------------|----------------|
| `.agents/memory/*.md` | Secret, password produzione |
| `.agents/sessions/` | File locali temporanei |
| `.agents/skills/` | |
| `.agents/scripts/` | |
| `AGENTS.md` | |

La memoria **fa parte del progetto**: chi clona il repo eredita contesto e backlog.

---

## Portare la skill su un altro repo (checklist)

- [ ] Copiare `.agents/skills/collaborative-project-memory/`
- [ ] Copiare `.agents/scripts/`
- [ ] Eseguire `init_project_memory.sh` (crea anche file auto-discovery IDE)
- [ ] Compilare `PROJECT_STATE.md`
- [ ] `python3 .agents/scripts/validate_memory.py` (verifica layout + auto-discovery)
- [ ] Commit e push

---

## Risoluzione problemi

| Problema | Soluzione |
|----------|-----------|
| L'agente non aggiorna WORKLOG | Richiamare `AGENTS.md`; in Cursor verificare che le rules siano attive |
| Due persone sullo stesso task | Controllare `ACTIVE_WORK.md`; usare branch separati |
| PROJECT_STATE obsoleto | Aggiornare dopo cambi architetturali; validate segnala > 14 giorni |
| Agente diverso non capisce il contesto | Non dipende dall'IDE: basta che legga gli stessi file in `.agents/memory/` |
