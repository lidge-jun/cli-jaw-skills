# Raw session notes (INPUT for the trial — as an agent actually produced them)

- ran: python3 scripts/validate_public_surface.py on main -> exit 1, "dev/SKILL.md:504"
- ran: ls */SKILL.md | wc -l -> 226
- read: scripts/validate_public_surface.py EXPECTED_SKILLS=226, 500-line cap, 4 Office exemptions
- ran: wc -l search/SKILL.md -> 472
- ran: gh run list -> last CI on main 25e30780 success (2026-09-05)
- grep: README.md line 10 badge "reference_assets-47", line 30 "47 skills include reference/"
- grep: docs/index.html line 137 "Reference folders | 47 skills"
- read: dev/SKILL.md Skill Ownership Map says "MUST NOT duplicate canonical content"
- read: search/SKILL.md declares itself standalone owner of tier policy
- read: deep-research/SKILL.md is vendored Apache-2.0 (author sanjay3290), Gemini agent wrapper
- probe: dev-architecture/references/ holds barrel-discipline.md, circular-dependencies.md, coupling-taxonomy.md only
- probe: registry.json has 230 entries vs 226 skill folders (pre-existing drift)
- decision taken: extract dev 7.2 mapping table to dev/references/static-analysis.md, net -11 lines -> 496
- decision taken: put the deep-research protocol under search/references/, not in SKILL.md (472+140 would breach 500)
- risk: creating search/references/ makes the reference-folder count 48, README+docs say 47
- risk: pytest tests/ needs officecli binary; CI only runs test_dev_frontend_refresh.py
