# Installing PaperDojo for OpenCode

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed
- Git installed

## Installation Steps

### 1. Clone PaperDojo

```bash
git clone https://github.com/HsiaHongKuan/paperdojo.git ~/.config/opencode/paperdojo
```

### 2. Symlink Skills

Create a symlink so OpenCode's native skill tool discovers the skills:

```bash
mkdir -p ~/.config/opencode/skills
ln -s ~/.config/opencode/paperdojo/skills/paperdojo ~/.config/opencode/skills/paperdojo
```

### 3. Restart OpenCode

Restart OpenCode. The skills will be available via the native skill tool.

## Usage

### Loading the Skills

Use OpenCode's native `skill` tool to load a skill:

```
use skill tool to load paperdojo
```

### Project Skills

You can also place the skills in `.opencode/skills/` within your project for project-specific use.

## Updating

```bash
cd ~/.config/opencode/paperdojo && git pull
```

## Uninstalling

```bash
rm ~/.config/opencode/skills/paperdojo
```

Optionally delete the clone: `rm -rf ~/.config/opencode/paperdojo`.
