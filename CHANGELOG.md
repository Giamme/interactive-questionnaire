# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and versions follow the format `{major}.{minor}` ([...] parts appear only when non-zero).

## [0.3] - 2026-10-15

The skill can now make a questionnaire as a single HTML file for people who don't use claude.ai: it opens in any browser, travels from person to person with everyone's answers inside, and Claude reads the answers back from a returned copy.

### Highlights

- A file version for people who don't use claude.ai: `build.py --standalone` writes one HTML file that opens in any browser with no account or server. Each person answers, then «Save a copy with the answers» downloads the file with their answers and everyone's before them, to pass on; whoever collects adds the copies or codes that come back, and `import_answers.py` reads answers straight out of a returned copy. Where a viewer doesn't run the page (a file preview or an attachment preview), the file shows its title and asks to be opened in a browser instead of an empty frame.

## [0.2] - 2026-10-15

Everyone who opens a shared questionnaire now sees the team's answers, and people the page can't save for, including visitors without a Claude account, send theirs as one compressed line that chats can't break.

### Highlights

- Anyone the page can't save for, including visitors without a Claude account, can send their answers with «Send your answers», which makes a one-line code to paste into a message; the owner pastes it into «Add answers from a code» and the answers join the team's under the sender's name. The code is letters and digits only, with a checksum, so it survives the formatting chat apps and mail clients apply, and a damaged code is refused rather than read wrong.
- «Copy all answers» now copies everyone's answers, with names, as one compressed line of letters and digits instead of readable text, so chats and email can't reformat it; the owner can paste it back into the page, which adds anyone missing and leaves the rest as they are, or paste it to Claude.
- People who open a shared questionnaire without an identity on the page, such as teammates outside your organization, now see the team's answers instead of an empty page.

### Added

- A config's `legacyLocalKey` brings in answers an earlier version of the page kept in someone's browser, and people who can now save carry those answers into the page.
- `scripts/import_answers.py` decodes answer codes, from one person or from «Copy all answers», into documents for the report or for an ArtifactData batch, and `summarize.py` names their senders and takes more than one `--docs` folder.

### Changed

- The skill's sharing advice now says who can save at each share level: on a personal plan, invite teammates by email as Editors with no public link, or keep the link and collect answers by message.

## [0.1] - 2026-10-15

First public release: a skill that turns your questions into a claude.ai page a team fills in one after another, keeping every answer for Claude to read back.

### Highlights

- Build a shareable questionnaire page on claude.ai from a JSON config: each person's answers are saved under their name, everyone sees the team's answers, and Claude reads them back into a report.

### Added

- Three kinds of question: decisions with a recommended answer (yes, a different answer, not sure), multiple choice with your own options, and open questions with a written answer.
- Pages in one or more languages, with a switch at the top. Italian and English are built in, and any other language can bring its own wording.
- Answering closes the question and scrolls to the next unanswered one. Floating buttons go to the top, the next unanswered question and the last one, and a sidebar lists every question with a tick for your answers (a drawer on phones).
- Scripts: `build.py` checks a config and explains every error before building the page, `extract_config.py` gets the config back out of a published page, and `summarize.py` turns the saved answers into a Markdown report.
