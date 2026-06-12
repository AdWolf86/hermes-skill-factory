---
name: skill-factory
description: "Convert Claude Code / Anthropic format skills to Hermes Agent format. Batch import external skill repositories into Hermes with proper frontmatter, structure, and category organization."
version: 1.0.0
author: AdWolf86
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, conversion, import, claude-code, factory]
    related_skills: [hermes-agent-skill-authoring]
---

# Hermes Skill Factory

Convert external skill repositories (Claude Code, Anthropic format) into native Hermes Agent skills. Handles frontmatter translation, structure adaptation, and batch installation.

## When to Use

- Importing a Claude Code / Anthropic-format skill repository into Hermes
- Batch converting 100s of skills from external sources
- Adding cybersecurity, devops, or other domain-specific skill libraries
- The user says "install these skills" and points to a repo with non-Hermes format

## How It Works

The plugin (`skill_factory.py`) registers a `skill_factory` tool that:
1. Reads Claude Code SKILL.md files
2. Converts frontmatter (domain/subdomain → categories, nist_csf/mitre_attack → metadata)
3. Adapts body structure (Prerequisites → numbered steps, adds Pitfalls/Verification)
4. Installs skills into `~/.hermes/skills/<category>/<name>/`

The standalone `convert_skills.py` script handles batch conversion from the command line.

## Step-by-Step

### 1. Install the factory

```bash
cd hermes-skill-factory
bash install.sh
hermes skills reload
```

### 2. Load the skill in Hermes

```
/skill skill-factory
```

Or preload on startup:
```bash
hermes -s skill-factory
```

### 3. Convert a skill repository

```bash
# Batch convert all skills
python3 ~/.hermes/scripts/convert_skills.py /path/to/claude-skills/

# Convert to a specific category
python3 ~/.hermes/scripts/convert_skills.py /path/to/claude-skills/ --category cybersecurity

# Dry run (preview only)
python3 ~/.hermes/scripts/convert_skills.py /path/to/claude-skills/ --dry-run
```

### 4. Reload Hermes skills

```bash
hermes skills reload
/hermes skills list  # verify they appear
```

## Conversion Rules

| Claude Code Field | Hermes Field |
|-------------------|-------------|
| `domain` | `category` (directory grouping) |
| `subdomain` | `metadata.hermes.tags` |
| `tags` | `metadata.hermes.tags` (merged) |
| `nist_csf` | `metadata.nist_csf` |
| `mitre_attack` | `metadata.mitre_attack` |
| `description` | `description` (trimmed to 300 chars) |
| `## When to Use` | `## When to Use` (kept) |
| `## Prerequisites` | `## Prerequisites` (kept) |
| `## Workflow` | `## Steps` (renamed, auto-numbered) |
| `## Key Concepts` | `## Reference` (renamed) |
| `## Common Scenarios` | `## Examples` (renamed) |

## Pitfalls

- **Frontmatter goes BEFORE the markdown body** — if the source skill has no YAML frontmatter, conversion will fail. Run the validator first.
- **Duplicate skill names** — if a skill with the same name already exists, conversion skips it. Use `--force` to overwrite.
- **Large code blocks** — some Claude Code skills have massive embedded code. These are preserved but may need trimming.
- **Not all sections map perfectly** — Claude Code skills are more verbose. The converter preserves all content but reorganizes for Hermes conventions.

## Verification

After conversion, verify skills are loadable:

```bash
# Check skill count
hermes skills list | wc -l

# Load one to verify
hermes -s analyzing-memory-dumps chat -q "What does this skill cover?"

# Check for conversion errors
python3 ~/.hermes/scripts/convert_skills.py --validate /path/to/skills/
```
