# How to "deploy" (submit) this project

For the hackathon there is no server to deploy. "Deploying" means: put the repo on GitHub, confirm it runs, upload the video, and submit the form.

## 1. Fill placeholders
Search for `[TEAM NAME]`, `[NAMES]`, `[GITHUB URL]` in: README.md, CREDITS.md, docs/video_script.md.
For docs/report.docx: edit the placeholders in Word directly, or edit docs/make_report.js and run `node docs/make_report.js` (needs `npm install docx`).

## 2. Run it once locally
```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python tests/test_consistency.py
python src/main.py
```
Confirm `results/` is filled. Commit it.

## 3. Create the GitHub repo and push
1. On github.com click New repository. Name it e.g. `bloodbank-qaoa`. Set it to **Public**. Do NOT add a README or .gitignore (we already have them).
2. In the project folder:
```bash
git init
git add .
git commit -m "Blood bank allocation with QAOA - hackathon submission"
git branch -M main
git remote add origin https://github.com/<your-username>/bloodbank-qaoa.git
git push -u origin main
```
Shortcut: `bash deploy.sh https://github.com/<your-username>/bloodbank-qaoa.git`

If git asks for a password, use a Personal Access Token (GitHub > Settings > Developer settings) or GitHub Desktop.

## 4. Test like a judge
```bash
git clone https://github.com/<your-username>/bloodbank-qaoa.git test-clone
cd test-clone && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && python src/main.py
```

## 5. Video, report, form
- Record the 3-minute video from docs/video_script.md (must be under 3:00). Upload to Google Drive, Share > General access > **Anyone with the link**. Check in an incognito window.
- Report: docs/report.docx (diagram is already inside). Fill the placeholders.
- Submit the form: https://forms.gle/jSRrXaHkjVb7G7AK8 with the repo link, report and video link.

## 6. Deadline rule
**Do not push any commit after 12 Nov 2026, 11:59pm.** The last commit before the cutoff is judged. Push early, then stop.
