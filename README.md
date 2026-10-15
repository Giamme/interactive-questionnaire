# interactive-questionnaire

A Claude Code skill that turns a set of questions into a **shareable questionnaire page on claude.ai**. Several people fill it in, one after another, and the page keeps every answer. Claude reads the answers back and summarizes them.

The skill is built for decision rounds, where you have a recommendation and want the team to agree or say what instead. It also handles plain multiple choice and open questions.

## What the page does

- **Saves answers per person.** Each answer goes under the person's name in the page's own shared store, and everyone can see the team's answers under each question.
- **Three kinds of question:**
  - `decision`: «Yes, as recommended / A different answer / Not sure»;
  - `choice`: your own options, where any option can ask for an explanation;
  - `open`: a written answer.
- **One or more languages,** with a switch at the top. Italian and English are built in, and another language needs its own UI strings.
- **One question at a time:** answering closes the card into a one-line summary and scrolls to the next unanswered question.
- **Ways around the page:**
  - floating buttons for the top, the next unanswered question and the last question;
  - a sidebar with a tick for each of your answers, which becomes a drawer on phones;
  - filters for «not answered by me» and «not answered by anyone».
- **Answers by message for anyone it can't save for:** view-only readers, people claude.ai doesn't identify on the page, and visitors without a Claude account. «Send your answers» makes a message with a code; the owner pastes it into the page, and the answers join the team's under the sender's name.
- **Copy as text:** «Copy all answers» gives everyone's answers as plain text.
- **Light and dark themes,** keyboard friendly, and it respects reduced motion.

## Requirements

- Claude Code signed in to a claude.ai account that can publish Artifacts (the `Artifact` and `ArtifactData` tools).
- Python 3.10 or newer for the scripts.
- Node.js is optional; `build.py` uses it to check that the page's script parses.

## Install

```bash
git clone https://github.com/Giamme/interactive-questionnaire.git ~/dev/interactive-questionnaire
```

```bash
ln -s ~/dev/interactive-questionnaire ~/.claude/skills/interactive-questionnaire
```

Then ask Claude Code for a questionnaire, a survey or a decision round for your team, or run `/interactive-questionnaire`.

## How it works

1. Claude writes the questions into a JSON config ([references/config.md](references/config.md)). The [examples](examples/) are complete models.
2. `scripts/build.py` checks the config and fills [assets/template.html](assets/template.html):

   ```bash
   python3 -I scripts/build.py examples/team-agreements.json /tmp/team.html --preview
   ```

3. Claude publishes the page as a private Artifact, with a shared store where each person writes only their own answers. You share it from claude.ai. Who can save depends on the share level: the owner and Editors always, Contributors on Team and Enterprise plans. Everyone else sends their answers as a message.
4. Claude reads the answers with ArtifactData and turns them into a report with `scripts/summarize.py`. Messages pasted into the chat are decoded with `scripts/import_answers.py`.
5. The config travels inside the published page, so `scripts/extract_config.py` can get it back in a later session, to change the questions and republish without losing answers.

[SKILL.md](SKILL.md) is the full workflow Claude follows.

## Privacy

Everyone who can open a questionnaire page sees the whole page and every answer, with names. Don't put secrets or personal data in the questions. The page doesn't send anything anywhere else.

## Versions

See [CHANGELOG.md](CHANGELOG.md).

## License

[MIT](LICENSE)
