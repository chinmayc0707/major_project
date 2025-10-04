# Major Project

This repository contains the "Major Project" application.

Contents:
- Python scripts (app.py, assemblyai.py, etc.)
- static/ and templates/ for the web frontend
- uploads/ and sample media (ignored by .gitignore)

How to push to GitHub:
1. Create a new repository on GitHub (https://github.com/new) named `major-project` (or another name).
2. In PowerShell in this folder:
   git remote add origin https://github.com/<YOUR_USERNAME>/major-project.git
   git push -u origin main

Or use the GitHub API with a personal access token (instructions provided in the repo)."

Automatic repo creation and push
--------------------------------

There is a helper PowerShell script `create_and_push.ps1` which will create a repository under your GitHub account (using a personal access token) and push the current `main` branch.

Usage (PowerShell):

1. Create a personal access token on GitHub with the `repo` scope. Save it somewhere safe.
2. In PowerShell set the token for the session:

   $env:GITHUB_TOKEN = "ghp_xxxYourTokenHerexxx"

3. Run the script (optionally change the repo name and visibility):

   .\create_and_push.ps1 -RepoName "major-project" -Visibility "public"

The script will create the repo, set `origin`, and push `main`.

Security note: do not commit tokens to source control. Prefer setting the environment variable only in your session.
