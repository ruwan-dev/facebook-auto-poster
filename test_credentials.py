#!/usr/bin/env python3
"""
Credentials & Connectivity Diagnostic Script
Tests Gemini API and Facebook Page Token permissions and scopes.
"""

import os
import sys
import socket
import requests
import urllib3.util.connection as urllib_conn
import google.generativeai as genai

# Force IPv4 to prevent IPv6 DNS/TLS handshake stalls
urllib_conn.allowed_gai_family = lambda: socket.AF_INET

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def check_gemini(api_key: str) -> bool:
    print("\n🔍 [1/2] Testing Google Gemini API...")
    try:
        genai.configure(api_key=api_key, transport="rest")
        model = genai.GenerativeModel("gemini-flash-lite-latest")
        response = model.generate_content("Say hello in Sinhala in one brief sentence.")
        print("✅ Gemini API works successfully!")
        print(f"   Model Output: {response.text.strip()}")
        return True
    except Exception as exc:
        print(f"❌ Gemini API test failed: {exc}")
        return False

def check_facebook(page_id: str, access_token: str) -> bool:
    print("\n🔍 [2/2] Inspecting Facebook Page Access Token & Permissions...")
    try:
        debug_url = "https://graph.facebook.com/debug_token"
        res = requests.get(debug_url, params={"input_token": access_token, "access_token": access_token}, timeout=15)
        data = res.json().get("data", {})

        if not data.get("is_valid"):
            err = res.json().get("error", {})
            print(f"❌ Invalid Facebook Token: {err.get('message', 'Token validation failed')}")
            return False

        token_type = data.get("type", "UNKNOWN")
        app_name = data.get("application", "Unknown App")
        scopes = data.get("scopes", [])

        print(f"   App Name:    {app_name}")
        print(f"   Token Type:  {token_type}")
        print(f"   Granted:     {', '.join(scopes)}")

        required_permissions = ["pages_manage_posts", "pages_read_engagement"]
        missing = [p for p in required_permissions if p not in scopes]

        if missing:
            print(f"\n❌ Missing Required Permission(s): {', '.join(missing)}")
            print("👉 To fix this in Meta for Developers Graph API Explorer:")
            print("   1. In the 'Permissions' dropdown, add:")
            for p in missing:
                print(f"      - {p}")
            print("   2. Generate a new User Token, then select your Page to get a new Page Access Token.")
            return False

        print("✅ Facebook Token has all required permissions to auto-post!")
        return True

    except Exception as exc:
        print(f"❌ Facebook diagnostic error: {exc}")
        return False

def main():
    print("=== Facebook Auto-Post: Pre-Flight Diagnostics ===")
    gemini_key = os.getenv("GEMINI_API_KEY")
    fb_page_id = os.getenv("FB_PAGE_ID")
    fb_token = os.getenv("FB_ACCESS_TOKEN")

    missing = []
    if not gemini_key: missing.append("GEMINI_API_KEY")
    if not fb_page_id: missing.append("FB_PAGE_ID")
    if not fb_token: missing.append("FB_ACCESS_TOKEN")

    if missing:
        print(f"\n⚠️  Missing environment variable(s): {', '.join(missing)}")
        print("💡 Create a '.env' file based on '.env.example' or export them in your shell.")
        sys.exit(1)

    gemini_ok = check_gemini(gemini_key)
    fb_ok = check_facebook(fb_page_id, fb_token)

    if gemini_ok and fb_ok:
        print("\n🎉 All services are verified and operational! You are ready to deploy.")
    else:
        print("\n⚠️  Please update the highlighted credential(s) above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
