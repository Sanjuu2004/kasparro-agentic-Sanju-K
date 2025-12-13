#!/usr/bin/env python3
"""
Test which OpenAI models you have access to
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_models():
    """Test available models"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Models to test (most common)
    models = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo-preview",
        "gpt-4-turbo",
        "gpt-4-32k",
        "gpt-4o",
        "gpt-4o-mini"
    ]
    
    print("Testing model access...")
    print("="*50)
    
    accessible_models = []
    
    for model in models:
        try:
            print(f"Testing {model:20}... ", end="")
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            if response.choices[0].message.content:
                print("✅ ACCESSIBLE")
                accessible_models.append(model)
            else:
                print("❌ NO RESPONSE")
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg or "not have access" in error_msg:
                print("❌ NO ACCESS")
            elif "rate limit" in error_msg.lower():
                print("⚠️  RATE LIMITED")
            else:
                print(f"❌ ERROR: {error_msg[:50]}...")
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print(f"Total models tested: {len(models)}")
    print(f"Models you can access: {len(accessible_models)}")
    
    if accessible_models:
        print("\n✅ You can use these models:")
        for model in accessible_models:
            print(f"  • {model}")
        
        # Recommend best model
        if "gpt-4-turbo-preview" in accessible_models:
            recommended = "gpt-4-turbo-preview"
        elif "gpt-4" in accessible_models:
            recommended = "gpt-4"
        elif "gpt-4o" in accessible_models:
            recommended = "gpt-4o"
        else:
            recommended = "gpt-3.5-turbo"
        
        print(f"\n💡 Recommended model: {recommended}")
        print(f"\nUpdate your .env file with:")
        print(f'MODEL_NAME={recommended}')
    else:
        print("\n❌ No models accessible. Check your:")
        print("  1. OpenAI API key")
        print("  2. Account billing/credits")
        print("  3. Model access permissions")

if __name__ == "__main__":
    test_models()