# Installing PaperDojo for Codex

Enable PaperDojo skills in Codex via native skill discovery. Just clone and symlink.

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/HsiaHongKuan/paperdojo.git ~/.codex/paperdojo
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/paperdojo/skills/paperdojo ~/.agents/skills/paperdojo
   ```

3. **Restart Codex** (quit and relaunch the CLI) to discover the skills.

## Verify

```bash
ls -la ~/.agents/skills/paperdojo
```

You should see a symlink pointing to the paperdojo skills directory.

## Updating

```bash
cd ~/.codex/paperdojo && git pull
```

Skills update instantly through the symlink.

## Uninstalling

```bash
rm ~/.agents/skills/paperdojo
```

Optionally delete the clone: `rm -rf ~/.codex/paperdojo`.
