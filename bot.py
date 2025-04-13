import telebot
from telebot import types
import logging
from config import TELEGRAM_TOKEN, DEFAULT_SEARCH_PARAMS, SessionLocal
from database import get_user_settings, update_user_settings
from parsers.hh_parser import parse_hh
from parsers.linkedin_parser import parse_linkedin
from models import UserSettings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    filename='log.log',
    filemode='w',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Conversation states
class States:
    NONE = 0
    KEYWORDS = 1
    LOCATIONS = 2
    SALARY = 3
    EXPERIENCE = 4

user_states = {}

# Experience levels
EXPERIENCE_LEVELS = {
    "noExperience": "No experience",
    "between1And3": "1-3 years",
    "between3And6": "3-6 years",
    "moreThan6": "6+ years"
    }
EXPERIENCE_REVERSE_MAP = {v: k for k, v in EXPERIENCE_LEVELS.items()}

def format_vacancy(vacancy: dict) -> str:
    return (
    f"🏢 <b>{vacancy['company']}</b>\n"
    f"🔹 <b>{vacancy['title']}</b>\n"
    f"💰 Salary: {vacancy.get('salary', 'Not specified')}\n"
    f"🌐 Source: {vacancy['source']}\n"
    f"🔗 <a href='{vacancy['url']}'>View job</a>"
    )

def get_user_settings_with_defaults(user_id: int) -> dict:
    db = SessionLocal()
    try:
        settings = get_user_settings(db, user_id)
        if settings:
            return {
                "keywords": settings.keywords,
                "locations": settings.locations,
                "salary_min": settings.salary_min,
                "experience": settings.experience
            }
        return DEFAULT_SEARCH_PARAMS.copy()

    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return DEFAULT_SEARCH_PARAMS.copy()

    finally:
        db.close()


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_states[user_id] = States.NONE

    bot.reply_to(message,
    "🔍 <b>Job Search Bot</b>\n\n"
    "I can help you find job openings!\n"
    "Use /settings to configure your search\n"
    "Use /search to find jobs\n"
    "Use /help for instructions",
    parse_mode="HTML")

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
    "🤖 <b>Job Search Bot Help</b>\n\n"
    "/start - Start the bot\n"
    "/settings - Configure search parameters\n"
    "/search - Find jobs\n"
    "/help - Show this message\n\n"
    "Configure your job search with:\n"
    "- Keywords (e.g., Python, Java)\n"
    "- Locations (e.g., Remote, Moscow)\n"
    "- Minimum salary\n"
    "- Experience level"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="HTML")

@bot.message_handler(commands=['settings'])
def settings(message):
    user_id = message.from_user.id
    user_states[user_id] = States.NONE

    current_settings = get_user_settings_with_defaults(user_id)

    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(
    types.KeyboardButton('Change Keywords'),
    types.KeyboardButton('Change Locations'),
    types.KeyboardButton('Change Salary'),
    types.KeyboardButton('Change Experience'),
    types.KeyboardButton('Show Current Settings'),
    types.KeyboardButton('Cancel')
    )

    bot.send_message(
    user_id,
    "⚙️ <b>Settings Menu</b>\n\n"
    "Current settings:\n"
    f"Keywords: {', '.join(current_settings['keywords'])}\n"
    f"Locations: {', '.join(current_settings['locations'])}\n"
    f"Min Salary: {current_settings['salary_min']}\n"
    f"Experience: {EXPERIENCE_LEVELS.get(current_settings['experience'], current_settings['experience'])}",
    reply_markup=markup,
    parse_mode="HTML"
    )

@bot.message_handler(func=lambda message: message.text == 'Change Keywords')
def request_keywords(message):
    user_id = message.from_user.id
    user_states[user_id] = States.KEYWORDS
    bot.send_message(
    user_id,
    "🔤 Enter job keywords separated by commas (e.g., Python, Django, Backend):",
    reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == States.KEYWORDS)
def save_keywords(message):
    user_id = message.from_user.id

    if message.text == 'Cancel':
        return cancel_action(message)

    keywords = [kw.strip() for kw in message.text.split(',') if kw.strip()]

    if not keywords:
        bot.send_message(user_id, "⚠️ Please enter at least one keyword")
        return

    if len(keywords) > 5:
        bot.send_message(user_id, "⚠️ Please enter no more than 5 keywords")
        return

    db = SessionLocal()
    try:
        current_settings = get_user_settings(db, user_id)
        if current_settings:
            current_settings.keywords = keywords
            db.commit()
        else:
            new_settings = DEFAULT_SEARCH_PARAMS.copy()
            new_settings["keywords"] = keywords
            update_user_settings(db, user_id, new_settings)

            bot.send_message(user_id, "✅ Keywords updated!")
    except Exception as e:
        logger.error(f"Error saving keywords: {e}")
        bot.send_message(user_id, "⚠️ Error saving settings")
    finally:
        db.close()

    user_states[user_id] = States.NONE
    settings(message)

