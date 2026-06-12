#!/usr/bin/env python3
"""
Hermes Skill Factory — CLI batch converter.

Converts Claude Code / Anthropic format skill repositories to Hermes format.

Usage:
    python3 convert_skills.py /path/to/claude-skills/ [--category NAME] [--force] [--dry-run] [--validate]

Examples:
    # Convert all skills from a cloned repo
    python3 convert_skills.py /tmp/Anthropic-Cybersecurity-Skills/skills/

    # Dry run to preview
    python3 convert_skills.py /tmp/Anthropic-Cybersecurity-Skills/skills/ --dry-run

    # Validate only (check which skills can be converted)
    python3 convert_skills.py /tmp/Anthropic-Cybersecurity-Skills/skills/ --validate
"""

import argparse
import sys
from pathlib import Path

# Add Hermes plugins to path
HERMES_HOME = Path.home() / ".hermes"
sys.path.insert(0, str(HERMES_HOME / "plugins"))

try:
    from skill_factory import convert_all  # type: ignore
except ImportError:
    # Use local copy during development
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "plugins"))
    from skill_factory import convert_all  # type: ignore


def main():
    parser = argparse.ArgumentParser(
        description="Convert Claude Code / Anthropic skills to Hermes Agent format"
    )
    parser.add_argument(
        "skills_dir",
        help="Path to directory containing Claude Code skill directories (each with SKILL.md)",
    )
    parser.add_argument(
        "--category",
        default="cybersecurity",
        help="Category folder name under ~/.hermes/skills/ (default: cybersecurity)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing skills instead of skipping",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview conversions without writing files",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate skills without converting (checks frontmatter)",
    )

    args = parser.parse_args()
    skills_root = Path(args.skills_dir).resolve()

    if not skills_root.exists():
        print(f"Error: directory not found: {skills_root}")
        sys.exit(1)

    if args.validate:
        _validate(skills_root)
    else:
        stats = convert_all(skills_root, args.category, args.force, args.dry_run)
        if stats["errors"] > 0:
            sys.exit(1)


def _validate(skills_root: Path):
    """Validate Claude Code skills without converting."""
    import yaml

    ok = 0
    fail = 0
    for md_path in sorted(skills_root.rglob("SKILL.md")):
        content = md_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            print(f"  FAIL {md_path.parent.name}: no frontmatter")
            fail += 1
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            print(f"  FAIL {md_path.parent.name}: malformed frontmatter")
            fail += 1
            continue
        try:
            fm = yaml.safe_load(parts[1])
            name = fm.get("name", "?")
            desc = (fm.get("description", "") or "")[:80]
            domain = fm.get("domain", "?")
            print(f"  OK   {name:50s} [{domain}] {desc}")
            ok += 1
        except yaml.YAMLError as e:
            print(f"  FAIL {md_path.parent.name}: YAML error: {e}")
            fail += 1

    print(f"\nValid: {ok}, Invalid: {fail}")


if __name__ == "__main__":
    main()
