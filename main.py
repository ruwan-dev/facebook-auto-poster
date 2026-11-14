#!/usr/bin/env python3
"""
Facebook Auto-Posting System in Sinhala
Author: Senior Software Architect & Python Developer
Description:
    Generates a daily trending tech post in Sinhala using the Google Gemini API (Free Tier)
    and automatically publishes it to a Facebook Page via Facebook Graph API.
"""

from datetime import datetime, timezone
import os
import sys
import re
import socket
import random
import logging
from typing import Dict, Any, Optional
import requests
import urllib3.util.connection as urllib_conn
import google.generativeai as genai

# Ensure IPv4 compatibility across all ISP environments (e.g. SLT / Dialog IPv6 routing stalls)
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
    """
    Validate and return required environment variables.
    Exits application if any required secret is missing.
    """
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
            "Please check your environment or GitHub Secrets.",
            ", ".join(missing_keys)
        )
        sys.exit(1)

    return config


def get_daily_theme() -> str:
    """
    Returns a thematic technology focus based on the current day of the week
    to ensure high diversity and fresh content every single day.
    """
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


def get_thematic_image() -> str:
    """
    Returns a thematic, high-resolution royalty-free technology image URL
    based on the current day of the week to accompany the post.
    """
    weekday = datetime.now(timezone.utc).weekday()
    theme_images = {
        0: [  # Monday: AI & Machine Learning
            "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1200&auto=format&fit=crop&q=80",
        ],
        1: [  # Tuesday: Cybersecurity & Privacy
            "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1200&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1200&auto=format&fit=crop&q=80",
        ],
        2: [  # Wednesday: Smart Gadgets & Mobile Tech
            "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1200&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=1200&auto=format&fit=crop&q=80",
        ],
        3: [  # Thursday: Cloud Computing & Software
            "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1200&auto=format&fit=crop&q=80",
        ],
        4: [  # Friday: Future Tech & Robotics
            "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1200&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200&auto=format&fit=crop&q=80",
        ],
        5: [  # Saturday: Productivity & Tech Tools
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1200&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&auto=format&fit=crop&q=80",
        ],
        6: [  # Sunday: Startups, Economy & Innovation
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&auto=format&fit=crop&q=80",
            "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&auto=format&fit=crop&q=80",
        ]
    }
    image_list = theme_images.get(weekday, theme_images[0])
    return random.choice(image_list)


SYSTEM_PROMPT = """You are 'LucidDreamsBot', an expert Sri Lankan Tech Content Creator. 
Your job is to automatically write highly engaging tech Facebook posts based on the topics provided to you. 
Whenever you generate a post, you MUST strictly obey the following absolute rules:

1. CORE LANGUAGE & TONE: Write the post entirely in natural, everyday conversational Sinhala script. Write exactly how a Sri Lankan would speak to a friend. Do not use formal, robotic translated language.
2. ZERO FOREIGN CHARACTERS (CRITICAL): You are STRICTLY FORBIDDEN from using Hindi, Tamil, or any other foreign language characters. The output must contain ONLY Sinhala characters (and the limited English words allowed below).
3. ENGLISH WORD LIMIT (STRICT): You are allowed a MAXIMUM of 5 English words in the entire post. Use them ONLY for unavoidable technical terms or specific App names. 
4. NO ENGLISH IN BRACKETS: Never translate or explain Sinhala words by putting English words inside brackets (e.g., do NOT write "දත්ත (Data)"). If a technical term is needed, just transliterate it in Sinhala script.
5. FORMATTING & STRUCTURE: No long paragraphs. Use short sentences and bullet points. Use 3 to 5 relevant emojis. You MUST include clear, actionable instructions formatted as 'පියවර 1:', 'පියවර 2:', etc.
6. CALL TO ACTION (CTA): End every post with a specific, engaging question related to the topic.
7. IMAGE GENERATION PROMPT: At the very end of your response, provide an English image generation prompt enclosed in [IMAGE_PROMPT: ...]. The image MUST perfectly and logically match the EXACT context of the post."""


def generate_sinhala_post(api_key: str) -> str:
    """
    Generate an engaging daily technology trend post in Sinhala using Gemini API
    following the strict LucidDreamsBot rules.
    """
    logger.info("Initializing Google Gemini API client...")
    try:
        genai.configure(api_key=api_key)
        
        todays_theme = get_daily_theme()
        logger.info("Today's technology focus theme: %s", todays_theme)

        # Active Free-Tier High Efficiency Models with fallback and system_instruction
        model_names = ["gemini-flash-lite-latest", "gemini-flash-latest"]
        model = None
        for name in model_names:
            try:
                model = genai.GenerativeModel(
                    model_name=name,
                    system_instruction=SYSTEM_PROMPT
                )
                break
            except Exception:
                continue

        if not model:
            model = genai.GenerativeModel(
                model_name="gemini-flash-lite-latest",
                system_instruction=SYSTEM_PROMPT
            )

        user_prompt = f"Write an engaging tech Facebook post on today's focus topic: {todays_theme}."

        logger.info("Requesting post generation from Gemini with strict LucidDreamsBot system instruction...")
        response = model.generate_content(
            user_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1000,
            )
        )

        if not response or not response.text:
            raise ValueError("Gemini returned an empty response.")

        raw_post_content = response.text.strip()
        logger.info("Successfully generated raw post content (%d characters).", len(raw_post_content))

        # Extract and log the image generation prompt if present
        image_prompt_match = re.search(r"\[IMAGE_PROMPT:\s*(.*?)\]", raw_post_content, re.DOTALL)
        if image_prompt_match:
            extracted_image_prompt = image_prompt_match.group(1).strip()
            logger.info("Extracted Image Prompt: %s", extracted_image_prompt)
            # Remove [IMAGE_PROMPT: ...] tag from Facebook post caption to keep the public post clean
            post_content = re.sub(r"\[IMAGE_PROMPT:\s*.*?\]", "", raw_post_content).strip()
        else:
            post_content = raw_post_content

        return post_content

    except Exception as exc:
        logger.error("Failed to generate content with Gemini API: %s", exc, exc_info=True)
        raise


def publish_to_facebook(
    page_id: str, 
    access_token: str, 
    message: str, 
    image_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Publish a post to a Facebook Page via Facebook Graph API v21.0.
    If image_url is provided, publishes as a high-engagement photo post.
    Falls back gracefully to a standard text feed post if photo publishing encounters an error.
    """
    if image_url:
        logger.info("Attempting to publish photo post with image: %s", image_url)
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
    logger.info("Publishing standard text post to Facebook Page ID: %s...", page_id)
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
        logger.error("Facebook Graph API error [Code %s]: %s (HTTP Status: %d)", error_code, error_msg, response.status_code)
        response.raise_for_status()
        return res_data

    except requests.exceptions.RequestException as req_err:
        logger.error("Network or HTTP request error while communicating with Facebook API: %s", req_err)
        raise


def main() -> None:
    """
    Main orchestration function.
    """
    logger.info("=== Starting Facebook Daily Auto-Post Workflow ===")
    try:
        config = load_config()
        post_content = generate_sinhala_post(api_key=config["GEMINI_API_KEY"])
        image_url = get_thematic_image()
        publish_to_facebook(
            page_id=config["FB_PAGE_ID"],
            access_token=config["FB_ACCESS_TOKEN"],
            message=post_content,
            image_url=image_url
        )
        logger.info("=== Auto-Post Workflow Completed Successfully ===")
    except Exception as exc:
        logger.critical("Auto-post execution failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()

