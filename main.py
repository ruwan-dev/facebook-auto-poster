#!/usr/bin/env python3
"""
Facebook Auto-Posting System in Sinhala (With Free AI Image Generation)
Author: Senior Software Architect & Python Developer
Description:
    Generates a daily trending tech post in Sinhala using the Google Gemini API (Free Tier),
    generates a matching AI Image dynamically, and automatically publishes it to a Facebook Page.
"""

from datetime import datetime, timezone
import os
import sys
import json
import socket
import random
import logging
import re
import urllib.parse
from typing import Dict, Any, Optional, Tuple
import requests
import urllib3.util.connection as urllib_conn
import google.generativeai as genai

# Ensure IPv4 compatibility across all ISP environments
urllib_conn.allowed_gai_family = lambda: socket.AF_INET

# Load local environment variables if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("FacebookAutoPoster")


def load_config() -> Dict[str, str]:
    required_keys = ["GEMINI_API_KEY", "FB_PAGE_ID", "FB_ACCESS_TOKEN"]
    config = {}
    missing_keys = []

    for key in required_keys:
        value = os.getenv(key)
        if not value or not value.strip():
            missing_keys.append(key)
        else:
            config[key] = value.strip()

    if missing_keys:
        logger.critical(
            "Missing required environment variables: %s. "
            "Please check your .env file or GitHub Secrets.",
            ", ".join(missing_keys)
        )
        sys.exit(1)

    return config


def get_daily_theme() -> str:
    themes = {
        0: "Artificial Intelligence (AI), Generative AI, and Machine Learning innovations",
        1: "Cybersecurity, Online Privacy, Scam awareness, and Data Protection",
        2: "Smartphones, Wearables, IoT devices, and Consumer Gadgets",
        3: "Cloud Computing, Web Development, and Software Engineering breakthroughs",
        4: "Future Tech, Robotics, Electric Vehicles (EV), and Renewable Tech",
        5: "Productivity Apps, Useful Tools, and Tech Tips & Tricks for everyday users",
        6: "Tech Startups, Digital Economy, and Remote Tech Careers"
    }
    weekday = datetime.now(timezone.utc).weekday()
    return themes.get(weekday, "Modern Technology Trends")


def get_ai_image_url(prompt: str) -> str:
    """
    Generates a 100% free AI image based on the prompt using Pollinations.ai
    No API key required. Returns a direct image URL for Facebook to download.
    """
    logger.info("Generating AI Image URL for prompt: %s", prompt)
    
    # URL encode the prompt to safely pass it in a web link
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Add a random seed so we get a unique image every time even for similar prompts
    seed = random.randint(1, 999999)
    
    # Generate a 1200x630 (Facebook Post size) image
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1200&height=630&nologo=true&seed={seed}"
    return image_url


