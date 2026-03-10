import json
import logging
import os
import random
from datetime import time
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from zoneinfo import ZoneInfo

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).parent
DUAS_FILE = BASE_DIR / "duas.json"
STATE_FILE = BASE_DIR / "state.json"

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TIMEZONE = os.getenv("TIMEZONE", "Europe/Berlin").strip()
MORNING_DUA_TIME = os.getenv("MORNING_DUA_TIME", "07:00").strip()
TARGET_CHAT_ID_ENV = os.getenv("TARGET_CHAT_ID", "").strip()


def load_duas() -> dict:
    with DUAS_FILE.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    with STATE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def format_dua(item: dict) -> str:
    bn = item.get("translation_bn", "")
    en = item.get("translation", "")
    meaning = bn if bn else en

    return (
        f"*{item['title']}*\n\n"
        f"{item['arabic']}\n\n"
        f"_{item['transliteration']}_\n\n"
        f"অর্থ (বাংলা): {meaning}"
    )


def get_target_chat_id() -> int | None:
    if TARGET_CHAT_ID_ENV:
        try:
            return int(TARGET_CHAT_ID_ENV)
        except ValueError:
            logger.warning("TARGET_CHAT_ID is not a valid integer")

    state = load_state()
    saved = state.get("chat_id")
    if saved is None:
        return None

    try:
        return int(saved)
    except ValueError:
        return None


def parse_hhmm(value: str) -> time:
    parts = value.split(":")
    if len(parts) != 2:
        raise ValueError("MORNING_DUA_TIME must be HH:MM")

    hour = int(parts[0])
    minute = int(parts[1])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("MORNING_DUA_TIME is out of valid range")

    return time(hour=hour, minute=minute)


def all_duas(duas: dict) -> list[dict]:
    pool: list[dict] = []
    for value in duas.values():
        if isinstance(value, list):
            pool.extend(value)
    return pool


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None:
        return

    chat_id = update.effective_chat.id
    save_state({"chat_id": chat_id})

    if update.message is not None:
        await update.message.reply_text(
            "Assalamu alaikum. আপনার দোয়া বট চালু হয়েছে।\n\n"
            "Commands:\n"
            "/out - বাইরে যাওয়ার দোয়া\n"
            "/home - বাসায় ঢোকার দোয়া\n"
            "/sleep - ঘুমানোর আগের দোয়া\n"
            "/travel - সফরের দোয়া\n"
            "/eat - খাবার শুরুর/শেষের দোয়া\n/study - পড়াশোনার দোয়া\n/parents - বাবা-মায়ের দোয়া\n/study - পড়াশোনার দোয়া\n/parents - বাবা-মায়ের দোয়া\n"
            "/dua - র‍্যান্ডম দোয়া\n"
            "/help - কমান্ড তালিকা"
        )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is not None:
        await update.message.reply_text(
            "Commands:\n"
            "/start - chat নিবন্ধন\n"
            "/out - বাইরে যাওয়ার দোয়া\n"
            "/home - বাসায় ঢোকার দোয়া\n"
            "/sleep - ঘুমানোর আগের দোয়া\n"
            "/travel - সফরের দোয়া\n"
            "/eat - খাবার শুরুর/শেষের দোয়া\n/study - পড়াশোনার দোয়া\n/parents - বাবা-মায়ের দোয়া\n/study - পড়াশোনার দোয়া\n/parents - বাবা-মায়ের দোয়া\n"
            "/dua - র‍্যান্ডম দোয়া\n"
            "/help - কমান্ড তালিকা"
        )


