#!/usr/bin/env python3
"""
Test script for model alias resolution.
This script tests the resolve_model_alias function with various inputs.
"""

from ai_git.config_utils import resolve_model_alias

def test_model_alias_resolution():
    """Test the model alias resolution with various inputs."""
    # Test cases: (input, expected_output)
    test_cases = [
        # Full identifiers (should remain unchanged)
        ("openai/gpt-4", "openai/gpt-4"),
        ("openrouter/anthropic/claude-3.5-sonnet", "openrouter/anthropic/claude-3.5-sonnet"),
        
        # Aliases from config
        ("claude35", "openrouter/anthropic/claude-3.5-sonnet"),
        ("geminiflash20-free", "openrouter/google/gemini-2.0-flash-exp:free"),
        ("gpt4o", "openai/gpt-4o-2024-05-13"),
        
        # Unknown alias (should remain unchanged)
        ("unknown-model", "unknown-model"),
    ]
    
    # Run tests
    print("Testing model alias resolution:")
    print("-" * 50)
    
    for i, (input_model, expected) in enumerate(test_cases, 1):
        result = resolve_model_alias(input_model)
        success = result == expected
        
        print(f"Test {i}: '{input_model}' -> '{result}'")
        if not success:
            print(f"  FAILED! Expected: '{expected}'")
        
        # Add a blank line for readability
        if i < len(test_cases):
            print()
    
    print("-" * 50)
    print("Test completed.")

if __name__ == "__main__":
    test_model_alias_resolution()