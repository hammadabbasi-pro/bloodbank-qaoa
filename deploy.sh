#!/usr/bin/env bash
# Usage: bash deploy.sh https://github.com/<user>/<repo>.git
set -e
[ -z "$1" ] && { echo "Usage: bash deploy.sh <github-repo-url>"; exit 1; }
git init
git add .
git commit -m "Blood bank allocation with QAOA - hackathon submission"
git branch -M main
git remote add origin "$1" 2>/dev/null || git remote set-url origin "$1"
git push -u origin main
echo "Pushed. Open the repo in an incognito window to confirm it is public."
