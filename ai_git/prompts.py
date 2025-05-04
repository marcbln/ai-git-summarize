from typing import List, Dict, Union

class PromptBuilder:
    MessageType = List[Dict[str, str]]
    
    @staticmethod
    def build_diff_prompt(diff_text: str) -> "PromptBuilder.MessageType":
        """Build prompt for summarizing git diffs."""
        return [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes git "
                           "diffs and generates Conventional Commit messages. "
                           "The summary line must start with one of: feat, fix, chore, docs, test, refactor, perf, or ci "
                           "followed by a concise description. Example: 'feat: add new authentication module'. "
                           "After the summary, provide a detailed explanation of the changes "
                           "using bullet points when appropriate. "
                           "Output only the commit message, without any additional labels or explanations."
            },
            {
                "role": "user",
                "content": f"Please summarize the following git diff and "
                           f"generate a commit message in standard git format:\n\n{diff_text}"
            }
        ]

    @staticmethod
    def build_short_diff_prompt(diff_text: str) -> "PromptBuilder.MessageType":
        """Build prompt for summarizing git diffs with single-line output."""
        return [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes git "
                           "diffs into concise, single-line Conventional Commit messages. "
                           "The message must start with one of: feat, fix, chore, docs, test, refactor, perf, or ci "
                           "followed by a colon and space, then a brief description. "
                           "Example: 'fix: resolve login page crash'. "
                           "Output just the formatted commit message without any additional text."
            },
            {
                "role": "user",
                "content": f"Please summarize the following git diff into a "
                           f"single-line commit message:\n\n{diff_text}"
            }
        ]

    @staticmethod
    def build_feedback_prompt(diff_text: str) -> "PromptBuilder.MessageType":
        """Build prompt for providing code quality feedback."""
        return [
            {
                "role": "system",
                "content": "You are a thorough code reviewer focused on code quality and best practices. "
                           "Analyze the provided git diff and provide constructive feedback on: "
                           "- Code style and formatting "
                           "- Potential bugs or edge cases "
                           "- Performance considerations "
                           "- Design patterns and architecture "
                           "- Testing considerations "
                           "- Documentation completeness "
                           "Suggest specific improvements where applicable. "
                           "Be direct but constructive in your feedback."
            },
            {
                "role": "user",
                "content": f"Please review these code changes and provide feedback "
                           f"on code quality and potential improvements:\n\n{diff_text}"
            }
        ]

    @staticmethod
    def build_ai_decides_prompt(diff_text: str, detailed: bool = True) -> "PromptBuilder.MessageType":
        """Build prompt where AI determines the Conventional Commit type."""
        return [
            {
                "role": "system",
                "content": "You are an expert at analyzing code changes and determining "
                           "the appropriate Conventional Commit type. Follow these rules:\n"
                           "1. First categorize the changes:\n"
                           "   - feat: New user-facing functionality\n"
                           "   - fix: Bug corrections\n"
                           "   - chore: Maintenance tasks\n"
                           "   - docs: Documentation changes\n"
                           "   - test: Test additions/modifications\n"
                           "   - refactor: Code improvements without behavior change\n"
                           "   - perf: Performance optimizations\n"
                           "   - ci: CI/CD pipeline changes\n"
                           "2. Choose the most specific applicable type\n"
                           "3. Format as: 'type: description'\n"
                           f"{'4. After the summary, provide detailed bullet points of changes' if detailed else ''}"
                           "\nOutput only the commit message, no additional text."
            },
            {
                "role": "user",
                "content": f"Analyze these changes and generate {'a detailed' if detailed else 'a single-line'} "
                           f"Conventional Commit message:\n\n{diff_text}"
            }
        ]

    @staticmethod
    def build_unified_prompt(diff_text: str) -> "PromptBuilder.MessageType":
        """Build unified prompt that lets AI decide between short and detailed formats."""
        return [
            {
                "role": "system",
                "content": """You are an expert at analyzing git diffs and generating optimal commit messages. Follow these rules:

1. First analyze the changes and determine if they warrant:
   - SHORT format (single line) for simple changes like:
     * Renames/refactors
     * Small fixes
     * Trivial updates
   - DETAILED format (multi-line) for:
     * Complex changes
     * Multiple files modified
     * Significant functionality changes

2. Use Conventional Commit types:
   feat: New features
   fix: Bug fixes
   chore: Maintenance
   docs: Documentation
   test: Tests
   refactor: Code improvements
   perf: Performance
   ci: CI/CD

3. Format:
   - SHORT: "type: description" (one line)
   - DETAILED: "type: description" followed by bullet points

Output ONLY the commit message. Absolutely no additional text, formatting, labels (like "SHORT:", "DETAILED:", "### Short Commit Message", etc.). The output must be the raw commit message content and nothing else."""
            },
            {
                "role": "user",
                "content": f"Analyze these changes and generate the optimal commit message:\n\n{diff_text}"
            }
        ]

    @staticmethod
    def build_history_prompt(commits: List[str], detail_level: str = "technical") -> "PromptBuilder.MessageType":
        """Build prompt for summarizing git commit history.
        
        Args:
            commits: List of commit messages
            detail_level: Level of detail ("technical", "non-technical", "overview")
            
        Returns:
            Formatted prompt messages
        """
        if detail_level == "technical":
            system_content = """You are a technical lead analyzing git commit history. 
Summarize these commits into a technical report highlighting:
- Major features and improvements
- Bug fixes and critical changes
- Architectural decisions
- Dependencies and tooling updates
Format as markdown with clear sections."""
        elif detail_level == "non-technical":
            system_content = """You are a product manager analyzing git commit history. 
Summarize these commits into a business-focused report highlighting:
- New user-facing features
- Bug fixes impacting users
- Performance improvements
- Notable technical debt
Keep it concise and avoid technical jargon."""
        else:  # overview
            system_content = """You are an executive assistant analyzing git commit history. 
Provide a high-level overview of these commits focusing on:
- Key themes and initiatives
- Major milestones
- Overall progress
Keep it very brief (3-5 bullet points max)."""

        return [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": "Here are the commits to analyze:\n\n" + "\n".join(commits)
            }
        ]

    @staticmethod
    def build_commit_analysis_prompt(
        diff_text: str,
        file_path: str | None = None,
        file_content: str | None = None
    ) -> "PromptBuilder.MessageType":
        """Build prompt for analyzing commit impact (refactoring vs. risk)."""

        system_content = """You are an expert code reviewer analyzing a git diff to determine its potential impact.
Your goal is to classify the changes as either 'Clean Refactoring' or 'Potential Risk'.

Follow these steps:
1. Analyze the provided git diff carefully.
2. If the diff alone is insufficient to make a confident assessment (e.g., you need to see the surrounding code in a modified file), respond ONLY with a JSON object like this: {"request_file": "path/to/the/file/you/need/to/see.py"}. Use the file path exactly as it appears in the diff header (e.g., 'a/path/to/file.py' or 'b/path/to/file.py'). Do not add any other text or explanation.
3. If you have enough information (either from the initial diff or after receiving requested file content), classify the changes:
    - 'Clean Refactoring': Changes improve code structure, readability, or performance without altering functionality or introducing obvious risks.
    - 'Potential Risk': Changes might introduce bugs, break existing functionality, have significant side effects, or lack clarity/tests.
4. Provide a brief justification for your classification, explaining the key factors that led to your decision. Use bullet points for clarity if needed.
5. Format your final response clearly, starting with the classification label (e.g., "Classification: Potential Risk").

Example Response (Final Analysis):
Classification: Clean Refactoring
Justification:
- Renamed variable 'temp' to 'user_input' for clarity.
- Extracted logic into a new private helper method '_process_data'.
- No functional changes observed.

Example Response (Requesting File):
{"request_file": "git_summarize/utils/helper.py"}
"""

        user_messages = []
        if file_path and file_content:
            user_messages.append({
                "role": "user",
                "content": f"Here is the original git diff:\n\n{diff_text}\n\nYou previously requested the content for '{file_path}'. Here it is:\n\n```\n{file_content}\n```\n\nPlease analyze the diff again with this additional context and provide your final classification and justification."
            })
        else:
            user_messages.append({
                "role": "user",
                "content": f"Please analyze the following git diff and classify it as 'Clean Refactoring' or 'Potential Risk'. Provide justification. If you need the full content of a specific file from the diff to make a decision, please request it using the specified JSON format.\n\nGit Diff:\n{diff_text}"
            })

        return [
            {
                "role": "system",
                "content": system_content
            }
        ] + user_messages
