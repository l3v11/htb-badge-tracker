#!/usr/bin/env python3
import csv
import os
import requests
import logging
from logging.handlers import RotatingFileHandler
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext

# Directory and file paths
INSTALL_DIR =  os.getcwd()
LOG_DIR = os.path.join(INSTALL_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'bot.log') 
DATA_DIR = os.path.join(INSTALL_DIR, 'data')
BADGE_CSV = os.path.join(DATA_DIR, 'badges.csv')

# Create the log directory if it does not exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Create the data directory if it does not exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# URL for fetching badge information
BADGE_URL = "https://academy.hackthebox.com/achievement/badge/"

# Set up logging with file rotation
# The log file size limit is set to 10 MB (maxBytes=10*1024*1024)
# Up to 5 backup log files will be kept (backupCount=5)
log_handler = RotatingFileHandler(LOG_FILE, maxBytes=10*1024*1024, backupCount=5)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[log_handler],
                    level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable is missing")
    exit(1)
AUTHORIZED_USER_ID = os.getenv('TELEGRAM_USER_ID', '')
if not AUTHORIZED_USER_ID:
    logger.error("TELEGRAM_USER_ID environment variable is missing")
    exit(1)
else:
    AUTHORIZED_USER_ID = int(AUTHORIZED_USER_ID)
CHAT_ID = os.getenv('TELEGRAM_CHANNEL_ID', '')
if not CHAT_ID:
    logger.error("TELEGRAM_CHANNEL_ID environment variable is missing")
    exit(1)

