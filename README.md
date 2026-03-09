# Dua Reminder Bot (Telegram)

This project creates a Telegram chatbot that:

- sends a daily dua reminder (for waking up)
- replies with going-out dua when you type `/out`
- can send a random dua with `/dua`

## 1) Create your Telegram bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name and username
4. Copy the bot token

## 2) Install dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3) Configure environment

Copy `.env.example` to `.env` and fill values:

```powershell
Copy-Item .env.example .env
```

- `TELEGRAM_BOT_TOKEN`: from BotFather
- `TIMEZONE`: your timezone (example: `Europe/Berlin`)
- `MORNING_DUA_TIME`: daily reminder time in `HH:MM` (24-hour), example `07:00`

`TARGET_CHAT_ID` is optional. If empty, the bot auto-saves the chat id when you send `/start`.

## 4) Run

```powershell
python bot.py
```

Then in Telegram:

1. Open your bot
2. Send `/start`
3. Try `/out`

## Commands

- `/start` - register your chat and show welcome message
- `/out` - dua for leaving home
- `/dua` - random dua
- `/help` - command list

## Notes for WhatsApp

Telegram is easiest to start. WhatsApp automation usually needs the WhatsApp Business API provider (like Twilio or Meta Cloud API), webhook hosting, and message templates for proactive messages.

If you want, next step we can build a WhatsApp version using Twilio with the same dua logic.
