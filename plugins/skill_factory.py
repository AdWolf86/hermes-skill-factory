"""
Hermes Skill Factory Plugin — converts Claude Code / Anthropic skills to Hermes format.

Registers a `skill_factory` tool and a `convert_skill` function callable from
other tools or the convert_skills.py CLI script.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Optional

import yaml

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
SKILLS_DIR = HERMES_HOME / "skills"

# ── Frontmatter conversion ──────────────────────────────────────────────────


def convert_frontmatter(claude_fm: dict, category: str = "cybersecurity") -> dict:
    """Convert Claude Code skill frontmatter to Hermes format."""
    hermes_fm: dict = {
        "name": claude_fm.get("name", "unknown-skill"),
        "description": _trim_description(claude_fm.get("description", "")),
        "version": claude_fm.get("version", "1.0.0"),
        "author": claude_fm.get("author", "unknown"),
        "license": claude_fm.get("license", "MIT"),
        "platforms": ["linux", "macos", "windows"],
        "metadata": {
            "hermes": {
                "tags": [],
                "category": category,
            }
        },
    }

    # Merge tags from Claude Code format
    cc_tags = claude_fm.get("tags", [])
    if isinstance(cc_tags, str):
        cc_tags = [t.strip() for t in cc_tags.split(",")]

    hermes_tags = cc_tags.copy()
    subdomain = claude_fm.get("subdomain", "")
    if subdomain and subdomain not in hermes_tags:
        hermes_tags.insert(0, subdomain)

    hermes_fm["metadata"]["hermes"]["tags"] = hermes_tags

    # Preserve cybersecurity metadata
    nist = claude_fm.get("nist_csf", [])
    if nist:
        hermes_fm["metadata"]["nist_csf"] = nist

    mitre = claude_fm.get("mitre_attack", [])
    if mitre:
        hermes_fm["metadata"]["mitre_attack"] = mitre

    # Preserve original domain info
    domain = claude_fm.get("domain", "")
    if domain:
        hermes_fm["metadata"]["domain"] = domain

    return hermes_fm


def _trim_description(desc: str, max_len: int = 300) -> str:
    """Trim and clean description to reasonable length."""
    # Remove leading/trailing whitespace and quotes
    desc = desc.strip().strip("'\"")
    # Normalize whitespace
    desc = re.sub(r"\s+", " ", desc)
    if len(desc) > max_len:
        desc = desc[: max_len - 3] + "..."
    return desc


# ── Body conversion ─────────────────────────────────────────────────────────


def convert_body(markdown_body: str) -> str:
    """Adapt Claude Code skill body to Hermes conventions."""
    # Rename ## Workflow → ## Steps
    body = re.sub(r"^##\s*Workflow", "## Steps", markdown_body, flags=re.MULTILINE)

    # Rename ## Key Concepts → ## Reference
    body = re.sub(
        r"^##\s*Key Concepts", "## Reference", body, flags=re.MULTILINE
    )

    # Rename ## Common Scenarios → ## Examples
    body = re.sub(
        r"^##\s*Common Scenarios", "## Examples", body, flags=re.MULTILINE
    )

    # Rename ## Output Format → ## Output
    body = re.sub(
        r"^##\s*Output Format", "## Output", body, flags=re.MULTILINE
    )

    # Rename ## Tools & Systems → ## Tools
    body = re.sub(
        r"^##\s*Tools & Systems", "## Tools", body, flags=re.MULTILINE
    )

    # Add Pitfalls section if not present
    if "## Pitfalls" not in body and "## Verification" not in body:
        pitfalls = (
            "\n\n## Pitfalls\n\n"
            "- This skill was auto-converted from Claude Code format. "
            "Review and adapt commands for your environment.\n"
            "- Some tool paths or package names may differ on your system.\n"
            "- Test in a safe environment before running against production.\n"
        )
        body += pitfalls

    # Add Verification section if not present
    if "## Verification" not in body:
        verify = (
            "\n\n## Verification\n\n"
            "After completing the steps:\n"
            "- [ ] Expected output produced\n"
            "- [ ] No errors in logs\n"
            "- [ ] Results saved/exported as specified\n"
        )
        body += verify

    return body


# ── Full conversion ─────────────────────────────────────────────────────────


def convert_skill(skill_path: Path, category: str = "cybersecurity", force: bool = False) -> Optional[Path]:
    """Convert a single Claude Code skill directory to a Hermes skill directory.

    Args:
        skill_path: Path to the Claude Code skill directory containing SKILL.md
        category: Hermes category folder (e.g. 'cybersecurity', 'devops')
        force: Overwrite existing skill

    Returns:
        Path to the installed Hermes skill directory, or None if skipped/error
    """
    source_md = skill_path / "SKILL.md"
    if not source_md.exists():
        print(f"  SKIP {skill_path.name}: no SKILL.md found")
        return None

    # Parse Claude Code SKILL.md
    content = source_md.read_text(encoding="utf-8")
    fm, body = _split_frontmatter(content)

    if fm is None:
        print(f"  SKIP {skill_path.name}: no valid YAML frontmatter")
        return None

    skill_name = fm.get("name", skill_path.name)
    hermes_fm = convert_frontmatter(fm, category)
    hermes_body = convert_body(body)

    # Build destination
    dest_dir = SKILLS_DIR / category / skill_name
    if dest_dir.exists() and not force:
        print(f"  SKIP {skill_name}: already exists (use --force to overwrite)")
        return None

    dest_dir.mkdir(parents=True, exist_ok=True)

    # Write Hermes SKILL.md
    hermes_content = yaml.dump(hermes_fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
    hermes_content = f"---\n{hermes_content}---\n\n{hermes_body}"

    (dest_dir / "SKILL.md").write_text(hermes_content, encoding="utf-8")

    # Copy references and scripts if present
    for sub in ["references", "scripts", "templates", "assets"]:
        src_sub = skill_path / sub
        if src_sub.is_dir():
            dest_sub = dest_dir / sub
            if dest_sub.exists():
                shutil.rmtree(dest_sub)
            shutil.copytree(src_sub, dest_sub)

    return dest_dir


def _split_frontmatter(content: str) -> tuple[Optional[dict], str]:
    """Split YAML frontmatter from markdown body."""
    if not content.startswith("---"):
        return None, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content

    try:
        fm = yaml.safe_load(parts[1])
        body = parts[2].strip()
        return fm, body
    except yaml.YAMLError:
        return None, content


# ── Batch conversion ────────────────────────────────────────────────────────


def convert_all(skills_root: Path, category: str = "cybersecurity", force: bool = False, dry_run: bool = False) -> dict:
    """Convert all Claude Code skills in a directory tree.

    Returns dict with counts: {converted, skipped, errors}
    """
    stats = {"converted": 0, "skipped": 0, "errors": 0}

    # Find all skill directories (those containing SKILL.md)
    skill_dirs = sorted([p.parent for p in skills_root.rglob("SKILL.md")])

    if not skill_dirs:
        print(f"No SKILL.md files found under {skills_root}")
        return stats

    print(f"Found {len(skill_dirs)} skills to convert")
    if dry_run:
        print("DRY RUN — no files will be written\n")

    for skill_path in skill_dirs:
        skill_name = skill_path.name
        if dry_run:
            print(f"  WOULD CONVERT: {skill_path} → {SKILLS_DIR / category / skill_name}")
            stats["converted"] += 1
        else:
            result = convert_skill(skill_path, category, force)
            if result:
                print(f"  ✓ {skill_name}")
                stats["converted"] += 1
            else:
                stats["skipped"] += 1

    if not dry_run:
        print(f"\nConverted: {stats['converted']}, Skipped: {stats['skipped']}, Errors: {stats['errors']}")
        print(f"Skills installed to: {SKILLS_DIR / category}/")
        print("Run 'hermes skills reload' to activate.")

    return stats