def generate_sinhala_post(api_key: str) -> Tuple[str, str]:
    """
    Generates the Sinhala post content and extracts the Image Prompt.
    Returns: (Clean Post Content, Image Generation Prompt)
    """
    logger.info("Initializing Google Gemini API client...")
    try:
        genai.configure(api_key=api_key)
        
        # Free-tier high efficiency models (prioritizing active gemini-flash-lite-latest)
        model_names = ["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-1.5-flash"]
        model = None
        for name in model_names:
            try:
                model = genai.GenerativeModel(model_name=name)
                break
            except Exception:
                continue

        if not model:
            model = genai.GenerativeModel(model_name="gemini-flash-lite-latest")

        todays_theme = get_daily_theme()
        logger.info("Today's technology focus theme: %s", todays_theme)

        # STRICT SYSTEM RULES
        system_prompt = (
            "You are 'LucidDreamsBot', an expert Sri Lankan Tech Content Creator. "
            "Your job is to automatically write highly engaging tech Facebook posts. "
            "You MUST strictly obey these absolute rules:\n"
            "1. CORE LANGUAGE & TONE: Write entirely in natural, conversational Sinhala script. Write exactly how a Sri Lankan would speak to a friend.\n"
            "2. ZERO FOREIGN CHARACTERS: STRICTLY NO Hindi, Tamil, or any other foreign language characters. ONLY Sinhala characters.\n"
            "3. ENGLISH WORD LIMIT: MAXIMUM of 5 English words in the entire post (only for unavoidable tech terms/app names).\n"
            "4. NO ENGLISH IN BRACKETS: Never translate or explain Sinhala words by putting English words inside brackets (e.g., do NOT write 'දත්ත (Data)'). Transliterate in Sinhala script instead.\n"
            "5. FORMATTING & STRUCTURE: No long paragraphs. Use short sentences, bullet points, and 3-5 emojis. DO NOT use markdown formatting like **bold** or *italic*.\n"
            "6. ACTIONABLE STEPS: If explaining a tech trick, you MUST include clear, step-by-step instructions (e.g., 'පියවර 1:', 'පියවර 2:').\n"
            "7. CTA: End every post with a specific engaging question related to the topic to drive comments.\n"
            "8. IMAGE GENERATION PROMPT (CRITICAL): At the very end of your response, on a new line, provide an English image generation prompt enclosed in exactly these tags: [IMAGE_PROMPT: ...]. The image must perfectly and logically match the EXACT context of the post. It should be highly detailed, cinematic, and high-quality."
        )

        user_prompt = (
            f"Write a compelling and viral Facebook post in Sinhala about an exciting, recent topic "
            f"under this category: {todays_theme}.\n\n"
            "Requirements for the post:\n"
            "1. An attention-grabbing Sinhala headline with emojis.\n"
            "2. A clear explanation with step-by-step instructions (if applicable).\n"
            "3. Why this matters to Sri Lankan tech enthusiasts.\n"
            "4. 5-7 popular hashtags (e.g., #TechNews #SinhalaTech #Technology #SriLanka).\n"
            "Return ONLY the post text and the [IMAGE_PROMPT: ...] tag at the end."
        )

        logger.info("Requesting post generation from Gemini...")
        response = model.generate_content(
            f"{system_prompt}\n\n{user_prompt}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1000,
            )
        )

        if not response or not response.text:
            raise ValueError("Gemini returned an empty response.")

        raw_content = response.text.strip()
        
        # Parse the [IMAGE_PROMPT: ...] out of the text
        image_prompt_match = re.search(r'\[IMAGE_PROMPT:\s*(.*?)\]', raw_content, re.IGNORECASE | re.DOTALL)
        
        if image_prompt_match:
            image_prompt = image_prompt_match.group(1).strip()
            # Remove the prompt block from the final Facebook post text
            clean_post_content = re.sub(r'\[IMAGE_PROMPT:\s*.*?\]', '', raw_content, flags=re.IGNORECASE | re.DOTALL).strip()
        else:
            # Fallback if Gemini forgets the tag
            image_prompt = f"High quality cinematic tech concept image representing {todays_theme}, 8k resolution, modern"
            clean_post_content = raw_content

        # Sanitizer: Enforce Zero Foreign Characters (strips accidental non-Sinhala Indic/Asian script tokens)
        clean_post_content = re.sub(r'[\u0900-\u0D7F\u0E00-\u0FFF]', '', clean_post_content)

        logger.info("Successfully generated post and extracted image prompt.")
        return clean_post_content, image_prompt

    except Exception as exc:
        logger.error("Failed to generate content with Gemini API: %s", exc, exc_info=True)
        raise


