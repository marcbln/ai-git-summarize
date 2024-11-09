import subprocess
from typing import Tuple, Optional

def check_unstaged_changes() -> Tuple[bool, str]:
    """Check if there are any unstaged changes."""
    try:
        result = subprocess.run(['git', 'diff'], 
                              capture_output=True, text=True, check=True)
        return bool(result.stdout), result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to check unstaged changes. Command output: {e.stderr}")
        return False, ""

def stage_all_changes() -> bool:
    """Stage all changes."""
    try:
        subprocess.run(['git', 'add', '-A'], check=True)
        print("Successfully staged all changes")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to stage changes. Command output: {e.stderr}")
        return False

def get_git_diff() -> Optional[str]:
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

def push_changes() -> bool:
    """Push committed changes to remote repository."""
    try:
        print("\nPushing changes...")
        subprocess.run(['git', 'push'], check=True)
        print("Changes pushed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to push changes. Command output: {e.stderr}")
        return False
