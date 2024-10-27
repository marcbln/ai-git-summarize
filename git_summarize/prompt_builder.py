class PromptBuilder:
    @staticmethod
    def build_diff_prompt(diff_text: str) -> list[dict]:
        """Build prompt for summarizing git diffs."""
        return [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes git "
                           "diffs and generates concise, informative commit "
                           "messages. A commit message should consist "
                           "of a concise single line summary, followed by a more "
                           "detailed explanation of the changes. Use bullet points "
                           "if appropriate. Do not use markdown for formatting. "
                           "Output the commit message directly without any labels or prefixes like 'Commit Message:'."
            },
            {
                "role": "user",
                "content": f"Please summarize the following git diff and "
                           f"generate a commit message in standard git format:\n\n{diff_text}"
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
