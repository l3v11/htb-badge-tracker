# HTB Badge Tracker

HTB Badge Tracker is a Telegram bot that periodically checks the number of badges for various Hack The Box Academy job role paths and exams, and sends updates to a specific Telegram channel.

## Features

- Fetches the latest badge numbers from Hack The Box Academy.
- Compares the latest badge numbers with the previous values.
- Posts an update message in a Telegram channel if there are any changes in badge numbers.
- Logs badge numbers with timestamps in a CSV file.
- Shows the last batch runs.

## Installation

1. **Create a Telegram Bot:**

   You can find instructions here:
   https://core.telegram.org/bots/tutorial

2. **Clone the repository:**

   ```bash
   git clone https://github.com/l3v11/htb-badge-tracker
   cd htb-badge-tracker
   ```

3. **Install the required dependencies:**

   ```bash
   pip3 install --no-cache-dir -r requirements.txt
   ````

4. **Create a .env file in the root directory and add the following environment variables:**

   ```plaintext
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_USER_ID=your_telegram_user_id
   TELEGRAM_CHANNEL_ID=your_telegram_channel_id
   CBBH_EXAM=cbbh_exam_id
   CBBH_PATH=cbbh_path_id
   CPTS_EXAM=cpts_exam_id
   CPTS_PATH=cpts_path_id
   CDSA_EXAM=cdsa_exam_id
   CDSA_PATH=cdsa_path_id
   CWEE_EXAM=cwee_exam_id
   CWEE_PATH=cwee_path_id
   CAPE_EXAM=cape_exam_id
   CAPE_PATH=cape_path_id
   CJCA_EXAM=cjca_exam_id
   CJCA_PATH=cjca_path_id
   ```

5. **Run the bot:**

   ```bash
   python3 bot.py
   ```

6. **Send the following list of Bot commands to [@BotFather](https://t.me/BotFather):**
   ```plaintext
   start - Start the bot
   status - Check badge status manually
   last_batch - Get the timestamp of last batch
   log - Get the log file
   ```

## Configuration

- TELEGRAM_BOT_TOKEN: Get this token by creating a bot in [@BotFather](https://t.me/BotFather).
- TELEGRAM_USER_ID: The Telegram user you want to authorize to use the bot.
- TELEGRAM_CHANNEL_ID: The ID of the Telegram channel where the bot will post updates.
- CBBH_EXAM, CBBH_PATH, CPTS_EXAM, CPTS_PATH, CDSA_EXAM, CDSA_PATH, CWEE_EXAM, CWEE_PATH, CAPE_EXAM, CAPE_PATH, CJCA_EXAM, CJCA_PATH: The IDs for the respective badges. If you do not have an ID, you can simply leave the variable empty. The bot will then set the number to 0.

You can find your Badge IDs here: [Hack The Box Academy - My Badges](https://academy.hackthebox.com/my-badges)

To get the ID of the badge, you have to share the badge.
Click on the "Share" link for the corresponding badge and then on "Get a shareable link"

You will get a URL like this:
https://academy.hackthebox.com/achievement/badge/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

The ID has the format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx


## License

This project is licensed under the terms of the MIT License.

## Credits
[Sourav](https://github.com/l3v11) *(Maintainer)* |
[PayloadBunny](https://github.com/PayloadBunnyy)
