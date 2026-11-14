#!/usr/bin/env python3
"""
Credentials & Connectivity Diagnostic Script
Tests Gemini API and Facebook Page permissions.
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
    print(f"\n🔍 [2/2] Inspecting Facebook Page (ID: {page_id}) Permissions...")
    try:
        url = f"https://graph.facebook.com/v21.0/{page_id}"
        params = {
            "fields": "id,name,can_post",
            "access_token": access_token
        }
        res = requests.get(url, params=params, timeout=15)
        data = res.json()

        if res.status_code == 200 and "id" in data:
            page_name = data.get("name")
            can_post = data.get("can_post", False)
            print(f"✅ Facebook Graph API connected successfully!")
            print(f"   Page Name: {page_name}")
            print(f"   Page ID:   {data.get('id')}")
            print(f"   Can Post:  {'YES (Authorized)' if can_post else 'NO'}")
            
            if can_post:
                print("🎉 Facebook Token is 100% verified and authorized to publish posts!")
                return True
            else:
                print("⚠️ Token is connected but 'can_post' is false. Please ensure pages_manage_posts is granted.")
                return False
        else:
            err = data.get("error", {})
            print(f"❌ Facebook API Error: {err.get('message')} (Code: {err.get('code')})")
            return False

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
        print("\n🎉 ALL CHECKS PASSED! Your auto-poster is fully operational.")
    else:
        print("\n⚠️  Please review the diagnostic messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
