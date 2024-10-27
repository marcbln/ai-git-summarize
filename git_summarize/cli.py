# git_summarize/cli.py
import subprocess
import os
import sys
import argparse
from openai import OpenAI

def setup_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set")
        sys.exit(1)
    return OpenAI(api_key=api_key)

def get_git_diff():
    try:
        result = subprocess.run(['git', 'diff', '--cached'], 
                              capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        print("Error: Failed to get git diff. Ensure you're in a git repository "
              "and have staged changes.")
        return None

def summarize_with_openai(client, diff_text, model="gpt-3.5-turbo"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", 
                 "content": "You are a helpful assistant that summarizes git "
                           "diffs and generates concise, informative commit "
                           "messages. The response should be in the format of "
                           "a concise single line summary, followed by a more "
                           "detailed explanation of the changes."},
                {"role": "user", 
                 "content": f"Please summarize the following git diff and "
                           f"generate a concise commit message:\n\n{diff_text}"}
            ],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error when calling OpenAI API: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description='Generate commit messages from git diff using OpenAI'
    )
    parser.add_argument(
        '--model', 
        default='gpt-3.5-turbo',
        help='OpenAI model to use (default: gpt-3.5-turbo)'
    )
    args = parser.parse_args()

    client = setup_openai()
    diff_text = get_git_diff()
    
    if diff_text:
        commit_message = summarize_with_openai(client, diff_text, model=args.model)
        if commit_message:
            print("\nSuggested commit message:")
            print("-" * 40)
            print(commit_message)
            print("-" * 40)
            
            response = input("\nUse this message for commit? [y/N]: ").lower()
            if response == 'y':
                try:
                    subprocess.run(['git', 'commit', '-m', commit_message], 
                                 check=True)
                    print("Changes committed successfully!")
                except subprocess.CalledProcessError:
                    print("Error: Failed to commit changes")
        else:
            print("Failed to generate commit message using OpenAI API.")
    else:
        print("No changes to summarize.")

if __name__ == "__main__":
    main()



