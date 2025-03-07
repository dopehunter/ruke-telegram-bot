#!/bin/bash
# This script prepares the Death Note mini-app for GitHub Pages deployment

# Create a docs folder for GitHub Pages (or use any other folder you've configured)
mkdir -p docs

# Copy public files to docs
cp -r public/* docs/

# Create .nojekyll file to bypass Jekyll processing
touch docs/.nojekyll

# Copy source files to docs
cp -r src docs/

# Fix paths in index.html (already done in the file)
cp public/index.html docs/

echo "Files prepared for GitHub Pages in 'docs' folder."
echo "You can now commit and push to your GitHub repository."
echo "Make sure to set GitHub Pages to use the 'docs' folder in your repository settings." 