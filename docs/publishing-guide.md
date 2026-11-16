# Publishing This Project on GitHub

[← Back to README](../README.md)

This guide publishes the repository as **`ghana-business-opportunity-analysis`** under your GitHub account and sets it up to make a strong portfolio impression.

## Option A — GitHub CLI (fastest)

Prerequisites: [Git](https://git-scm.com/downloads) and the [GitHub CLI](https://cli.github.com/), logged in to the account that should own the repository.

```bash
gh auth status
```

If the wrong account is active, switch accounts:

```bash
gh auth switch
```

From the repository folder:

```bash
git init -b main
git add .
git commit -m "Ghana Business Opportunity Analysis 2026: research, financial model and recommendation"
gh repo create ghana-business-opportunity-analysis --public --source . --remote origin --push --description "Evidence-based investment feasibility case study: small-business opportunities in Ghana for US$5k-20k, with a reproducible Python financial model"
```

## Option B — GitHub website (no command line)

1. Go to <https://github.com/new>. Name the repository `ghana-business-opportunity-analysis`, choose **Public**, and **do not** add a README, licence or .gitignore (they already exist here).
2. On the new repository page, choose **"uploading an existing file"**, drag in the whole folder contents (keep the folder structure), and commit.

## Make it portfolio-ready

1. **About panel** (gear icon on the repository page):
   - Description: *Evidence-based investment feasibility case study of small-business opportunities in Ghana (US$5k–20k), with a reproducible Python financial model.*
   - Topics: `business-analysis`, `market-research`, `financial-modeling`, `feasibility-study`, `ghana`, `africa`, `investment-analysis`, `python`, `pandas`, `matplotlib`, `case-study`
2. **Pin the repository** on your profile: Profile → *Customize your pins*.
3. **Add a social preview image** (Settings → General → Social preview). The ranking chart `visuals/financial-charts/03_weighted_ranking.png` works well.
4. **Link it from your profile README** (the `<username>/<username>` repository), for example:

   ```markdown
   ### Featured case study
   **[Ghana Business Opportunity Analysis 2026](https://github.com/<username>/ghana-business-opportunity-analysis)**: market research, financial modelling and investment recommendation for small businesses in Ghana (US$5k–20k).
   ```

5. **Optional — GitHub Pages:** Settings → Pages → *Deploy from a branch* → `main` / root. GitHub renders the Markdown as a simple website.

## Updating the analysis later

1. Edit an assumption in `data/datasets/inputs/*.csv`.
2. Run `python models/run_all.py`. Model outputs, charts and every table in the documents refresh.
3. Review the prose for any statement that depends on the changed number, then commit:

```bash
git add .
git commit -m "Update assumptions: <what changed>"
git push
```

## Before you publish — checklist

- [ ] Replace the copyright holder in `LICENSE` with your name if you wish.
- [ ] Review the disclaimer in the README.
- [ ] Re-run `python models/run_all.py` once on your machine to confirm reproducibility.
- [ ] Check the repository renders correctly on GitHub: charts load, the `<details>` sections expand, and links work.