@bot.message_handler(func=lambda message: message.text == 'Change Locations')
def request_locations(message):
    user_id = message.from_user.id
    user_states[user_id] = States.LOCATIONS

    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(
    types.KeyboardButton('Remote'),
    types.KeyboardButton('Moscow'),
    types.KeyboardButton('Saint Petersburg'),
    types.KeyboardButton('New York'),
    types.KeyboardButton('Multiple Locations'),
    types.KeyboardButton('Cancel')
    )

    bot.send_message(
    user_id,
    "🌍 Select location or enter custom one:",
    reply_markup=markup
    )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == States.LOCATIONS)
def save_locations(message):
    user_id = message.from_user.id

    if message.text == 'Cancel':
        return cancel_action(message)

    if message.text == 'Multiple Locations':
        bot.send_message(
        user_id,
        "Enter locations separated by commas (e.g., Remote, Moscow, New York):",
        reply_markup=types.ReplyKeyboardRemove()
        )
        return

    locations = [loc.strip() for loc in message.text.split(',') if loc.strip()]

    if not locations:
        bot.send_message(user_id, "⚠️ Please enter at least one location")
        return

    if len(locations) > 3:
        bot.send_message(user_id, "⚠️ Please enter no more than 3 locations")
        return

    db = SessionLocal()
    try:
        current_settings = get_user_settings(db, user_id)
        if current_settings:
            current_settings.locations = locations
            db.commit()
        else:
            new_settings = DEFAULT_SEARCH_PARAMS.copy()
            new_settings["locations"] = locations
            update_user_settings(db, user_id, new_settings)

            bot.send_message(user_id, "✅ Locations updated!")
    except Exception as e:
        logger.error(f"Error saving locations: {e}")
        bot.send_message(user_id, "⚠️ Error saving settings")
    finally:
        db.close()

    user_states[user_id] = States.NONE
    settings(message)

@bot.message_handler(func=lambda message: message.text == 'Change Salary')
def request_salary(message):
    user_id = message.from_user.id
    user_states[user_id] = States.SALARY

    markup = types.ReplyKeyboardMarkup(row_width=3)
    markup.add(
    types.KeyboardButton('50000'),
    types.KeyboardButton('100000'),
    types.KeyboardButton('150000'),
    types.KeyboardButton('200000'),
    types.KeyboardButton('Custom Amount'),
    types.KeyboardButton('Cancel')
    )

    bot.send_message(
    user_id,
    "💰 Enter minimum salary (RUB):",
    reply_markup=markup
    )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == States.SALARY)
def save_salary(message):
    user_id = message.from_user.id

    if message.text == 'Cancel':
        return cancel_action(message)

    if message.text == 'Custom Amount':
        bot.send_message(
        user_id,
        "Enter custom minimum salary amount in RUB:",
        reply_markup=types.ReplyKeyboardRemove()
        )
        return

    if not message.text.isdigit():
        bot.send_message(user_id, "⚠️ Please enter a valid number")
        return

    salary = int(message.text)

    if salary < 0:
        bot.send_message(user_id, "⚠️ Salary cannot be negative")
        return

    if salary > 1000000:
        bot.send_message(user_id, "⚠️ Please enter a reasonable salary amount")
        return

    db = SessionLocal()
    try:
        current_settings = get_user_settings(db, user_id)
        if current_settings:
            current_settings.salary_min = salary
            db.commit()
        else:
            new_settings = DEFAULT_SEARCH_PARAMS.copy()
            new_settings["salary_min"] = salary
            update_user_settings(db, user_id, new_settings)

            bot.send_message(user_id, f"✅ Minimum salary set to {salary} RUB!")
    except Exception as e:
        logger.error(f"Error saving salary: {e}")
        bot.send_message(user_id, "⚠️ Error saving settings")
    finally:
        db.close()

    user_states[user_id] = States.NONE
    settings(message)


