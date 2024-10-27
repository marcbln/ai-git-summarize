# git_summarize/cli.py
import subprocess
import os
import sys
import argparse
import json
from openai import OpenAI
from .prompt_builder import PromptBuilder

def setup_openai(model: str):
    print(f"\nSetting up client for model: {model}")
    if model.startswith("openrouter/"):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("Error: OPENROUTER_API_KEY environment variable is not set")
            sys.exit(1)
        print("Using OpenRouter API endpoint with base url https://openrouter.ai/api/v1")
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Error: OPENAI_API_KEY environment variable is not set")
            sys.exit(1)
        print("Using OpenAI API endpoint")
        return OpenAI(api_key=api_key)

def get_git_diff():
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

def summarize_with_openai(client, diff_text, model="gpt-3.5-turbo"):
    print(f"\nGenerating summary using model: {model}")
    try:
        messages = PromptBuilder.build_diff_prompt(diff_text)
        print(f"Generated prompt with {len(messages)} messages")
        
        # Add OpenRouter specific headers if using OpenRouter
        if model.startswith("openrouter/"):
            # Remove the "openrouter/" prefix for the actual API call
            actual_model = model.replace("openrouter/", "", 1)
            print(f"Using OpenRouter with model: {actual_model}")
            kwargs = {
                "extra_headers": {
                    "X-Title": "ai-git-summarize",
                },
                "model": actual_model,
                "messages": messages,
            }
            print("Using OpenRouter configuration:")
            print(json.dumps(kwargs, indent=2))
        else:
            kwargs = {
                "model": model,
                "messages": messages,
                "max_tokens": 100
            }
            print("Using OpenAI configuration:")
            print(json.dumps(kwargs, indent=2))
            
        print("\nSending API request...")
        response = client.chat.completions.create(**kwargs)
        print("Successfully received API response")
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"\nError when calling API: {type(e).__name__} - {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response details: {e.response}")
        return None

def main():
    parser = argparse.ArgumentParser(
        description='Generate commit messages from git diff using AI'
    )
    parser.add_argument(
        '--model', 
        default='gpt-3.5-turbo',
        help='Model to use (default: gpt-3.5-turbo, for OpenRouter prefix with "openrouter/")'
    )
    args = parser.parse_args()

    print(f"\nStarting git-summarize with model: {args.model}")
    client = setup_openai(args.model)
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
                    print("\nCommitting changes...")
                    subprocess.run(['git', 'commit', '-m', commit_message], 
                                 check=True)
                    print("Changes committed successfully!")
                except subprocess.CalledProcessError as e:
                    print(f"Error: Failed to commit changes. Command output: {e.stderr}")
        else:
            print("Failed to generate commit message using API.")
    else:
        print("No changes to summarize.")

if __name__ == "__main__":
    main()
