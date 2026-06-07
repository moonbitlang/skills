# Agent Skills

Agent Skills are folders of instructions, scripts, and resources that AI agents can discover and use to perform at specific tasks. Write once, use everywhere.

## Installing

Install all skills to the portable universal skills directory:

```sh
npx skills@latest add moonbitlang/skills -g --agent universal --skill "*" --copy -y
```

This installs one copy under `~/.agents/skills/`.

Install all skills for Codex with the `skills` CLI:

```sh
npx skills@latest add moonbitlang/skills -g --agent codex --skill "*" --copy -y
```

Install all skills for Claude Code:

```sh
npx skills@latest add moonbitlang/skills -g --agent claude-code --skill "*" --copy -y
```

List the skills available in this repository:

```sh
npx skills@latest add moonbitlang/skills --list
```

Install one skill by name:

```sh
npx skills@latest add moonbitlang/skills -g --agent codex --skill moonbit-orientation --copy -y
```

Each skill lives in its own directory under `skills/`.

### Local copy

If you do not want to use `npx`, clone the repository and copy the skill directories manually:

```sh
git clone https://github.com/moonbitlang/skills.git
cd skills
mkdir -p ~/.agents/skills

for skill in skills/*; do
  [ -f "$skill/SKILL.md" ] || continue
  rsync -a --delete "$skill/" "$HOME/.agents/skills/$(basename "$skill")/"
done
```

## Maintaining vendored skills

Installable skills are committed as regular directories under `skills/`. Do not
use submodules or symlinks for installable skill entries; `npx skills` expects
to find real `skills/<name>/SKILL.md` files after a normal clone.

Some skills are vendored from upstream repositories. Their sources are listed in
`skills.sources.json`. To refresh them:

```sh
./scripts/sync-upstream-skills.py
npx skills@latest add . --list
git diff
```

The same sync path also runs weekly in GitHub Actions and opens a pull request
when upstream skill contents change.

## License

The license of an individual skill can be found directly inside the skill's directory inside the LICENSE.txt file.
