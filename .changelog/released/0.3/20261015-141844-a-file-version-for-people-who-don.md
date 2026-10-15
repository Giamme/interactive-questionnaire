---
type: added
breaking: false
audience: user
highlight: true
commits: 4f8b1c7,531306f
---
A file version for people who don't use claude.ai: `build.py --standalone` writes one HTML file that opens in any browser with no account or server. Each person answers, then «Save a copy with the answers» downloads the file with their answers and everyone's before them, to pass on; whoever collects adds the copies or codes that come back, and `import_answers.py` reads answers straight out of a returned copy. Where a viewer doesn't run the page (a file preview or an attachment preview), the file shows its title and asks to be opened in a browser instead of an empty frame.
