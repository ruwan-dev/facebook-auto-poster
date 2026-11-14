# 🚀 100% Free Daily Facebook Auto-Posting System (Sinhala Tech Trends)

An automated serverless pipeline powered by **Google Gemini API (Free Tier)**, **Facebook Graph API**, and **GitHub Actions** (free monthly CI/CD quota) to create and publish daily Sinhala technology posts to a Facebook Page.

---

## 📁 Project Structure

```text
C:\Users\RuwanPathirana\Desktop\OV\facebook-auto-poster\
├── .github/
│   └── workflows/
│       └── auto_post.yml       # GitHub Actions workflow (runs daily at 2:30 AM UTC)
├── main.py                     # Python orchestrator (Gemini AI + FB Graph API)
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

## ⏰ Automated Schedule

The GitHub Actions workflow runs every day at **02:30 AM UTC** (**08:00 AM Sri Lanka Time**):
- **Schedule Cron**: `'30 2 * * *'`
- **Manual Trigger**: Go to the **Actions** tab in your GitHub repository, select **"Daily Facebook Auto-Post"**, and click **"Run workflow"** to trigger a test post anytime.

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

