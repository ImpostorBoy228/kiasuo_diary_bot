# kiasuo_diary_bot

AI-based Telegram bot for sending homework assignments from the Kiasuo diary system.

**Status:** Experimental, unstable. Requires Gosuslugi authentication every hour.  
*At least, I tried.*

## Features

- **Fetches Homework**: Retrieves homework assignments from the Kiasuo diary API.
- **Telegram Integration**: Sends homework to users via Telegram with interactive buttons.
- **Authentication**: Uses browser automation (Selenium) to obtain a token from Gosuslugi.
- **Background Fetching**: Fetches and formats homework asynchronously.
- **Markdown Formatting**: Uses custom routines to format homework for Telegram's MarkdownV2.
- **Error Handling & Logging**: Detailed logs for all major actions and errors.

## Main Components

- `bot.py`  
  - Sets up the Telegram bot (ApplicationBuilder, handlers).
  - `/start`: Presents a button to fetch homework.
  - `/help`: Shows instructions.
  - Button callback: Fetches and sends homework, handling errors.
  - Main loop: Handles token acquisition, runs polling.

- `fetcher.py`  
  - `fetch_homeworks()`: Loads token, requests schedule/homework from Kiasuo API, formats for Telegram.
  - Uses `llm_transform()` for Markdown formatting.
  - Handles token loss and error messaging.

- `auth.py`  
  - `get_token_with_browser()`: Launches Chrome via Selenium; user manually logs in via Gosuslugi, token is extracted from localStorage.
  - `save_token/load_token`: Stores/retrieves token from disk.
  - Handles cookies for session persistence.

- `llm.py`  
  - `llm_transform()`: Groups homework by date/subject, escapes characters for MarkdownV2, formats list for Telegram message.

- `config.py`  
  - Stores bot token and user ID.

## Usage

1. **Install Dependencies**
   ```bash
   pip install python-telegram-bot selenium httpx
   ```

2. **Run the Bot**
   ```bash
   python bot.py
   ```
   - On first run, browser will open for manual authentication.
   - Click "Войти через Госуслуги" in the browser window.

3. **Interact via Telegram**
   - Use `/start` to launch.
   - Press button to fetch homework.
   - Use `/help` for instructions.

## Troubleshooting

- **Token Lost**: If the token expires, re-authenticate via browser.
- **API Errors**: Check logs for request/response issues.
- **Markdown Formatting**: All messages are escaped for Telegram's MarkdownV2.

## Limitations

- Requires manual authentication every hour due to Gosuslugi token expiry.
- Unstable due to API changes and authentication issues.

