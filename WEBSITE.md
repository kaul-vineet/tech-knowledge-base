# Viewing the knowledge base as a website

The site is one self-contained file, `site/index.html` (about 3 MB: all 7 topics, 154 lessons, no internet needed).

## Open it on your Mac mini or Windows PC
- Double-click `site/index.html`, or open it in any modern browser (Safari, Edge, Chrome, Firefox).
- Progress ("Mark complete"), your chosen topic and the Mac/Windows toggle are saved in the browser (localStorage).

## Rebuild after editing content
```
python tools/build_site.py            # writes site/index.html
```
Mac: `python3 tools/build_site.py` · Windows: `py tools/build_site.py`

## Publish on GitHub Pages (like lpc1768-learning-guide-site)
1. Push this folder as a GitHub repository (see CI.md).
2. Settings → Pages → Source: **GitHub Actions**.
3. The `pages` workflow (`.github/workflows/pages.yml`) rebuilds and deploys on every content change.
   The site appears at `https://<user>.github.io/<repo>/`.

## Practice (grind Q&A)
1,505 multiple-choice questions (160+ per topic, 40+ per level, 5+ per lesson). Open a topic → Practice, or a lesson → Practise this lesson. Sets: all, by level, by lesson, not seen yet, missed last time, hardest. Keys 1–4 answer, Enter = next. Results are saved in the browser; "Retry missed" drills only your misses.
Questions live in `<topic>/content/qbank/L100–L400.json`; validate with `python tools/check_qbank.py <topic>` and `python <topic>/research/qbank_checks.py`.

## Features
Topic switcher · sidebar grouped Getting started / L100 Run it / L200 Build it / L300 Harden it / L400 Design it / Capstone ·
search (Ctrl/⌘ K) · section tabs (Concept, Lab, Code, Failure lab, Design, Build task, Try it, Learning tools, Agent assist,
Checkpoint, Sources) · Mac mini / Windows command toggle · copy buttons · "Complete and continue" with progress bar ·
focus mode · dark mode follows the OS · prints cleanly.
Mermaid diagram sources are shown as code (paste into any Mermaid viewer); everything else renders offline.
