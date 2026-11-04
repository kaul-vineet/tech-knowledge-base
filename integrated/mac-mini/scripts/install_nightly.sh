#!/usr/bin/env bash
# Install / uninstall the nightly LaunchAgent (user domain gui/<uid>, no sudo).
#   install_nightly.sh install      render the plist, plutil -lint it, launchctl bootstrap it
#   install_nightly.sh run-now      launchctl kickstart (one run now, to test)
#   install_nightly.sh status       launchctl print gui/<uid>/local.kb.nightly
#   install_nightly.sh uninstall    launchctl bootout + delete the plist
#   install_nightly.sh --here OUT   render the plist to OUT only (sandbox mode: no launchctl, no ~/Library)
set -eu
LABEL=local.kb.nightly
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KB_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
TEMPLATE="$SCRIPT_DIR/../launchd/$LABEL.plist.template"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"
# launchd starts jobs with a minimal PATH: give it the python3 you use interactively (venv or Homebrew) first.
JOB_PATH="$(dirname "$(command -v python3)"):/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

render() {  # render <out>
  sed -e "s|__KB_ROOT__|$KB_ROOT|g" -e "s|__HOME__|$HOME|g" -e "s|__PATH__|$JOB_PATH|g" "$TEMPLATE" > "$1"
}

case "${1:-}" in
  --here) render "${2:?usage: install_nightly.sh --here OUT}"; echo "rendered $2 (not installed)" ;;
  install)
    mkdir -p "$HOME/Library/LaunchAgents" "$HOME/kb-runs"
    render "$PLIST"
    plutil -lint "$PLIST"
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true   # reinstall = bootout, then bootstrap
    launchctl bootstrap "$DOMAIN" "$PLIST"
    echo "installed $PLIST; next run 02:30 local time (missed while asleep -> runs at wake)" ;;
  run-now) launchctl kickstart -p "$DOMAIN/$LABEL" ;;
  status) launchctl print "$DOMAIN/$LABEL" ;;
  uninstall)
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    rm -f "$PLIST"
    echo "removed $LABEL (run files in ~/kb-runs are kept)" ;;
  *) sed -n '2,8p' "$0"; exit 2 ;;
esac
