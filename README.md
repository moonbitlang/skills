# Agent Skills

Agent Skills are folders of instructions, scripts, and resources that AI agents can discover and use to perform at specific tasks. Write once, use everywhere.

## Installing

### Git clone

Clone the repository with submodules so every bundled skill is available locally:

```sh
git clone --recurse-submodules https://github.com/moonbitlang/skills.git
cd skills
```

If you already cloned the repository without submodules, initialize them afterward:

```sh
git submodule update --init --recursive
```

Each skill lives in its own directory under `skills/`.

### General agents

For agents that can install skills from natural language prompts, such as Codex, Claude, Gemini CLI, OpenCode, and similar tools, ask the agent to install the skills listed in this repository:

```text
install the skills listed in this repo: https://raw.githubusercontent.com/moonbitlang/skills/refs/heads/master/.claude-plugin/marketplace.json
```

### Claude Code

Run `/plugin` in the CLI, and select `Add Marketplace`. Input `moonbitlang/skills` to add this marketplace.

Then install the `moonbit-skills` plugin from the marketplace. The plugin exposes the bundled skills from the `skills/` directory.

### Codex

Run in the CLI: `$skill-installer install <skill-name> by submodule from https://github.com/moonbitlang/skills.git`

Or, run `$skill-installer install all skills listed in https://raw.githubusercontent.com/moonbitlang/skills/refs/heads/master/.claude-plugin/marketplace.json` to install all skills in this repo.

## License

The license of an individual skill can be found directly inside the skill's directory inside the LICENSE.txt file.
