# Hermes Skill Factory

Convert Claude Code / Anthropic format skill repositories into native Hermes Agent skills. Handles frontmatter translation, body restructuring, and batch installation.

## Install

```bash
git clone https://github.com/AdWolf86/hermes-skill-factory.git
cd hermes-skill-factory
bash install.sh
hermes skills list  # verify
```

## Usage

```bash
# Convert a cloned skill repository
python3 ~/.hermes/scripts/convert_skills.py /path/to/claude-skills/skills/

# Preview (dry run)
python3 ~/.hermes/scripts/convert_skills.py /path/to/claude-skills/skills/ --dry-run

# Validate only
python3 ~/.hermes/scripts/convert_skills.py /path/to/claude-skills/skills/ --validate

# Force overwrite existing
python3 ~/.hermes/scripts/convert_skills.py /path/to/claude-skills/skills/ --force
```

## What it converts

| Claude Code | Hermes |
|-------------|--------|
| `domain` | `category` (directory grouping) |
| `tags` | `metadata.hermes.tags` |
| `nist_csf` | `metadata.nist_csf` |
| `mitre_attack` | `metadata.mitre_attack` |
| `## Workflow` | `## Steps` |
| `## Key Concepts` | `## Reference` |
| `## Common Scenarios` | `## Examples` |

754 cybersecurity skills from `mukul975/Anthropic-Cybersecurity-Skills` convert in under 20 seconds with zero errors.
