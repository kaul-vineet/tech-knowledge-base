# Self-hosted GitHub Actions runner on the Mac mini

`.github/workflows/mac-mini.yml` runs every project on the Mac mini: scorecard, failure lab, tests, `checks_NN.py`,
the project's `mac_mini/tests`, `checks_NN_mac.py`, and `mac_mini/ci.sh` (Mac experiments that need no model server),
nightly and on demand. It complements `integrated.yml`, which runs on GitHub's hosted `macos-latest` — same OS family,
but not your RAM, your installed simulators or your Ollama models.

## Security first
GitHub's own warning: use self-hosted runners **only with private repositories**, because forks of a public repository
can run code on your machine by opening a pull request. So:
- private repository only; the workflow has no `pull_request` trigger (only `workflow_dispatch` and `schedule`);
- the job runs only if the repository variable `MAC_MINI_RUNNER` is `true` (Settings → Secrets and variables →
  Actions → Variables), so nothing queues for a runner that does not exist (a queued job fails after 24 hours);
- run the runner as your normal user (not root), on a Mac with FileVault on; it needs only outbound HTTPS (443).

## Register the runner
GitHub → repository → Settings → Actions → Runners → **New self-hosted runner** → macOS, ARM64. The page shows the
exact download and `config.sh` commands with a token that expires after one hour; run them in a new folder:
```zsh
mkdir ~/actions-runner && cd ~/actions-runner
# paste the download + tar commands shown on the page, then:
./config.sh --url https://github.com/<you>/<repo> --token <token-from-the-page>
./run.sh                     # "Connected to GitHub ... Listening for Jobs" -> Ctrl-C once it works
```
The runner gets the default labels `self-hosted`, `macOS`, `ARM64` automatically; the workflow asks for exactly
`runs-on: [self-hosted, macOS, ARM64]`.

## Run it as a service (starts at boot/login)
```zsh
cd ~/actions-runner
./svc.sh install            # GitHub docs: sudo ./svc.sh install on Linux; on macOS the service is a launchd agent
./svc.sh start
./svc.sh status
# remove: ./svc.sh stop && ./svc.sh uninstall && ./config.sh remove --token <removal token>
```
Then set `MAC_MINI_RUNNER=true` and start the workflow once by hand (Actions → "mac mini (self-hosted)" → Run workflow).
Add `MAC_MINI_OLLAMA=true` only after `ollama ps` works on the Mac: then `mac_mini/ci_ollama.sh` runs too.

## Keep it healthy
- The runner updates itself; if you disable updates (`--disableupdate`) GitHub stops queueing jobs 30 days after a
  new runner version.
- The checkout lives in `~/actions-runner/_work/`; the workflow uploads `kb-runs-ci/` (JSONL) as artifacts.
- One Mac: the matrix runs one project at a time (`max-parallel: 1`) and `concurrency` stops overlapping runs; the
  nightly launchd job (README) and the runner may still overlap — schedule them hours apart (02:30 local vs the
  21:30 UTC cron) or use only one of them.

**What you should see:** a `profile` job with this Mac's RAM and model class, then 8 green project jobs. A red
"failure lab" step means a seeded fault did **not** fail the scorecard — a seam test lost its teeth on macOS.
Sources: `../research/mac-mini-evidence.md` (GitHub Docs: adding runners, labels, service, runner reference).
