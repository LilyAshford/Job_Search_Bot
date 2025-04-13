 <h2>🔍 JobHunter Pro - The Slightly Illegal Job Stalker Bot</h2>

Because manually checking job boards is *so* 2010.


*(Actual footage of our bot out-hustling you in the job market)*

## 🔍 What's This?

A Telegram bot that scours HH.ru and LinkedIn for jobs while you binge-watch Netflix. It's like having a personal recruiter, but one that actually works 24/7 and doesn't ghost you.

⚡ Features

- **HH.ru + LinkedIn scraping** - Like a digital bloodhound for jobs
- **Telegram interface** - Because CLI is for masochists
- **SQLite/PostgreSQL support** - Your data won't disappear like my will to live
- **Configurable searches** - "Blockchain expert with 10 years experience" → *laughs in bot*
- **Pretends to be human on LinkedIn** (shhh...)

## 🛠️ Installation - For When You're Done Procrastinating

```bash
# Clone the repo (if you can find your terminal)
git clone https://github.com/LilyAshford/Job_Search_Bot.git
cd jobhunter-pro

# Install dependencies (a.k.a. magic spells)
pip install -r requirements.txt

# Configure the bot (the adulting part)
cp config.py config.py # Then edit like your life depends on it
```

## ⚙️ Configuration

Edit `config.py` with your darkest secrets:

```python
# Telegram
TELEGRAM_TOKEN = "YOUR_TOKEN_HERE" # Get from @BotFather

# LinkedIn Creds (because bots need social media too)
LINKEDIN_EMAIL = "your_email@example.com"
LINKEDIN_PASSWORD = "hunter2" # Pro tip: Actually change this

# Database (SQLite by default because we're lazy)
DATABASE_URL = "sqlite:///jobs.db" # For PostgreSQL: "postgresql://user:pass@localhost/dbname"

# Default search parameters
DEFAULT_SEARCH_PARAMS = {
"keywords": ["Python"],
"locations": ["Remote"],
"salary_min": 50000, # In rubles, because we fancy
"experience": "noExperience" # "Senior" if you're feeling bold
}
```

## 🚦 Running the Bot

```bash
python bot.py
# Warning: May cause sudden influx of recruiter messages
```

## 🤖 Bot Commands

| Command | What It Does | Emotional Support Provided |
|---------|--------------|----------------------------|
| `/start` | Wakes the bot up | ☕ "I'm here!" |
| `/help` | Explains things you'll ignore | 📖 *Patience not included* |
| `/settings` | Lets you pretend you're picky | ⚙️ "Remote work only, eh?" |
| `/search` | Actually does the work | 🔍 "Hold my beer..." |

## 🧰 Tech Stack

- **Selenium** - For convincing LinkedIn we're human
- **SQLAlchemy** - ORM magic (it's not black magic, I swear)
- **HH.ru API** - The Russian job market's open secret
- **Telegram Bot API** - For those sweet push notifications


## Prerequisites
- Python 3.8+ (because we like modern things)
- Chrome (for LinkedIn to think we're human)
- A Telegram account (obviously)


## 🚨 Known Issues

- LinkedIn might suspect you're a bot (because you are)
- HH.ru API returns salaries in RUB (time to learn currency conversion)
- No "auto-apply" feature (we have *some* ethics)

## 🤝 Contributing

PRs welcome! (Especially if they include coffee recipes ☕)

1. Fork it (like a GitHub salad)
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Added magic'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a PR (and pray to the merge gods)

## 📜 License

MIT - Because capitalism is hard enough already

---
*Disclaimer*: No jobs were harmed in the making of this bot. Results may vary. Batteries not included. If your bot achieves sentience, please teach it to leetcode.






