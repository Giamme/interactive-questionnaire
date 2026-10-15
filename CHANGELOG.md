# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and versions follow the format `{major}.{minor}` ([...] parts appear only when non-zero).

## [0.1] - 2026-10-15

First public release: a skill that turns your questions into a claude.ai page a team fills in one after another, keeping every answer for Claude to read back.

### Highlights

- Build a shareable questionnaire page on claude.ai from a JSON config: each person's answers are saved under their name, everyone sees the team's answers, and Claude reads them back into a report.

### Added

- Three kinds of question: decisions with a recommended answer (yes, a different answer, not sure), multiple choice with your own options, and open questions with a written answer.
- Pages in one or more languages, with a switch at the top. Italian and English are built in, and any other language can bring its own wording.
- Answering closes the question and scrolls to the next unanswered one. Floating buttons go to the top, the next unanswered question and the last one, and a sidebar lists every question with a tick for your answers (a drawer on phones).
- Scripts: `build.py` checks a config and explains every error before building the page, `extract_config.py` gets the config back out of a published page, and `summarize.py` turns the saved answers into a Markdown report.