@bot.message_handler(func=lambda message: message.text == 'Change Experience')
def request_experience(message):
    user_id = message.from_user.id
    user_states[user_id] = States.EXPERIENCE

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        types.KeyboardButton(text)
        for text in EXPERIENCE_LEVELS.values()
    ]
    markup.add(*buttons, types.KeyboardButton('Cancel'))

    bot.send_message(
        user_id,
        "👔 <b>Select your experience level:</b>",
        reply_markup=markup,
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == States.EXPERIENCE)
def save_experience(message):
    user_id = message.from_user.id

    if message.text == 'Cancel':
        cancel_action(message)
        return

    if message.text not in EXPERIENCE_REVERSE_MAP:
        bot.send_message(
            user_id,
            "⚠️ Please select an option from the keyboard below:",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=[
                    [types.KeyboardButton(exp)]
                    for exp in EXPERIENCE_LEVELS.values()
                ],
                resize_keyboard=True
            )
        )
        return

    db = SessionLocal()
    try:
        settings = get_user_settings(db, user_id) or UserSettings(
            user_id=user_id,
            **DEFAULT_SEARCH_PARAMS
        )

        settings.experience = EXPERIENCE_REVERSE_MAP[message.text]

        db.add(settings)
        db.commit()

        bot.send_message(
            user_id,
            f"✅ Experience level set to <b>{message.text}</b>!",
            parse_mode="HTML",
            reply_markup=types.ReplyKeyboardRemove()
        )

    except Exception as e:
        logger.error(f"Error saving experience: {str(e)}", exc_info=True)
        bot.send_message(
            user_id,
            "⚠️ Failed to save experience level. Please try again."
        )
    finally:
        db.close()

    user_states[user_id] = States.NONE
    show_settings(message)


@bot.message_handler(func=lambda message: message.text == 'Show Current Settings')
def show_settings(message):
    user_id = message.from_user.id

    db = SessionLocal()
    try:
        current_settings = get_user_settings(db, user_id)

        if current_settings:
            current_settings = {
                'keywords': current_settings.keywords,
                'locations': current_settings.locations,
                'salary_min': current_settings.salary_min,
                'experience': current_settings.experience
            }
        else:
            current_settings = DEFAULT_SEARCH_PARAMS.copy()

        bot.send_message(
            user_id,
            "⚙️ <b>Current Settings</b>\n\n"
            f"Keywords: {', '.join(current_settings['keywords'])}\n"
            f"Locations: {', '.join(current_settings['locations'])}\n"
            f"Min Salary: {current_settings['salary_min']} RUB\n"
            f"Experience: {EXPERIENCE_LEVELS.get(current_settings['experience'], current_settings['experience'])}",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error showing settings: {e}")
        bot.send_message(user_id, "⚠️ Error loading settings")
    finally:
        db.close()


@bot.message_handler(func=lambda message: message.text == 'Cancel')
def cancel_action(message):
    user_id = message.from_user.id
    user_states[user_id] = States.NONE
    bot.send_message(
    user_id,
    "❌ Action cancelled\n"
        "Use /settings to configure your search\n"
        "Use /search to find jobs",
        parse_mode="HTML",
    reply_markup=types.ReplyKeyboardRemove()
    )

@bot.message_handler(commands=['search'])
def search_jobs(message):
    user_id = message.from_user.id

    bot.send_chat_action(user_id, 'typing')
    msg = bot.send_message(user_id, "🔍 Searching for jobs...")

    try:
        vacancies = []
        vacancies.extend(parse_hh(user_id))
        vacancies.extend(parse_linkedin(user_id))

        if not vacancies:
            bot.edit_message_text(
            "😕 No jobs found with current settings. Try adjusting your search criteria.",
            chat_id=user_id,
            message_id=msg.message_id
            )
            return

        bot.edit_message_text(
        f"✅ Found {len(vacancies)} jobs:",
        chat_id=user_id,
        message_id=msg.message_id
        )

        for vacancy in vacancies:
            try:
                bot.send_message(
                user_id,
                format_vacancy(vacancy),
                parse_mode="HTML",
                disable_web_page_preview=True
                )
            except Exception as e:
                logger.error(f"Error sending vacancy: {e}")
                continue

    except Exception as e:
        logger.error(f"Search error: {e}")
        bot.send_message(user_id, "⚠️ Error occurred while searching")

if __name__ == "__main__":
    from models import Base
    from config import engine

    # Create database tables
    Base.metadata.create_all(bind=engine)

    logger.info("Starting bot...")
    print("Starting bot...")
    while True:
        try:
            bot.infinity_polling(none_stop=True, timeout=30, skip_pending=True)
        except Exception as e:
            logging.error(f"polling error: {e}")
            import time
            time.sleep(5)
