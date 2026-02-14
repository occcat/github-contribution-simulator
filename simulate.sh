#!/bin/bash
#
# GitHub Contribution Simulator - Quick Start Script
#
# Usage: ./simulate.sh [start_year] [intensity]
# Example: ./simulate.sh 2022 medium

set -e

# Default values
START_YEAR="${1:-2020}"
INTENSITY="${2:-medium}"
REPO_DIR="./simulated-repo"

# Validate intensity
if [[ ! "$INTENSITY" =~ ^(light|medium|heavy)$ ]]; then
    echo "❌ Error: Intensity must be 'light', 'medium', or 'heavy'"
    exit 1
fi

echo "🌱 GitHub Contribution Simulator"
echo "================================="
echo ""
echo "Configuration:"
echo "  Start Year: $START_YEAR"
echo "  Intensity: $INTENSITY"
echo "  Repository: $REPO_DIR"
echo ""

# Step 1: Preview
echo "📊 Step 1: Previewing contribution pattern..."
python3 simulator.py --start "${START_YEAR}-01-01" --intensity "$INTENSITY" --stats-only
echo ""

# Step 2: Confirm
read -p "⚡ Create commits? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "👋 Cancelled."
    exit 0
fi

# Step 3: Generate commits
echo ""
echo "🔨 Step 2: Generating commits..."
python3 generate_commits.py --start "${START_YEAR}-01-01" --intensity "$INTENSITY" --repo "$REPO_DIR"

echo ""
echo "✅ Complete!"
echo ""
echo "Next steps:"
echo "  1. cd $REPO_DIR"
echo "  2. git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo "  3. git push -u origin main"
