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
