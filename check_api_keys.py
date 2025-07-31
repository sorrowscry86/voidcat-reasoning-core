#!/usr/bin/env python3
"""
Check API keys and environment setup - diagnosing the cosmic energy flow! 🔍
"""

import os
from dotenv import load_dotenv

def check_api_keys():
    """Check which API keys are available."""
    print("🔍 Checking API Key Configuration")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check each API key
    keys_to_check = [
        ("OPENAI_API_KEY", "OpenAI"),
        ("DEEPSEEK_API_KEY", "DeepSeek"),
        ("OPENROUTER_API_KEY", "OpenRouter")
    ]
    
    available_keys = []
    
    for env_var, provider in keys_to_check:
        key = os.getenv(env_var)
        if key and key != "your_openai_api_key_here":
            print(f"✅ {provider}: Key configured")
            available_keys.append(provider)
        else:
            print(f"❌ {provider}: Not set or using placeholder")
    
    print(f"\n📊 Summary: {len(available_keys)} out of {len(keys_to_check)} providers configured")
    
    if not available_keys:
        print("\n⚠️  No valid API keys found!")
        print("   Please set at least one API key in your .env file:")
        print("   - Copy .env.example to .env")
        print("   - Add your actual API keys")
        print("   - Make sure they're not placeholder values")
    else:
        print(f"\n🎉 Ready to test with: {', '.join(available_keys)}")
    
    return available_keys

if __name__ == "__main__":
    check_api_keys()