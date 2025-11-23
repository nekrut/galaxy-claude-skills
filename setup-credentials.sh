#!/bin/bash
# Galaxy Credentials Setup Script
# This script helps you securely store your Galaxy API credentials

set -e

CRED_FILE="$HOME/.galaxy-credentials"
BACKUP_FILE="$HOME/.galaxy-credentials.backup"

echo "========================================="
echo "Galaxy Credentials Setup"
echo "========================================="
echo ""

# Check if credentials file already exists
if [ -f "$CRED_FILE" ]; then
    echo "⚠️  Credentials file already exists: $CRED_FILE"
    read -p "Do you want to overwrite it? (yes/no): " OVERWRITE
    if [ "$OVERWRITE" != "yes" ]; then
        echo "Aborted. Your existing credentials were not modified."
        exit 0
    fi
    # Create backup
    cp "$CRED_FILE" "$BACKUP_FILE"
    echo "✓ Backup created: $BACKUP_FILE"
fi

# Prompt for Galaxy URL
echo ""
echo "Enter your Galaxy server URL"
echo "Examples:"
echo "  - https://usegalaxy.org"
echo "  - https://usegalaxy.eu"
echo "  - https://usegalaxy.org.au"
echo "  - https://your-custom-galaxy.org"
echo ""
read -p "Galaxy URL: " GALAXY_URL

# Validate URL format
if [[ ! "$GALAXY_URL" =~ ^https?:// ]]; then
    echo "❌ Error: URL must start with http:// or https://"
    exit 1
fi

# Prompt for API Key
echo ""
echo "Enter your Galaxy API Key"
echo "To get your API key:"
echo "  1. Log in to your Galaxy instance"
echo "  2. Go to: User → Preferences → Manage API Key"
echo "  3. Copy the key shown there"
echo ""
read -s -p "Galaxy API Key: " GALAXY_API_KEY
echo ""

# Validate API key is not empty
if [ -z "$GALAXY_API_KEY" ]; then
    echo "❌ Error: API key cannot be empty"
    exit 1
fi

# Create credentials file
cat > "$CRED_FILE" << EOF
# Galaxy API Credentials
# Generated: $(date)
#
# To use these credentials, run:
#   source ~/.galaxy-credentials
#
# Or add this alias to your ~/.bashrc or ~/.zshrc:
#   alias galaxy-env='source ~/.galaxy-credentials'

export GALAXY_URL="$GALAXY_URL"
export GALAXY_API_KEY="$GALAXY_API_KEY"
EOF

# Set secure permissions (read/write for owner only)
chmod 600 "$CRED_FILE"

echo ""
echo "========================================="
echo "✓ Setup Complete!"
echo "========================================="
echo ""
echo "Your credentials have been saved to:"
echo "  $CRED_FILE"
echo ""
echo "File permissions: 600 (read/write for you only)"
echo ""
echo "To use your credentials:"
echo "  source ~/.galaxy-credentials"
echo ""
echo "Or add this to your ~/.bashrc or ~/.zshrc for automatic loading:"
echo "  alias galaxy-env='source ~/.galaxy-credentials'"
echo ""
echo "Then you can use:"
echo "  galaxy-env  # Load credentials"
echo "  claude \"Using galaxy-bioblend.md, list my histories\""
echo ""

# Test connection option
read -p "Would you like to test the connection now? (yes/no): " TEST_CONN

if [ "$TEST_CONN" = "yes" ]; then
    echo ""
    echo "Testing connection to Galaxy..."

    # Source the credentials
    source "$CRED_FILE"

    # Try to connect using curl
    if command -v curl &> /dev/null; then
        response=$(curl -s -w "\n%{http_code}" "${GALAXY_URL}/api/version" -H "x-api-key: ${GALAXY_API_KEY}" 2>&1)
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n-1)

        if [ "$http_code" = "200" ]; then
            echo "✓ Connection successful!"
            echo "Galaxy version: $(echo "$body" | grep -o '"version_major":"[^"]*"' | cut -d'"' -f4)"
        elif [ "$http_code" = "401" ]; then
            echo "❌ Authentication failed. Please check your API key."
        elif [ "$http_code" = "404" ]; then
            echo "❌ Galaxy server not found. Please check your URL."
        else
            echo "⚠️  Unexpected response (HTTP $http_code)"
            echo "Response: $body"
        fi
    else
        echo "⚠️  curl not found. Install curl to test the connection."
        echo "Your credentials are saved, but connection test was skipped."
    fi
fi

echo ""
echo "Happy Galaxy analysis! 🚀"
