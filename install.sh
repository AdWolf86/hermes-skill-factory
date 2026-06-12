#!/usr/bin/env bash
# Hermes Skill Factory — install script
# Converts Claude Code / Anthropic format skills to Hermes Agent format.
set -e

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SKILL_DIR="$HERMES_HOME/skills/meta/skill-factory"
PLUGIN_DIR="$HERMES_HOME/plugins"

echo "=== Hermes Skill Factory Installer ==="
echo "Hermes home: $HERMES_HOME"
echo ""

# Install the meta-skill
echo "Installing meta-skill..."
mkdir -p "$SKILL_DIR"
cp "$(dirname "$0")/skills/skill-factory/SKILL.md" "$SKILL_DIR/"
echo "  ✓ Meta-skill installed to $SKILL_DIR"

# Install the plugin
echo "Installing plugin..."
mkdir -p "$PLUGIN_DIR"
cp "$(dirname "$0")/plugins/skill_factory.py" "$PLUGIN_DIR/"
echo "  ✓ Plugin installed to $PLUGIN_DIR"

# Install the converter script
echo "Installing converter..."
mkdir -p "$HERMES_HOME/scripts"
cp "$(dirname "$0")/scripts/convert_skills.py" "$HERMES_HOME/scripts/"
chmod +x "$HERMES_HOME/scripts/convert_skills.py"
echo "  ✓ Converter installed to $HERMES_HOME/scripts/"

echo ""
echo "Done! Activate with:"
echo "  hermes skills reload"
echo "  hermes skills enable skill-factory"
echo ""
echo "To convert a Claude Code skill repo:"
echo "  python3 ~/.hermes/scripts/convert_skills.py /path/to/claude-skills/"