async def out_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    item = duas["out"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def home_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    item = duas["enter_home"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def sleep_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    item = duas["before_sleep"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def travel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    item = duas["travel"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def eat_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    start_item = duas["before_eating"][0]
    end_item = duas["after_eating"][0]
    text = f"{format_dua(start_item)}\n\n--------------------\n\n{format_dua(end_item)}"
    if update.message is not None:
        await update.message.reply_text(text, parse_mode="Markdown")


async def study_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    item = duas["study"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def parents_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    item = duas["parents"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")

async def sneeze_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    item = duas["sneeze"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def sad_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    item = duas["sad"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def patience_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    item = duas["patience"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def protection_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    item = duas["protection"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def mosque_in_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    item = duas["mosque_enter"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def mosque_out_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    item = duas["mosque_exit"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")

async def bathroom_in_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["bathroom_enter"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def bathroom_out_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["bathroom_exit"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def mirror_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["mirror"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def clothes_on_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["clothes_wear"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def clothes_off_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["clothes_remove"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def wudu_before_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["wudu_before"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def wudu_after_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["wudu_after"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def market_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["market"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def rain_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["rain"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def rain_after_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["rain_after"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def thunder_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["thunder"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def fear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["fear"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def angry_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["angry"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def evil_eye_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["evil_eye"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def good_news_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["good_news"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def debt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["debt_relief"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def strength_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["strength"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def success_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["success"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def barakah_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["barakah"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def good_ending_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["good_ending"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def new_place_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["new_place"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def moon_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["moon"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def fasting_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["fasting"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def iftar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["iftar"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def laylatul_qadr_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["laylatul_qadr"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def paradise_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["paradise"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def hell_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["hell"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def health_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["health"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def rizq_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["rizq"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def knowledge_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    item = context.bot_data["duas"]["knowledge"][0]
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")

async def random_dua_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    duas = context.bot_data["duas"]
    pool = all_duas(duas)
    item = random.choice(pool)
    if update.message is not None:
        await update.message.reply_text(format_dua(item), parse_mode="Markdown")


async def morning_dua_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = get_target_chat_id()
    if chat_id is None:
        logger.info("No target chat id found yet. Send /start once to register chat.")
        return

    duas = context.bot_data["duas"]
    item = random.choice(duas["wakeup"])
    await context.bot.send_message(
        chat_id=chat_id,
        text="সুপ্রভাত। ঘুম থেকে ওঠার দোয়াটি পড়ুন:\n\n" + format_dua(item),
        parse_mode="Markdown",
    )


def main() -> None:
    if not TOKEN:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN in .env")

    try:
        morning_time = parse_hhmm(MORNING_DUA_TIME)
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc

    try:
        tz = ZoneInfo(TIMEZONE)
    except Exception as exc:
        raise RuntimeError(f"Invalid TIMEZONE: {TIMEZONE}") from exc

    morning_time = morning_time.replace(tzinfo=tz)

    application = Application.builder().token(TOKEN).build()
    application.bot_data["duas"] = load_duas()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("out", out_cmd))
    application.add_handler(CommandHandler("home", home_cmd))
    application.add_handler(CommandHandler("sleep", sleep_cmd))
    application.add_handler(CommandHandler("travel", travel_cmd))
    application.add_handler(CommandHandler("eat", eat_cmd))
    application.add_handler(CommandHandler("study", study_cmd))
    application.add_handler(CommandHandler("parents", parents_cmd))
    application.add_handler(CommandHandler("sneeze", sneeze_cmd))
    application.add_handler(CommandHandler("sad", sad_cmd))
    application.add_handler(CommandHandler("patience", patience_cmd))
    application.add_handler(CommandHandler("protection", protection_cmd))
    application.add_handler(CommandHandler("mosque_in", mosque_in_cmd))
    application.add_handler(CommandHandler("mosque_out", mosque_out_cmd))
    application.add_handler(CommandHandler("bathroom_in", bathroom_in_cmd))
    application.add_handler(CommandHandler("bathroom_out", bathroom_out_cmd))
    application.add_handler(CommandHandler("mirror", mirror_cmd))
    application.add_handler(CommandHandler("clothes_on", clothes_on_cmd))
    application.add_handler(CommandHandler("clothes_off", clothes_off_cmd))
    application.add_handler(CommandHandler("wudu_before", wudu_before_cmd))
    application.add_handler(CommandHandler("wudu_after", wudu_after_cmd))
    application.add_handler(CommandHandler("market", market_cmd))
    application.add_handler(CommandHandler("rain", rain_cmd))
    application.add_handler(CommandHandler("rain_after", rain_after_cmd))
    application.add_handler(CommandHandler("thunder", thunder_cmd))
    application.add_handler(CommandHandler("fear", fear_cmd))
    application.add_handler(CommandHandler("angry", angry_cmd))
    application.add_handler(CommandHandler("evil_eye", evil_eye_cmd))
    application.add_handler(CommandHandler("good_news", good_news_cmd))
    application.add_handler(CommandHandler("debt", debt_cmd))
    application.add_handler(CommandHandler("strength", strength_cmd))
    application.add_handler(CommandHandler("success", success_cmd))
    application.add_handler(CommandHandler("barakah", barakah_cmd))
    application.add_handler(CommandHandler("good_ending", good_ending_cmd))
    application.add_handler(CommandHandler("new_place", new_place_cmd))
    application.add_handler(CommandHandler("moon", moon_cmd))
    application.add_handler(CommandHandler("fasting", fasting_cmd))
    application.add_handler(CommandHandler("iftar", iftar_cmd))
    application.add_handler(CommandHandler("laylatul_qadr", laylatul_qadr_cmd))
    application.add_handler(CommandHandler("paradise", paradise_cmd))
    application.add_handler(CommandHandler("hell", hell_cmd))
    application.add_handler(CommandHandler("health", health_cmd))
    application.add_handler(CommandHandler("rizq", rizq_cmd))
    application.add_handler(CommandHandler("knowledge", knowledge_cmd))
    application.add_handler(CommandHandler("dua", random_dua_cmd))

    application.job_queue.run_daily(
        callback=morning_dua_job,
        time=morning_time,
        name="morning_dua",
        data=None,
        days=(0, 1, 2, 3, 4, 5, 6),
    )

    logger.info("Bot started")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()










