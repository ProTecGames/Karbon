# Contribution Guide
🌟 Welcome to the Karbon community! 🌟
Thank you for your interest in contributing to Karbon – The AI Web Builder! We welcome all kinds of contributions: code, bug reports, ideas, documentation, and design improvements.

## Getting Started:

1. Fork the Repository
    Click the Fork button at the top right of the main repo page to create your own copy.
    
2. Clone Your Forked Repo
    ```bash
    git clone https://github.com/your-username/karbon.git
    cd karbon
    ```
    
3. Install Requirements
    ```bash
    pip install -r requirements.txt
    ```

    For extra components (Tkinter, Pillow), you may need to run:
        ```bash
        pip install Pillow
        ```

5. Run the App Locally
    ```bash
    python main.py
    ```
🌟 The Karbon window should now appear! 🌟

## How to Contribute:

1. Find or Open an Issue:
   - Browse existing issues on the issues' tab.
   - Use filters like good first issue for beginner-friendly tasks.
   - If you spot a bug or want to suggest a feature not yet listed, open a new issue.
   - Please provide: A descriptive title; steps to reproduce or the feature you propose; any relevant error logs or screenshots.

2. Assigning Issues:
   - To claim an unassigned issue, comment by tagging the repo-owner. Only the project owner/maintainers can assign issues.
   
3. Create a Feature Branch:
    ```bash
    git checkout -b feature/your-feature-name
    ```
    
📌 Use informative branch names related to your work.

4. Make & Test Your Changes:
   
   - Update or add code, always following Karbon's coding style and existing structure (see files such as contributor_page.py, ui_items/, and core/).
   - If you add dependencies, update requirements.txt.
   - For UI work, run the app to verify everything appears and functions correctly.
   - Add or update docstrings and comments as needed.
    
5. Commit & Push
   
    - Write clear commit messages, referencing the related issue number in your message (e.g., Fix: #42 – Bug with export button).
    - Push your branch to your fork:
        ```bash
        git push origin feature/your-feature-name
        ```
    
6. Open a Pull Request:
   
    Go to your forked repo on GitHub and click Compare & pull request.
   
    In your PR description: 
    - Reference the relevant issue(s) with Closes #issue_number or Fixes #issue_number. 
    - Include what your PR does, steps to test, and any screenshots/Demo gifs for UI changes.
    - Respond to any maintainer feedback and make updates as needed.

7. Stay Updated:
    
    Pull the latest changes from main often to avoid conflicts.
    ```bash
    git pull upstream main
    ```

📌 Respectful behavior and inclusive collaboration are expected from all contributors. If you need help, open an issue or ask in Discussions. We’re excited to build with you.
