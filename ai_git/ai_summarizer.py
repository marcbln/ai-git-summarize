import json
import re
import os
from typing import Optional, Dict, Any, List
from openai import OpenAI
from rich import print as rprint
from rich.panel import Panel
from .prompts import PromptBuilder
from .git_operations import get_file_content_at_commit # Assuming this will be added
from .config_utils import resolve_model_alias


class AISummarizer:
    """Class to handle AI-powered code summarization and feedback."""
    
    def __init__(self, client: OpenAI):
        """Initialize with an OpenAI client instance."""
        self.client = client

    def _prepare_api_kwargs(self, messages: list, model: str, max_tokens: int = 100) -> Dict[str, Any]:
        """Prepare kwargs for API call based on model type."""
        try:
            # The model parameter is already the resolved identifier
            print(f"Using model: {model}")
            
            if model.startswith("openrouter/"):
                actual_model = model.replace("openrouter/", "", 1)
                print(f"Using OpenRouter with model: {actual_model}")
                kwargs = {
                    "extra_headers": {
                        "X-Title": "ai-git-summarize",
                    },
                    "model": actual_model,
                    "messages": messages,
                }
            else:
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens
                }
            
            print(f"API configuration:\n{json.dumps(kwargs, indent=2)}")
            return kwargs
        except Exception as e:
            # Log the error but don't handle UnknownModelAliasError here
            # It should be handled at the command level (git_summary.py)
            print(f"Error preparing API kwargs: {e}")
            raise

    def _make_api_call(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """Make API call with error handling and response validation."""
        try:
            model_display = kwargs.get('model', 'unknown model')
            # If this is an OpenRouter model (which would have had the prefix removed in _prepare_api_kwargs),
            # we should display it with the openrouter/ prefix in the message
            if 'extra_headers' in kwargs and 'X-Title' in kwargs['extra_headers']:
                model_display = f"openrouter/{model_display}"
            print(f"\nSending API request to {model_display}...")
            response = self.client.chat.completions.create(**kwargs)
            print("Successfully received API response")
            print(f"\nFull API response: {response.json()}")

            # Validate response
            if (not response or not hasattr(response, 'choices') or
                not response.choices or not hasattr(response.choices[0], 'message') or
                not hasattr(response.choices[0].message, 'content')):
                print("Error: Invalid API response structure")
                return None

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"\nError when calling API: {type(e).__name__} - {str(e)}")
            if hasattr(e, 'response'):
                print(f"Response details: {e.response}")
            if hasattr(e, '__dict__'):
                print(f"Full error details: {e.__dict__}")
            return None
            
    def _strip_backticks(self, text: Optional[str]) -> Optional[str]:
        """Removes surrounding backticks and standalone backtick lines."""
        if text is None:
            return None

        text = text.strip()

        if not text:
            return None

        # Remove surrounding backticks (any quantity)
        # Remove surrounding backticks, prioritizing triple backticks with language ID
        triple_match = re.match(r"^```(?:[a-zA-Z0-9_.-]*)?\s*\n?(.*?)\n?```$", text, re.DOTALL)
        if triple_match:
            text = triple_match.group(1).strip()
        else:
            # Fallback to matching any number of surrounding backticks (single, double, etc.)
            # This handles cases like `code` or ``code`` after the triple check failed.
            general_match = re.match(r"^`+(.*?)`+$", text, re.DOTALL)
            if general_match:
                text = general_match.group(1).strip()

        # Remove lines containing only backticks (any quantity)
        cleaned_lines = [
            line.rstrip('\n')
            for line in text.split('\n')
            if line.strip().strip('`').strip()  # True if line has non-backtick content
        ]

        return '\n'.join(cleaned_lines).strip()

    def generate_code_feedback(self, diff_text: str, model: str) -> Optional[str]:
        """Generate code quality feedback using AI.
        
        Args:
            diff_text: Git diff text to analyze
            model: Name of the model to use (can include 'openrouter/' prefix)
            
        Returns:
            str: Generated feedback if successful
            None: If API call fails
        """
        print(f"\nGenerating feedback using model: {model}")
        messages = PromptBuilder.build_feedback_prompt(diff_text)
        kwargs = self._prepare_api_kwargs(messages, model, max_tokens=300)
        return self._make_api_call(kwargs)

    def summarize_history(self, commit_range: str, model: str, detail_level: str = "technical") -> Optional[str]:
        """Summarize a range of git commits.
        
        Args:
            commit_range: Git commit range (e.g. "HEAD~7..HEAD")
            model: Model to use for summarization
            detail_level: Level of detail ("technical", "non-technical", "overview")
            
        Returns:
            str: Generated summary if successful
            None: If API call fails
        """
        commits = self._get_commit_messages(commit_range)
        if not commits:
            return None
        return self._summarize_commit_history(commits, model, detail_level)

    def _get_commit_messages(self, commit_range: str) -> List[str]:
        """Get commit messages from git history.
        
        Args:
            commit_range: Git commit range
            
        Returns:
            List of commit messages
        """
        from .git_operations import get_commit_messages
        return get_commit_messages(commit_range)

    def _summarize_commit_history(self, commits: List[str], model: str, detail_level: str) -> Optional[str]:
        """Generate summary from commit messages.
        
        Args:
            commits: List of commit messages
            model: Model to use
            detail_level: Level of detail
            
        Returns:
            str: Generated summary
        """
        messages = PromptBuilder.build_history_prompt(commits, detail_level)
        kwargs = self._prepare_api_kwargs(messages, model, max_tokens=500)
        return self._make_api_call(kwargs)

    def generate_project_report(
        self,
        projects: List[str],
        start_date: str,
        end_date: str,
        model: str
    ) -> Dict[str, Any]:
        """Generate a report for multiple projects between dates.
        
        Args:
            projects: List of project paths
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            model: Model to use for analysis
            
        Returns:
            Dictionary containing report data
        """
        from datetime import datetime
        from .git_operations import get_commit_messages
        
        report_data = {
            "period": {
                "start": start_date,
                "end": end_date
            },
            "projects": [],
            "total_commits": 0,
            "unique_authors": set(),
            "files_changed": 0
        }
        
        for project_path in projects:
            try:
                # Get commits for this project within date range
                commits = get_commit_messages(
                    f"--since={start_date} --until={end_date}",
                    cwd=project_path
                )
                
                if not commits:
                    continue
                    
                # Get commit stats for this project
                stats = self._get_commit_stats(project_path, start_date, end_date)
                
                project_report = {
                    "path": project_path,
                    "commit_count": len(commits),
                    "authors": stats.get("authors", []),
                    "files_changed": stats.get("files_changed", 0),
                    "commits": commits
                }
                
                report_data["projects"].append(project_report)
                report_data["total_commits"] += len(commits)
                report_data["unique_authors"].update(stats.get("authors", []))
                report_data["files_changed"] += stats.get("files_changed", 0)
                
            except Exception as e:
                print(f"Error processing project {project_path}: {str(e)}")
                continue
                
        # Convert authors set to list
        report_data["unique_authors"] = list(report_data["unique_authors"])
        
        return report_data
        
    def _get_commit_stats(self, project_path: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get commit statistics for a project within date range.
        
        Args:
            project_path: Path to git project
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary with stats:
            - authors: list of unique authors
            - files_changed: total files changed
        """
        import subprocess
        from collections import defaultdict
        
        stats = {
            "authors": set(),
            "files_changed": 0
        }
        
        try:
            # Get unique authors
            author_cmd = [
                "git", "log",
                f"--since={start_date}",
                f"--until={end_date}",
                "--pretty=format:%an",
                "--no-merges"
            ]
            authors = subprocess.check_output(
                author_cmd,
                cwd=project_path,
                text=True
            ).strip().split('\n')
            if authors and authors[0]:  # Check if there are any authors
                stats["authors"] = set(authors)
            
            # Get files changed count
            files_cmd = [
                "git", "log",
                f"--since={start_date}",
                f"--until={end_date}",
                "--name-only",
                "--pretty=format:",
                "--no-merges"
            ]
            files = subprocess.check_output(
                files_cmd,
                cwd=project_path,
                text=True
            ).strip().split('\n')
            stats["files_changed"] = len(set(f for f in files if f))
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting stats for {project_path}: {e}")
            
        return stats

    def summarize_changes(
        self,
        diff_text: str,
        model: str,
        strategy: str
    ) -> Optional[str]:
        """Generate a commit message summary using AI based on the specified strategy.
        
        Args:
            diff_text: Git diff text to summarize
            model: Name of the model to use (can include 'openrouter/' prefix)
            strategy: Commit message strategy ('ai', 'short', 'detailed')
            
        Returns:
            str: Generated commit message summary if successful
            None: If API call fails or response is invalid
        """
        print(f"\nGenerating summary using model: {model} with strategy: {strategy}")
        
        if strategy == "ai":
            print(Panel("Using AI to determine optimal commit message format.",
                      title="[bold]AI Decision[/bold]", border_style="green", expand=False))
            messages = PromptBuilder.build_unified_prompt(diff_text)
        elif strategy == "short":
            print(Panel("Generating SHORT commit message.", title="[bold]Strategy[/bold]", border_style="yellow", expand=False))
            messages = PromptBuilder.build_short_diff_prompt(diff_text)
        elif strategy == "detailed":
            print(Panel("Generating DETAILED commit message.", title="[bold]Strategy[/bold]", border_style="cyan", expand=False))
            messages = PromptBuilder.build_diff_prompt(diff_text)
        else:
            raise ValueError(f"Invalid strategy: {strategy}. Valid options are 'unified', 'short', 'detailed'")

        if not messages:
            raise RuntimeError("Failed to generate prompt messages for commit strategy")

        print(f"\nGenerated prompt with {len(messages)} messages")
        
        kwargs = self._prepare_api_kwargs(messages, model)
        summary = self._make_api_call(kwargs)
        return self._strip_backticks(summary)

    def analyze_commit_impact(
        self,
        diff_text: str,
        model: str,
        commit_ref: str, # Needed to fetch file content at the correct version
        repo_path: str = "." # Assume current directory is repo root unless specified
    ) -> Optional[str]:
        """Analyze git diff for potential risks, requesting file context if needed.

        Args:
            diff_text: Git diff text to analyze.
            model: Name of the model to use.
            commit_ref: The specific commit reference (e.g., 'HEAD', hash) for context.
            repo_path: Path to the git repository root.

        Returns:
            str: AI's analysis ('Clean Refactoring' or 'Potential Risk' with justification).
            None: If API calls fail or critical errors occur.
        """
        print(f"\nAnalyzing commit impact using model: {model} for commit: {commit_ref}")

        # --- Initial Analysis Attempt ---
        messages = PromptBuilder.build_commit_analysis_prompt(diff_text)
        kwargs = self._prepare_api_kwargs(messages, model, max_tokens=500) # Use a potentially larger token count for analysis
        initial_response = self._make_api_call(kwargs)

        if not initial_response:
            return None # API call failed

        # --- Check for File Request ---
        requested_file = None
        try:
            # Use regex to find the specific JSON structure, allowing for surrounding text
            # This looks for {"request_file": "some/path.py"} potentially within other text.
            # It captures the file path.
            match = re.search(r'{\s*"request_file"\s*:\s*"([^"]+)"\s*}', initial_response)
            if match:
                requested_file = match.group(1)
                print(Panel(f"AI requested context for file: [bold cyan]{requested_file}[/]",
                          title="[bold yellow]File Request[/]", border_style="yellow"))
            else:
                 print("AI did not request specific file context.")

        except Exception as e:
            # Log if regex or parsing fails, but proceed assuming no valid request found
            print(f"[yellow]Warning:[/yellow] Could not parse potential file request from AI response: {e}. Assuming direct analysis.")
            requested_file = None # Ensure it's None if parsing failed

        # --- Handle File Request or Return Initial Analysis ---
        if requested_file:
            try:
                # Attempt to fetch the file content at the *parent* of the commit_ref
                if requested_file.startswith('a/') or requested_file.startswith('b/'):
                    actual_file_path = requested_file[2:]
                else:
                    actual_file_path = requested_file

                parent_commit_ref = f"{commit_ref}^"
                print(f"Fetching content for '{actual_file_path}' at commit '{parent_commit_ref}'...")

                file_content = get_file_content_at_commit(parent_commit_ref, actual_file_path, cwd=repo_path)

                if file_content is None: # Function might return None on git errors handled internally
                     print(f"[bold red]Error:[/bold red] Failed to retrieve content for '{actual_file_path}' at commit '{parent_commit_ref}'.")
                     return f"Error: Failed to retrieve content for requested file '{requested_file}'."

                print(f"Successfully fetched content for '{actual_file_path}'.")

                # --- Second Analysis Attempt with Context ---
                messages = PromptBuilder.build_commit_analysis_prompt(
                    diff_text,
                    file_path=requested_file, # Pass the original requested path for context
                    file_content=file_content
                )
                kwargs = self._prepare_api_kwargs(messages, model, max_tokens=1000) # Allow more tokens for combined context

                print("Sending follow-up request with file context...")
                final_response = self._make_api_call(kwargs)

                # Strip backticks just in case the final response has them
                return self._strip_backticks(final_response)

            except FileNotFoundError as e:
                # Handle file not found specifically after request
                print(f"[bold red]Error:[/bold red] {e}")
                return f"Error: AI requested file '{requested_file}', but it could not be found at commit '{parent_commit_ref}'."
            except Exception as e:
                # Handle other errors during file fetching/second call
                print(f"[bold red]Error processing file request or follow-up analysis:[/bold red] {e}")
                return f"Error during follow-up analysis after requesting file '{requested_file}': {e}"
        else:
            # No valid file request found, return the initial analysis
            print("Proceeding with initial analysis result.")
            return self._strip_backticks(initial_response)
