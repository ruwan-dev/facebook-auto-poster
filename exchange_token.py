#!/usr/bin/env python3
"""
Token Exchange Helper
Automates the conversion of a short-lived user token into a permanent (never-expiring) Facebook Page Access Token.
"""

import sys
import requests

def exchange_token(app_id: str, app_secret: str, short_lived_token: str):
    print("\n🔄 [Step 1/2] Exchanging short-lived user token for 60-day extended user token...")
    exchange_url = "https://graph.facebook.com/v21.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id.strip(),
        "client_secret": app_secret.strip(),
        "fb_exchange_token": short_lived_token.strip()
    }
    
    try:
        res = requests.get(exchange_url, params=params, timeout=15)
        data = res.json()
        
        if res.status_code != 200 or "access_token" not in data:
            print(f"❌ Failed to exchange user token: {data.get('error', {}).get('message', 'Unknown error')}")
            return
        
        long_lived_user_token = data["access_token"]
        print("✅ 60-day User Token successfully acquired!")
        
        print("\n🔄 [Step 2/2] Fetching never-expiring Page Access Token(s)...")
        accounts_url = "https://graph.facebook.com/v21.0/me/accounts"
        accounts_res = requests.get(
            accounts_url,
            params={"access_token": long_lived_user_token},
            timeout=15
        )
        accounts_data = accounts_res.json()
        
        pages = accounts_data.get("data", [])
        if not pages:
            print("⚠️ No Facebook Pages found associated with this account or permissions are missing.")
            return

        print(f"\n🎉 Successfully found {len(pages)} Page(s):\n" + "="*60)
        for idx, page in enumerate(pages, 1):
            print(f"[{idx}] Page Name: {page.get('name')}")
            print(f"    Page ID:   {page.get('id')}")
            print(f"    Permanent FB_ACCESS_TOKEN:\n    {page.get('access_token')}\n")
        print("="*60)
        print("💡 Copy the Page ID and the permanent FB_ACCESS_TOKEN into your .env and GitHub Secrets!")

    except Exception as exc:
        print(f"❌ Error during token exchange: {exc}")

if __name__ == "__main__":
    print("=== Facebook Permanent Page Access Token Generator ===")
    app_id = input("Enter Meta App ID: ").strip()
    app_secret = input("Enter Meta App Secret: ").strip()
    short_token = input("Enter Short-Lived User Token (from Graph API Explorer): ").strip()
    
    if not all([app_id, app_secret, short_token]):
        print("❌ All three values are required.")
        sys.exit(1)
        
    exchange_token(app_id, app_secret, short_token)
