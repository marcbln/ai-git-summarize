import subprocess

def get_git_diff():
    """Fetch and return the git diff of staged changes."""
    print("\nFetching git diff...")
    try:
        result = subprocess.run(['git', 'diff', '--cached'], 
                              capture_output=True, text=True, check=True)
        diff_text = result.stdout
        if not diff_text:
            print("Warning: No changes found in git diff")
            return None
        print(f"Successfully retrieved diff ({len(diff_text)} characters)")
        return diff_text
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to get git diff. Command output: {e.stderr}")
        print("Ensure you're in a git repository and have staged changes.")
        return None

def commit_changes(message: str) -> bool:
    """Commit changes with the given message."""
    try:
        print("\nCommitting changes...")
        subprocess.run(['git', 'commit', '-m', message], check=True)
        print("Changes committed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to commit changes. Command output: {e.stderr}")
        return False