# Create badges.csv file and write the header line
if not os.path.isfile(BADGE_CSV):
    fields = [
        'timestamp', 'CBBH-Exam', 'CBBH-Path', 'CPTS-Exam', 'CPTS-Path', 'CDSA-Exam', 'CDSA-Path',
        'CWEE-Exam', 'CWEE-Path', 'CAPE-Exam', 'CAPE-Path', 'CJCA-Exam', 'CJCA-Path'
    ]
    with open(BADGE_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(fields)

# Badge IDs and symbols from environment variables
BADGES = {
    'CBBH': {
        'symbol': '🕸️',
        'exam_id': os.getenv('CBBH_EXAM'),
        'path_id': os.getenv('CBBH_PATH')
    },
    'CPTS': {
        'symbol': '⚔️',
        'exam_id': os.getenv('CPTS_EXAM'),
        'path_id': os.getenv('CPTS_PATH')
    },
    'CDSA': {
        'symbol': '🛡️',
        'exam_id': os.getenv('CDSA_EXAM'),
        'path_id': os.getenv('CDSA_PATH')
    },
    'CWEE': {
        'symbol': '🕷️',
        'exam_id': os.getenv('CWEE_EXAM'),
        'path_id': os.getenv('CWEE_PATH')
    },
    'CAPE': {
        'symbol': '🫅',
        'exam_id': os.getenv('CAPE_EXAM'),
        'path_id': os.getenv('CAPE_PATH')
    },
    'CJCA': {
        'symbol': '🥷',
        'exam_id': os.getenv('CJCA_EXAM'),
        'path_id': os.getenv('CJCA_PATH')
    }
}

# Function to fetch the last recorded badge numbers from the CSV file
def get_last_badge_numbers():
    try:
        with open(BADGE_CSV, 'r') as csvfile:
            last_line = csvfile.readlines()[-1].strip()
        return last_line.split(',')
    except FileNotFoundError:
        logger.error("CSV file not found")
        return [0] * (len(BADGES) * 2 + 1)
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        return [0] * (len(BADGES) * 2 + 1)

# Function to fetch the current badge number from the website for a given badge ID
def fetch_badge_number(badge_id):
    if not badge_id:
        return '0'
    try:
        page = requests.get(f"{BADGE_URL}{badge_id}")
        page.raise_for_status()
        soup = BeautifulSoup(page.text, 'html.parser')
        span = soup.find('span', class_='font-size-20 text-white')
        return span.get_text() if span else '0'
    except requests.RequestException as e:
        logger.error(f"Error fetching badge number: {e}")
        return '0'

# Function to fetch the current badge numbers for all badges
def fetch_current_badge_numbers():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    badge_numbers = [timestamp]
    for badge in BADGES.values():
        badge_numbers.append(fetch_badge_number(badge['exam_id']))
        badge_numbers.append(fetch_badge_number(badge['path_id']))
    return badge_numbers

# Function to compare the last and current badge numbers
def compare_badge_numbers(last_badges, current_badges):
    return [int(current) - int(last) for last, current in zip(last_badges[1:], current_badges[1:])]

# Function to add the current badge numbers to the CSV file
def add_badge_numbers_to_csv(new_entry):
    try:
        with open(BADGE_CSV, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(new_entry)
    except Exception as e:
        logger.error(f"Error writing to CSV file: {e}")

# Function to generate a message detailing the changes in badge numbers
def generate_update_message(differences, current_badges):
    message = ""
    for i, (name, badge) in enumerate(BADGES.items()):
        path_diff, exam_diff = differences[2 * i], differences[2 * i + 1]
        path_num, exam_num = current_badges[2 * i + 1], current_badges[2 * i + 2]

        if badge['exam_id'] or badge['path_id']:
            message += f"{badge['symbol']} *{name}*\n"
            if badge['exam_id']:
                message += f"EXAM: {exam_num} {'*(+' + str(exam_diff) + ')*' if exam_diff != 0 else ''}\n"
            if badge['path_id']:
                message += f"PATH: {path_num} {'*(+' + str(path_diff) + ')*' if path_diff != 0 else ''}\n"
            message += "\n"

    message += f"_Last updated: {current_badges[0]} UTC_"
    return message

# Function to get the last update times for each exam from the CSV file
def get_last_update_times():
    last_update_times = {}
    try:
        with open(BADGE_CSV, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)

            if len(rows) < 2:
                return last_update_times

            data_rows = rows[1:]
            previous_values = {}

            for row in data_rows:
                timestamp = row[0]
                for i, (name, badge) in enumerate(BADGES.items()):
                    if not badge['exam_id'] or not badge['path_id']:
                        continue
                    exam_index = 2 * i + 2
                    if exam_index >= len(row):
                        continue
                    exam_value = row[exam_index]

                    if name not in previous_values or previous_values[name] != exam_value:
                        last_update_times[name] = (timestamp, exam_value)
                        previous_values[name] = exam_value

    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
    return last_update_times

# Function to display the last batch update times for each exam
async def last_batch(update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id if update.message and update.message.from_user else None

    if user_id != AUTHORIZED_USER_ID:
        logger.warning(f"Unauthorized access attempt by user: {user_id}")
        return

    last_update_times = get_last_update_times()
    message = "_Last Batch Update Times:_\n\n"
    for name, badge in BADGES.items():
        symbol = badge['symbol']
        if badge['exam_id'] or badge['path_id']:
            if name in last_update_times:
                timestamp = last_update_times[name][0]
                message += f"{symbol} {name}: {timestamp} UTC\n"
            else:
                message += f"{symbol} {name}: No data\n"
        else:
            message += f"{symbol} {name}: No data\n"
    try:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=message,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")

# Function to send status message every hour
async def status_message(context: CallbackContext):
    last_badge_numbers = get_last_badge_numbers()
    current_badge_numbers = fetch_current_badge_numbers()

    if last_badge_numbers[0] == "timestamp":
        add_badge_numbers_to_csv(current_badge_numbers)
        logger.info("Current badge numbers added to CSV")
    else:
        differences = compare_badge_numbers(last_badge_numbers, current_badge_numbers)

        if any(differences):
            add_badge_numbers_to_csv(current_badge_numbers)
            logger.info("Current badge numbers added to CSV")
            message = generate_update_message(differences, current_badge_numbers)
            try:
                await context.bot.send_message(
                    chat_id=CHAT_ID,
                    text=message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to send Telegram message: {e}")
        else:
            logger.info("No badge updates since last check")

# Function to start the bot and send a welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id if update.message and update.message.from_user else None

    if user_id != AUTHORIZED_USER_ID:
        logger.warning(f"Unauthorized access attempt by user: {user_id}")
        return

    if update.message:
        await update.message.reply_text("👽 HTB Badge Tracker Bot is online and watching!")
    else:
        chat_id = update.effective_chat.id if update.effective_chat else None
        if chat_id:
            await context.bot.send_message(
                chat_id=chat_id,
                text="👽 HTB Badge Tracker Bot is online and watching!"
            )
        else:
            pass

# Function to schedule the badge status check every hour
async def scheduled_status_check(application: Application):
    job_queue = application.job_queue

    if job_queue:
        job_queue.run_repeating(status_message, interval=3600, first=10)
        logger.info("Scheduled badge status check every hour")
    else:
        logger.warning("Job queue not available during startup")

# Function to manually check the badge status
async def manual_status_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id if update.message and update.message.from_user else None

    if user_id != AUTHORIZED_USER_ID:
        logger.warning(f"Unauthorized access attempt by user: {user_id}")
        return

    await status_message(context)

    if update.message:
        await update.message.reply_text("⌛ Badge status has been checked!")
    else:
        chat_id = update.effective_chat.id if update.effective_chat else None
        if chat_id:
            await context.bot.send_message(
                chat_id=chat_id,
                text="⌛ Badge status has been checked!"
            )
        else:
            pass

# Function to send the latest log (bot.log) file to Telegram
async def send_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id if update.message and update.message.from_user else None

    if user_id != AUTHORIZED_USER_ID:
        logger.warning(f"Unauthorized access attempt by user: {user_id}")
        return

    try:
        with open(LOG_FILE, 'rb') as log_file:
            chat_id = update.effective_chat.id if update.effective_chat else None
            if chat_id:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=log_file,
                    filename="bot.log"
                )
            else:
                pass

    except Exception as e:
        logger.error(f"Failed to send the log file: {e}")
        if update.message:
            await update.message.reply_text("❌ Failed to send the log file!")

# Main function to set up the bot and start polling
def main():
    # Create the application with the bot token
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", manual_status_check))
    application.add_handler(CommandHandler("last_batch", last_batch))
    application.add_handler(CommandHandler("log", send_log))

    # Schedule the status message every hour
    application.post_init = scheduled_status_check
    application.run_polling()

if __name__ == '__main__':
    main()
