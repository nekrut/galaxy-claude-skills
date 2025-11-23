# Security Best Practices

## Overview

Your Galaxy API key is a sensitive credential that provides full access to your Galaxy account. Treat it like a password and never share it or commit it to version control.

## Quick Setup (Recommended)

Use our setup script to securely store your credentials:

```bash
./setup-credentials.sh
```

This will:
- Prompt for your Galaxy URL and API key
- Store them in `~/.galaxy-credentials` with secure permissions (600)
- Optionally test the connection
- Provide instructions for loading credentials

## Manual Setup

If you prefer to set up credentials manually:

### 1. Create Credentials File

```bash
# Create file with secure permissions
touch ~/.galaxy-credentials
chmod 600 ~/.galaxy-credentials

# Add your credentials
cat >> ~/.galaxy-credentials << 'EOF'
export GALAXY_URL="https://usegalaxy.org"
export GALAXY_API_KEY="your_actual_api_key_here"
EOF
```

### 2. Load Credentials

**Option A: Load manually when needed**
```bash
source ~/.galaxy-credentials
```

**Option B: Create an alias (recommended)**

Add to your `~/.bashrc` or `~/.zshrc`:
```bash
alias galaxy-env='source ~/.galaxy-credentials'
```

Then use:
```bash
galaxy-env  # Load credentials
claude "Using galaxy-bioblend.md, list my histories"
```

## Security Guidelines

### ✅ DO

- **Use file permissions 600** - Only you can read the credentials file
- **Add credential files to .gitignore** - Never commit secrets
- **Store credentials in your home directory** - Keep them separate from code
- **Use environment variables** - Don't hardcode API keys in scripts
- **Rotate API keys periodically** - Generate new keys every few months
- **Use different keys for different purposes** - Dev vs production, different projects

### ❌ DON'T

- **Never commit API keys to git** - Even in "private" repositories
- **Don't share API keys** - Each user should have their own
- **Don't hardcode keys in scripts** - Always use environment variables
- **Don't store keys in shell history** - Use `read -s` for sensitive input
- **Don't use world-readable permissions** - Always use 600 (user-only)

## Advanced Options

### Option 1: System Keyring (Most Secure)

#### Using `pass` (Linux/macOS)
```bash
# Install pass
sudo apt install pass  # Linux
brew install pass      # macOS

# Initialize (one time)
gpg --gen-key
pass init your-gpg-id

# Store credentials
pass insert galaxy/url
pass insert galaxy/api-key

# Use in scripts
export GALAXY_URL=$(pass show galaxy/url)
export GALAXY_API_KEY=$(pass show galaxy/api-key)
```

#### Using GNOME Keyring (Linux)
```bash
# Store credentials
secret-tool store --label='Galaxy URL' service galaxy field url
secret-tool store --label='Galaxy API Key' service galaxy field api-key

# Retrieve
export GALAXY_URL=$(secret-tool lookup service galaxy field url)
export GALAXY_API_KEY=$(secret-tool lookup service galaxy field api-key)
```

### Option 2: Project-Specific .env File

For specific projects:

```bash
# In your project directory
cd ~/my-galaxy-project

# Create .env file
cat > .env << 'EOF'
GALAXY_URL=https://usegalaxy.org
GALAXY_API_KEY=your_key_here
EOF

chmod 600 .env

# CRITICAL: Add to .gitignore
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore

# Load before use
source .env
```

### Option 3: Per-Command Loading

Create a wrapper script for one-off commands:

```bash
#!/bin/bash
# galaxy-claude.sh

# Load credentials
source ~/.galaxy-credentials

# Pass all arguments to Claude
claude "$@"
```

Usage:
```bash
chmod +x galaxy-claude.sh
./galaxy-claude.sh "Using galaxy-bioblend.md, list my histories"
```

## What to Add to .gitignore

Always ensure these patterns are in your `.gitignore`:

```gitignore
# Environment files
.env
.env.local
.env.*.local

# Credentials
*credentials*
*.key
*.secret

# Galaxy specific
.galaxy-*
galaxy-credentials*
```

## Getting Your API Key

1. Log in to your Galaxy instance (e.g., https://usegalaxy.org)
2. Click on **User** in the top menu
3. Select **Preferences**
4. Click **Manage API Key**
5. Click **Create a new key** (if you don't have one)
6. Copy the key shown

**Note:** API keys are not shown again after creation. If you lose it, you'll need to generate a new one.

## Rotating API Keys

It's good practice to rotate your API keys periodically:

1. Generate a new key in Galaxy (User → Preferences → Manage API Key)
2. Update your credentials file:
   ```bash
   ./setup-credentials.sh
   ```
3. Test the new key
4. Delete the old key from Galaxy

## Multiple Galaxy Instances

If you work with multiple Galaxy servers:

```bash
# Create separate credential files
cat > ~/.galaxy-credentials-usegalaxy-org << 'EOF'
export GALAXY_URL="https://usegalaxy.org"
export GALAXY_API_KEY="key_for_org"
EOF

cat > ~/.galaxy-credentials-usegalaxy-eu << 'EOF'
export GALAXY_URL="https://usegalaxy.eu"
export GALAXY_API_KEY="key_for_eu"
EOF

chmod 600 ~/.galaxy-credentials-*

# Create aliases
alias galaxy-org='source ~/.galaxy-credentials-usegalaxy-org'
alias galaxy-eu='source ~/.galaxy-credentials-usegalaxy-eu'

# Use
galaxy-org  # Switch to usegalaxy.org
galaxy-eu   # Switch to usegalaxy.eu
```

## Troubleshooting

### Permission Denied Errors

If you get permission errors:
```bash
chmod 600 ~/.galaxy-credentials
```

### API Key Not Working

1. Verify the key is correct (no extra spaces)
2. Check it's not expired
3. Generate a new key in Galaxy
4. Update your credentials file

### Credentials Not Loading

Make sure you're sourcing the file, not executing it:
```bash
source ~/.galaxy-credentials  # ✓ Correct
~/.galaxy-credentials          # ✗ Wrong
```

## Security Incident Response

If you believe your API key has been compromised:

1. **Immediately revoke the key** in Galaxy (User → Preferences → Manage API Key)
2. **Generate a new key**
3. **Update your credentials file**
4. **Review your Galaxy history** for unexpected activity
5. **Change your Galaxy password** if you suspect account compromise

## Questions?

- **Galaxy Security**: https://docs.galaxyproject.org/en/master/admin/security.html
- **Galaxy Help Forum**: https://help.galaxyproject.org/
- **Report Security Issues**: Contact your Galaxy instance administrator

---

**Remember:** Your API key is as sensitive as your password. Protect it accordingly! 🔒
