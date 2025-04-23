import subprocess
from typing import Tuple, Optional, List

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

def get_commit_diff(commit_ref: str, cwd: Optional[str] = None) -> Optional[str]:
    """Fetch and return the git diff for a specific commit reference.

    Args:
        commit_ref: The commit hash, tag, branch, or reference (e.g., 'HEAD', 'HEAD^').
        cwd: Working directory to run git command in (optional).

    Returns:
        The diff text as a string, or None if an error occurs or the commit has no diff.
    """
    print(f"\nFetching diff for commit: {commit_ref}...")
    # Remove --no-patch-if-empty as it might not be supported in all git versions
    cmd = ['git', 'show', '--pretty=format:', commit_ref]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
            errors='replace'
        )
        diff_text = result.stdout.strip() # Remove potential leading/trailing whitespace
        if not diff_text:
            print(f"Warning: No textual changes found for commit {commit_ref}")
            # Return empty string for commits with no diff (e.g., merge commits with no changes)
            # rather than None, as None usually indicates an error fetching.
            return ""
        print(f"Successfully retrieved diff for {commit_ref} ({len(diff_text)} characters)")
        return diff_text
    except subprocess.CalledProcessError as e:
        stderr_lower = e.stderr.lower()
        if "unknown revision or path not in the working tree" in stderr_lower or \
           "invalid object name" in stderr_lower:
             print(f"Error: Invalid commit reference '{commit_ref}'. {e.stderr.strip()}")
        else:
            print(f"Error: Failed to get diff for commit '{commit_ref}'. Command output: {e.stderr.strip()}")
        return None
    except FileNotFoundError as e:
         print(f"Error: 'git' command not found. Ensure Git is installed and in your PATH. {e}")
         return None
    except Exception as e:
        print(f"Unexpected error getting commit diff: {e}")
        return None

def get_configured_remotes() -> List[str]:
    """Get list of configured git remotes."""
    try:
        result = subprocess.run(['git', 'remote'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except subprocess.CalledProcessError:
        return []

def commit_changes(message: str) -> bool:
    """Commit changes with the given message."""
    try:
        print("\nCommitting changes...")
        result = subprocess.run(['git', 'commit', '-m', message], 
                              capture_output=True, text=True, check=True)
        print("Changes committed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to commit changes. Command output: {e.stderr}")
        return False

def get_commit_messages(commit_range: str = "HEAD~7..HEAD", cwd: Optional[str] = None) -> List[str]:
    """Get commit messages from git history.
    
    Args:
        commit_range: Git commit range (e.g. "HEAD~7..HEAD")
        cwd: Working directory to run git command in (optional)
        
    Returns:
        List of commit messages
    """
    try:
        cmd = ['git', 'log']
        if commit_range:
            # Split the commit range into parts to handle date ranges
            if commit_range.startswith('--since') or commit_range.startswith('--until'):
                # Handle date range parameters
                parts = commit_range.split()
                cmd.extend(parts)
            else:
                # Handle regular commit range
                cmd.append(commit_range)
        
        cmd.append('--pretty=format:%s')
        
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, check=True,
            cwd=cwd
        )
        if not result.stdout:
            print(f"Warning: No commits found in range {commit_range}")
            return []
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to get commit history. Command output: {e.stderr}")
        return []


def push_changes(remote: str = "origin", branch: str = "") -> bool:
    """Push changes to remote repository."""
    try:
        print("\nPushing changes...")
        remotes = get_configured_remotes()
        if not remotes:
            print("Error: No configured remote repositories found.")
            print("Add a remote repository using: git remote add <name> <url>")
            return False
            
        if remote not in remotes:
            print(f"Warning: Remote '{remote}' not found. Available remotes: {', '.join(remotes)}")
            remote = remotes[0]
            print(f"Using '{remote}' instead.")

        cmd = ['git', 'push', remote]
        if branch:
            cmd.append(branch)
            
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Changes pushed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to push changes. Command output: {e.stderr}")
        return False

def get_file_content_at_commit(commit_ref: str, file_path: str, cwd: Optional[str] = None) -> Optional[str]:
    """Retrieve the content of a specific file at a given commit reference.

    Args:
        commit_ref: The commit hash, tag, branch, or reference (e.g., 'HEAD^').
        file_path: The path to the file relative to the repository root.
        cwd: Working directory to run git command in (optional).

    Returns:
        The content of the file as a string, or None if an error occurs.

    Raises:
        FileNotFoundError: If the file does not exist at the specified commit.
        subprocess.CalledProcessError: For other git command errors.
    """
    cmd = ['git', 'show', f'{commit_ref}:{file_path}']
    try:
        print(f"Executing: {' '.join(cmd)} in {cwd or '.'}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=cwd,
            errors='replace' # Handle potential decoding errors
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        stderr_lower = e.stderr.lower()
        if f"exists on disk, but not in '{commit_ref}'" in stderr_lower or \
           f"does not exist in '{commit_ref}'" in stderr_lower or \
           "invalid object name" in stderr_lower: # Also catch invalid commit refs here
            # Raise FileNotFoundError specifically, as expected by the caller
            raise FileNotFoundError(f"File '{file_path}' not found at commit '{commit_ref}'. Git error: {e.stderr.strip()}") from e
        else:
            # Re-raise other git errors
            print(f"Error: Failed to get file content for '{file_path}' at '{commit_ref}'. Command output: {e.stderr}")
            raise # Re-raise the original CalledProcessError
    except FileNotFoundError as e:
        # This catches if 'git' command itself is not found
         print(f"Error: 'git' command not found. Ensure Git is installed and in your PATH. {e}")
         raise # Re-raise the FileNotFoundError
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected error getting file content: {e}")
        raise # Re-raise the unexpected error
