# Golden-Lab-Technologies/.github

Source for the organization profile shown at https://github.com/Golden-Lab-Technologies.

- `profile/README.md`: the profile page. Every claim comes from `golden-lab-site/facts.json` or the live site; check there before adding one.
- `profile/assets/banner.svg`: generated, do not hand-edit. Rebuild with
  `uv run --with fonttools --with uharfbuzz python tools/build_banner.py`.
- `tools/fonts/`: Poppins (SIL Open Font License, see `OFL.txt`), used only to convert banner text to outlines.
