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

#     @staticmethod
#     def build_commits_prompt(commits: str) -> list[dict]:
#         """Build prompt for summarizing commit messages."""
#         prompt = f"""Please analyze these git commit messages and provide a concise summary of the changes:

# {commits}

# Format the response as a bullet point list of the main changes."""

#         return [
#             {
#                 "role": "user",
#                 "content": prompt
#             }
#         ]
