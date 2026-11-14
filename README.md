# 🚀 100% Free Daily Facebook Auto-Posting System (Sinhala Tech Trends)

An automated serverless pipeline powered by **Google Gemini API (Free Tier)**, **Pollinations AI**, **Facebook Graph API**, and **GitHub Actions** to create, illustrate, and publish daily Sinhala technology posts to a Facebook Page.

### 🌐 Live Web Dashboard
View all published posts, AI generated visuals, and automation statistics:
👉 **[https://ruwan-dev.github.io/facebook-auto-poster/](https://ruwan-dev.github.io/facebook-auto-poster/)**

---

## 📁 Project Structure

```text
C:\Users\RuwanPathirana\Desktop\OV\facebook-auto-poster\
├── .github/
│   └── workflows/
│       └── auto_post.yml       # GitHub Actions workflow (runs daily at 2:30 AM UTC)
├── docs/                       # 🌟 GitHub Pages Live Dashboard
│   ├── index.html              # Modern glassmorphism web dashboard UI
│   └── posts.json              # Automated publication history and metadata
├── main.py                     # Python orchestrator (Gemini AI + Pollinations + FB API)
├── requirements.txt            # Python dependencies
├── test_credentials.py         # Diagnostic test script
├── .env.example                # Template for local testing
└── .gitignore                  # Keeps secrets out of version control
```

---

## 🔑 Credentials Setup

### 1. Google Gemini API Key (100% Free)
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google Account and click **"Get API key"**.
3. Create a new API key and copy it (`GEMINI_API_KEY`).

### 2. Facebook Page ID & Access Token
1. **Find your Page ID**:
   - Go to your Facebook Page > **About** > **Page Transparency** (or copy from the URL/Settings).
2. **Generate a Never-Expiring Page Access Token**:
   - Go to [Meta for Developers](https://developers.facebook.com/) and create a Business App.
   - Under **Graph API Explorer**:
     - Select your App and Page.
     - Add the following permissions:
       - `pages_manage_posts`
       - `pages_read_engagement`
       - `pages_show_list`
     - Generate an User Token, then exchange it for a **Long-Lived Page Access Token** using Meta's Access Token Tool.

---

## 🔒 GitHub Secrets Configuration

Once you push this project to a GitHub repository:
1. Open your repository on GitHub.
2. Go to **Settings** > **Secrets and variables** > **Actions**.
3. Click **"New repository secret"** and add these three secrets:
   - `GEMINI_API_KEY`: Your Gemini API Key from Google AI Studio.
   - `FB_PAGE_ID`: Your numerical Facebook Page ID.
   - `FB_ACCESS_TOKEN`: Your Facebook Page Access Token.

---

## ⏰ Automated Schedule & Content Rotation

The GitHub Actions workflow runs every day at **02:30 AM UTC** (**08:00 AM Sri Lanka Time**):
- **Schedule Cron**: `'30 2 * * *'`
- **Manual Trigger**: Go to the **Actions** tab in your GitHub repository, select **"Daily Facebook Auto-Post"**, and click **"Run workflow"** to trigger a post anytime.

### 🎨 Daily Thematic Photography & Topics
Each day of the week automatically rotates themes and pairs with curated high-resolution photography:
- **Monday**: Artificial Intelligence & Machine Learning Innovations
- **Tuesday**: Cybersecurity, Online Privacy & Scam Awareness
- **Wednesday**: Smartphones, Wearables & Smart Consumer Gadgets
- **Thursday**: Cloud Computing & Software Engineering
- **Friday**: Future Tech, Robotics, EVs & Green Tech
- **Saturday**: Productivity Apps, Digital Tools & Life Hacks
- **Sunday**: Tech Startups, Digital Economy & Innovation

If image hosting is ever unreachable, the system automatically falls back to publishing a standard text post so your schedule is never interrupted.

---

## 💻 Local Testing & Setup

1. Open a terminal and enter the project folder:
   ```bash
   cd C:\Users\RuwanPathirana\Desktop\OV\facebook-auto-poster
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
4. Fill in your credentials in `.env`.
5. Run the non-destructive diagnostic check:
   ```bash
   python test_credentials.py
   ```
6. Run the auto-poster to publish a post:
   ```bash
   python main.py
   ```