def publish_to_facebook(
    page_id: str, 
    access_token: str, 
    message: str, 
    image_url: Optional[str] = None
) -> Dict[str, Any]:
    
    if image_url:
        logger.info("Attempting to publish photo post with AI image...")
        photos_endpoint = f"https://graph.facebook.com/v21.0/{page_id}/photos"
        payload = {
            "url": image_url,
            "caption": message,
            "access_token": access_token
        }
        try:
            response = requests.post(photos_endpoint, data=payload, timeout=40)
            res_data = response.json()
            if response.status_code == 200 and "id" in res_data:
                post_id = res_data.get("post_id", res_data["id"])
                logger.info("Photo post published successfully! Facebook Post ID: %s", post_id)
                return res_data
            else:
                err_msg = res_data.get("error", {}).get("message", "Unknown error")
                err_code = res_data.get("error", {}).get("code", "N/A")
                logger.warning(
                    "Photo post failed [Code %s]: %s. Falling back to standard text post...",
                    err_code, err_msg
                )
        except Exception as photo_err:
            logger.warning("Error uploading photo (%s). Falling back to standard text post...", photo_err)

    # Standard feed post fallback
    feed_endpoint = f"https://graph.facebook.com/v21.0/{page_id}/feed"
    payload = {
        "message": message,
        "access_token": access_token
    }
    logger.info("Publishing standard text post to Facebook...")
    try:
        response = requests.post(feed_endpoint, data=payload, timeout=30)
        res_data = response.json()

        if response.status_code == 200 and "id" in res_data:
            post_id = res_data["id"]
            logger.info("Text post published successfully! Facebook Post ID: %s", post_id)
            return res_data

        error_info = res_data.get("error", {})
        error_msg = error_info.get("message", "Unknown error")
        error_code = error_info.get("code", "N/A")
        logger.error("Facebook Graph API error [Code %s]: %s", error_code, error_msg)
        response.raise_for_status()
        return res_data

    except requests.exceptions.RequestException as req_err:
        logger.error("Network error while communicating with Facebook API: %s", req_err)
        raise


def log_post_to_dashboard(
    post_id: str,
    content: str,
    theme: str,
    image_url: Optional[str] = None,
    image_prompt: Optional[str] = None
) -> None:
    """
    Appends the published post to docs/posts.json for the GitHub Pages dashboard.
    """
    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
    os.makedirs(docs_dir, exist_ok=True)
    posts_file = os.path.join(docs_dir, "posts.json")

    posts = []
    if os.path.exists(posts_file):
        try:
            with open(posts_file, "r", encoding="utf-8") as f:
                posts = json.load(f)
        except Exception as e:
            logger.warning("Could not read existing posts.json (%s), creating fresh list.", e)
            posts = []

    # Check if post_id already exists to prevent duplicates
    if any(p.get("id") == post_id for p in posts):
        logger.info("Post %s already logged in posts.json.", post_id)
        return

    now_iso = datetime.now(timezone.utc).isoformat()
    new_entry = {
        "id": post_id,
        "timestamp": now_iso,
        "theme": theme,
        "content": content,
        "image_url": image_url or "",
        "image_prompt": image_prompt or "",
        "facebook_url": f"https://www.facebook.com/{post_id}",
        "type": "photo" if image_url else "feed",
        "status": "published"
    }

    # Prepend new post so the newest appears first on the dashboard
    posts.insert(0, new_entry)

    try:
        with open(posts_file, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=2)
        logger.info("Successfully recorded post %s to docs/posts.json for GitHub Pages Dashboard.", post_id)
    except Exception as exc:
        logger.error("Failed to write to docs/posts.json: %s", exc)


def main() -> None:
    logger.info("=== Starting Facebook Daily Auto-Post Workflow ===")
    try:
        config = load_config()
        
        # 1. Get the Sinhala post text AND the English Image Prompt from Gemini
        post_content, image_prompt = generate_sinhala_post(api_key=config["GEMINI_API_KEY"])
        
        # 2. Generate a 100% matching AI image URL for free
        ai_image_url = get_ai_image_url(image_prompt)
        
        # 3. Publish both to Facebook
        fb_response = publish_to_facebook(
            page_id=config["FB_PAGE_ID"],
            access_token=config["FB_ACCESS_TOKEN"],
            message=post_content,
            image_url=ai_image_url
        )

        # 4. Record to GitHub Pages Dashboard
        post_id = fb_response.get("post_id", fb_response.get("id", "N/A"))
        todays_theme = get_daily_theme()
        log_post_to_dashboard(
            post_id=post_id,
            content=post_content,
            theme=todays_theme,
            image_url=ai_image_url,
            image_prompt=image_prompt
        )

        logger.info("=== Auto-Post Workflow Completed Successfully ===")
    except Exception as exc:
        logger.critical("Auto-post execution failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
