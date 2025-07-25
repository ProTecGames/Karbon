# GitHub Export Integration with Encrypted Token Storage

## Overview

This feature allows users to export their generated website code directly to a GitHub repository using a GitHub personal access token (PAT). The token is stored securely and encrypted on the user's machine, with options for users to update or change the token at any time.

## Features

- **Secure Token Storage**: GitHub tokens are encrypted using Fernet symmetric encryption and stored locally
- **Token Management UI**: A dedicated interface for adding, testing, and removing GitHub tokens
- **Automatic Username Detection**: The system automatically detects the GitHub username from the token
- **Repository Creation**: Automatically creates repositories if they don't exist
- **Error Handling**: Comprehensive error handling for token validation, network issues, and GitHub API errors

## How to Use

### Setting Up Your GitHub Token

1. Generate a GitHub Personal Access Token:
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token" → "Generate new token (classic)"
   - Give your token a name (e.g., "Karbon Web Builder")
   - Select the `repo` scope (Full control of private repositories)
   - Click "Generate token"
   - **IMPORTANT**: Copy your token immediately as GitHub will only show it once

2. In Karbon:
   - Go to GitHub → Manage Token
   - Paste your token in the field
   - Click "Save Token"
   - Click "Test Connection" to verify it works

### Exporting to GitHub

1. Create your website using Karbon
2. Go to File → Export Code
3. The system will:
   - Save your code locally
   - Create or update a GitHub repository
   - Push your code to the repository
   - Provide a link to view your repository

## Technical Implementation

### Components

- **token_manager.py**: Handles encryption, decryption, and storage of GitHub tokens
- **token_manager_view.py**: Provides the UI for token management
- **github_exporter.py**: Creates GitHub repositories
- **repo_pusher.py**: Pushes code to GitHub repositories
- **exporter.py**: Coordinates the export process

### Security Considerations

- Tokens are encrypted using Fernet symmetric encryption
- The encryption key is stored locally in a separate file
- Tokens are never logged or displayed in plain text
- The system validates tokens before use

## Troubleshooting

### Common Issues

- **Invalid Token**: Ensure your token has the `repo` scope and hasn't expired
- **Connection Failed**: Check your internet connection
- **Repository Creation Failed**: Verify you have permission to create repositories
- **Push Failed**: Ensure your token has the correct permissions

### Testing

You can test the GitHub integration using the provided test script:

```bash
python test_github_integration.py
```

## Future Improvements

- Support for organization repositories
- Branch selection
- Custom commit messages
- Support for private/public repository settings