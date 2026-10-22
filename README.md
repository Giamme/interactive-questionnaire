# interactive-questionnaire

An agent skill that turns a set of questions into a **shareable questionnaire page on claude.ai**, or into **a single HTML file** for people who don't use claude.ai. Several people fill it in, one after another, and the page keeps every answer. Claude reads the answers back and summarizes them.

The skill is built for decision rounds, where you have a recommendation and want the team to agree or say what instead. It also handles plain multiple choice and open questions.

## What the page does

- **Saves answers per person.** Each answer goes under the person's name in the page's own shared store, and everyone can see the team's answers under each question.
- **Three kinds of question:**
  - `decision`: «Yes, as recommended / A different answer / Not sure»;
  - `choice`: your own options, plus «Something else» with a line for the answer, and «Not sure»;
  - `open`: a written answer.
- **One or more languages,** with a switch at the top. Italian and English are built in, and another language needs its own UI strings.
- **One question at a time:** answering closes the card into a one-line summary and scrolls to the next unanswered question.
- **Ways around the page:**
  - floating buttons for the top, the next unanswered question and the last question;
  - a sidebar with a tick for each of your answers, which becomes a drawer on phones;
  - filters for «not answered by me» and «not answered by anyone».
- **Answers by message for anyone it can't save for:** view-only readers, people claude.ai doesn't identify on the page, and visitors without a Claude account. «Send your answers» makes a one-line code they paste into a message; the owner pastes it into the page, and the answers join the team's under the sender's name.
- **Copy in one line:** «Copy all answers» copies everyone's answers, with names, as one compressed line of letters and digits. The owner can paste it back into the page, which adds anyone missing, or paste it to Claude.
- **Light and dark themes,** keyboard friendly, and it respects reduced motion.

## Install

What you get depends on the agent:

| Agent | What it makes |
|---|---|
| Claude Code signed in to a claude.ai account that can publish Artifacts | the claude.ai page, or the file on request |
| Claude Code on an API key, Bedrock or Vertex; Codex, Copilot CLI, Cursor, Gemini CLI, OpenCode and others | the single HTML file |

The scripts need Python 3.10 or newer. Node.js is optional: `build.py` uses it to check that the page's script parses.

### Claude Code

```
/plugin marketplace add Giamme/interactive-questionnaire
/plugin install interactive-questionnaire@interactive-questionnaire
```

From a shell: `claude plugin marketplace add Giamme/interactive-questionnaire && claude plugin install interactive-questionnaire@interactive-questionnaire`.

### Codex

```sh
codex plugin marketplace add Giamme/interactive-questionnaire
codex plugin add interactive-questionnaire@interactive-questionnaire
```

### GitHub Copilot CLI

```sh
copilot plugin marketplace add Giamme/interactive-questionnaire
copilot plugin install interactive-questionnaire@interactive-questionnaire
```

### Cursor, Gemini CLI, Antigravity, OpenCode, Windsurf/Devin, Amp, Kiro and others

Install the skill with [`npx skills`](https://github.com/vercel-labs/skills), which knows where each agent looks:

```sh
npx skills add Giamme/interactive-questionnaire            # pick agents interactively
npx skills add Giamme/interactive-questionnaire -g -a cursor -a gemini-cli -a opencode -y
```

### From a clone

To track `main` and update every agent with a `git pull`, clone the repo and symlink the skill into each agent that's installed:

```sh
git clone https://github.com/Giamme/interactive-questionnaire ~/src/interactive-questionnaire
~/src/interactive-questionnaire/scripts/install --dry-run   # see what would be linked
~/src/interactive-questionnaire/scripts/install             # every detected agent; or --client codex --client claude
~/src/interactive-questionnaire/scripts/install --uninstall
```

Install the skill in one place per agent. With the Claude Code plugin installed, don't also link the skill into `~/.claude/skills`, or Claude Code lists it twice.

**Upgrading an older install:** the skill used to sit at the root of the repo and now lives in `skills/interactive-questionnaire/`. If you linked the whole clone into `~/.claude/skills/interactive-questionnaire`, remove that link and use one of the methods above.

Then ask your agent for a questionnaire, a survey or a decision round for your team.

## How it works

Commands below run from `skills/interactive-questionnaire/`.

1. Claude writes the questions into a JSON config ([references/config.md](skills/interactive-questionnaire/references/config.md)). The [examples](skills/interactive-questionnaire/examples/) are complete models.
2. `scripts/build.py` checks the config and fills [assets/template.html](skills/interactive-questionnaire/assets/template.html):

   ```bash
   python3 -I scripts/build.py examples/team-agreements.json /tmp/team.html --preview
   ```

3. Claude publishes the page as a private Artifact, with a shared store where each person writes only their own answers. You share it from claude.ai. Who can save depends on the share level: the owner and Editors always, Contributors on Team and Enterprise plans. Everyone else sends their answers as a message.
4. Claude reads the answers with ArtifactData and turns them into a report with `scripts/summarize.py`. Messages pasted into the chat are decoded with `scripts/import_answers.py`.
5. The config travels inside the published page, so `scripts/extract_config.py` can get it back in a later session, to change the questions and republish without losing answers.

[SKILL.md](skills/interactive-questionnaire/SKILL.md) is the full workflow Claude follows.

## Without claude.ai: one file to share

From `skills/interactive-questionnaire/`:

```bash
python3 -I scripts/build.py examples/team-agreements.json team.html --standalone
```

`team.html` opens in any browser, with no account and no server. Each person answers, then «Save a copy with the answers» downloads the file again with their answers and everyone's before them, to send to the next person or back to whoever collects. The collector adds the copies (or one-line codes) people send back in «Add other people's answers». `scripts/import_answers.py` and `scripts/summarize.py` read the answers straight out of a returned copy.

## What it runs

- **The scripts** are standard-library Python, with no dependencies, no network calls and no environment variables. They read and write only the files you name: the config, the page, its preview, the imported answers and the report. When Node.js is installed, `build.py` runs `node --check` on a temporary copy of the page's script and deletes it.
- **The preview:** the agent serves the questionnaire folder on `127.0.0.1:8769` with `python3 -m http.server`, opens it, then stops the server and deletes the preview.
- **The claude.ai page** saves each person's picks, notes and times in the Artifact's own store, under their claude.ai account. Everyone who can open the page sees them.
- **The page** loads its font from Google Fonts (fonts.googleapis.com and fonts.gstatic.com) and, on claude.ai, shows people's profile pictures. It sends answers nowhere else. Your browser keeps your own answers, language, name and a random browser id in `localStorage`. «Copy all answers» writes to the clipboard, and the file version's «Save a copy» puts everyone's answers in the downloaded file.

## Privacy

Everyone who can open a questionnaire page sees the whole page and every answer, with names. Don't put secrets or personal data in the questions.

## Versions

See [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE)
