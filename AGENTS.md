# Agent notes

## Architecture diagrams (archify skill)

Architecture diagrams are made with the [archify](https://github.com/tt-a1i/archify)
skill. It is installed per machine, not vendored in this repo:

```bash
npx skills add tt-a1i/archify   # installs to ~/.agents/skills/archify
```

Agents that do not load `~/.agents/skills` automatically (e.g. Claude Code)
should read `~/.agents/skills/archify/SKILL.md` before authoring a diagram.

Conventions for this repo:

- Diagrams live at fixed paths in `docs/diagrams/`: the spec
  `<name>.architecture.json` and its rendered `<name>-architecture.html`.
  Edit the existing spec in place; do not use archify's default timestamped
  `.archify/` folders (they are gitignored).
- Render with `make diagrams` (override `NODE=` / `ARCHIFY=` if `node` or the
  skill live elsewhere).
- When a code change alters what a diagram shows, update its spec in the same
  change and set `meta.repository.revision` to the commit it describes.
