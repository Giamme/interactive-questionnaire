# Questionnaire config

One JSON file describes a questionnaire. `scripts/build.py` checks it and fills the page template. The config travels inside the built page, so `scripts/extract_config.py` can always get it back from a published page.

Two complete examples are in `examples/`:

- `team-agreements.json`: five questions in Italian and English, mostly `decision` with one `choice` and one `open`.
- `kinds-demo.json`: one question of each kind, in English only.

## Top level

| Field | Required | What it is |
|---|---|---|
| `id` | yes | A slug such as `offsite-2027`. It keys the viewer's browser storage (their language choice, their name and answers kept locally when the page can't save) and it's checked in every answer sent as a message. Keep it the same across republishes. |
| `legacyLocalKey` | no | The full browser storage key under which an earlier version of the page kept answers it couldn't save, such as `old-id:answers`. The page reads it when nothing is kept under the current `id`, and someone who can now save brings those answers into the page. Use it only when the `id` changed. |
| `title` | yes | The page name in the browser tab and the claude.ai gallery: two to four words, a name rather than a sentence («Offsite Planning Round», not «Survey: please answer»). |
| `languages` | yes | Language codes. The first is the default, and the others appear in a switch at the top. With one language there's no switch. The template ships `it` and `en`. |
| `content` | yes | Per language, the questionnaire's own words (see below). A missing language falls back to the first one. |
| `groups` | no | An ordered list of `{key, label}`. With groups, each question names one, and the page and the sidebar show group headings. Keep a group's questions together. |
| `questions` | yes | The questions, in the order people should answer them, most important first. |
| `ui` | no | Per language, overrides for the page's own words. A language other than `it` or `en` must give all of them; `build.py` lists any that are missing. |

## `content.<lang>`

All fields are optional. In any of them, `{n}` is replaced by the number of questions.

| Field | Shown as |
|---|---|
| `heading` | The page's H1. Defaults to `title`. |
| `lede` | One or two sentences under the heading: what this is, and how many questions. |
| `purpose` | «Purpose»: the decision or outcome that depends on the answers. |
| `from` | «From»: who is asking. Use a role or team, never an email address. |
| `to` | «To»: who should answer. |
| `used` | «Your answers»: how the answers are used. The default already says they're saved under each person's name and visible to everyone with the page. Keep that sentence when you replace it. |
| `context` | A «Context» paragraph. This is **HTML**: links are allowed, as `<a href="https://…" target="_blank" rel="noopener">…</a>`. Point to the material the questions are about. Leave it out to hide the section. |
| `how` | One sentence put before the standard «How to answer» text, for example how long it takes. The standard text explains the answer buttons, closing cards, the floating buttons and the sidebar, and adapts to the kinds of question present. |

## Questions

```json
{
  "id": "Q7",
  "group": "plan",
  "kind": "decision",
  "en": {"title": "…", "body": "…", "rec": "…"},
  "it": {"title": "…", "body": "…", "rec": "…"}
}
```

- **`id`**: starts with a letter, then letters, digits, `-` or `_`, unique. Answers are stored under it, so **never rename or reuse an id once people have answered**. To change a question's meaning, give it a new id.
- **`<lang>.title`**: the question in a few words. It's what the sidebar and the copied text show.
- **`<lang>.body`**: the context and one concrete example that makes the question answerable. Line breaks (`\n`) are kept.
- **`<lang>.rec`**: the recommended answer and why, in one to three sentences.

### Kinds

| `kind` | Answer buttons | Done when | Use it for |
|---|---|---|---|
| `decision` (default) | «Yes, as recommended» · «A different answer» · «Not sure» | a pick; «A different answer» also needs its line of text | Decisions where you have a recommendation. `rec` is required. |
| `choice` | the question's own `options`, plus «Not sure» unless `"unsure": false` | a pick; an option with `"needsNote": true` also needs text | A fixed set of alternatives. `rec` is optional. |
| `open` | a text box, plus a «Not sure» toggle | some text, or «Not sure» | Facts or opinions you can't predict. Leave out `rec`. |

A `choice` question's options:

```json
"options": [
  {"key": "turin", "label": {"en": "Turin", "it": "Torino"}},
  {"key": "elsewhere", "label": {"en": "Somewhere else", "it": "Altrove"}, "needsNote": true}
]
```

- **`key`**: letters, digits, `-` and `_`. `yes`, `other`, `unsure` and `answer` are reserved. Answers are stored under the key, so keep keys stable.
- **`label`**: one text per language.
- **`short`** (optional): a shorter label for summaries.

## What is stored

The page keeps one document per person in its `responses` collection. The document id is that person's opaque user id (`u_…`):

```json
{
  "answers": {
    "Q7": {"pick": "yes", "note": "", "at": "2026-10-15T10:00:00.000Z"},
    "Q9": {"pick": "answer", "note": "their written answer", "at": "…"}
  },
  "extra": {"note": "the «Anything else?» box", "at": "…"},
  "updatedAt": "…"
}
```

The values of `pick` depend on the kind:

- `decision`: `yes`, `other` or `unsure`.
- `choice`: an option `key`, or `unsure`.
- `open`: `answer` (the text is in `note`) or `unsure`.

`note` is the comment, or the required text. Nothing in the document depends on the page's language.

### Answers sent as a message

Someone the page can't save for sends a one-line code: `IQ3.` followed by letters and digits only, so a chat app or mail client finds nothing in it to format. A message with a few notes makes a line of a few hundred characters.

- **Inside:** one kind byte (`1` JSON, `2` raw-deflated JSON), the data, and a big-endian CRC32 of both. Every 8 bytes become 11 base62 characters (`0-9A-Za-z`); a shorter last block uses 2, 3, 5, 6, 7, 9 or 10 characters for 1 to 7 bytes.
- **Reading it back** joins the runs of letters and digits after `IQ3` until the CRC32 matches, so line breaks, quote marks, formatting and invisible characters a chat put inside the line are skipped. A code that lost or changed a character, or changed case, is refused as damaged, never read wrong.
- **The JSON is packed tight:** `{"v": 2, "q": "<config id>", "g": "<16 letters and digits>", "n": "Their name", "t": "<time>", "a": {"Q7": ["yes"], "Q9": ["answer", "their text"]}, "x": "the «Anything else?» note"}`. `g` is the sender's browser, so a second code from the same person replaces the first.

Earlier forms are still read: `IQ2` (Crockford base32 in groups between two `IQ2` lines) and `IQ1.z.<base64url>.END`.

When the owner adds it, or Claude does with `scripts/import_answers.py`, it becomes the document `responses/guest-<gid>`, with the same fields as above plus `guestName` (the name they typed) and `importedAt`. Only known question ids, valid picks and notes up to 4,000 characters are kept, and a code for another questionnaire is refused.
