# GitHub Integration for Karbon

## Overview

This document provides an overview of the GitHub integration implementation for Karbon, which allows users to export their projects directly to GitHub repositories.

## Features

- **GitHub Token Management**: Secure storage and validation of GitHub personal access tokens
- **Repository Creation**: Automatic creation of repositories if they don't exist
- **Code Export**: Export project code to GitHub repositories
- **Error Handling**: Comprehensive error handling and user feedback
- **UI Integration**: Seamless integration with the Karbon UI

## Components

### Token Management

- `token_manager.py`: Handles encryption, decryption, storage, and validation of GitHub tokens
- `token_manager_view.py`: Provides the UI for token management

### GitHub Integration

- `exporter.py`: Contains the main export functionality and token validation
- `github_exporter.py`: Handles repository creation and management
- `repo_pusher.py`: Manages Git operations for pushing code to GitHub

### UI Integration

- `karbon_ui.py`: Integrates GitHub export functionality into the main Karbon UI

## Security Considerations

- GitHub tokens are encrypted using the `cryptography` library
- Tokens are never stored in plain text
- Token validation is performed before any GitHub operations

## Testing

The implementation includes comprehensive test scripts:

- `test_github_integration.py`: Basic token validation and management test
- `test_github_integration_full.py`: Comprehensive test of token management and repository operations
- `test_karbon_export.py`: Test of the Karbon export functionality
- `test_token_ui.py`: Test of the token management UI

## Usage

### Setting Up a GitHub Token

1. Navigate to the GitHub Token Manager in Karbon
2. Click "Generate Token" to open GitHub's token creation page
3. Create a token with the `repo` scope
4. Copy the token and paste it into the Token Manager
5. Click "Save Token" to securely store the token
6. Click "Test Connection" to verify the token works

### Exporting to GitHub

1. Create or open a project in Karbon
2. Click the "Export" button
3. Select "Export to GitHub"
4. Enter a repository name
5. Click "Export" to push the code to GitHub

## Implementation Details

### Token Validation

The `validate_github_token` function in `exporter.py` validates GitHub tokens by:

1. Decrypting the stored token (if not provided)
2. Attempting to authenticate with GitHub
3. Retrieving the user information
4. Returning a tuple with validation status, username, and any error messages

### Repository Management

The `create_repo` function in `github_exporter.py` handles repository creation by:

1. Validating the GitHub token
2. Checking if the repository already exists
3. Creating a new repository if needed
4. Returning the repository object

### Code Export

The `export_to_github` function in `exporter.py` exports code to GitHub by:

1. Validating the GitHub token
2. Getting the GitHub user
3. Creating or accessing the repository
4. Creating or updating the index.html file
5. Returning the repository URL

## Future Improvements

- Support for exporting multiple files and directories
- Support for branch management
- Support for pull requests
- Integration with GitHub Actions for CI/CD
- Support for other Git hosting services (GitLab, Bitbucket, etc.)

## Dependencies

- `cryptography`: For token encryption and decryption
- `PyGithub`: For GitHub API integration
- `GitPython`: For Git operations