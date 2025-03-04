# Ruke Telegram Bot

A Telegram bot that mimics the personality and speech patterns of Ryuk from Death Note, speaking in Russian.

## Features

- Responds to messages in the style of Ryuk from Death Note
- Uses Google's Gemini AI model to generate contextual responses
- Maintains Ryuk's cynical, playful personality
- Maintains conversation context for a natural dialogue experience
- Works in both private chats and group chats

## Setup

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (obtained from [@BotFather](https://t.me/botfather))
- Google API Key for Gemini

### Installation

1. Clone this repository
```bash
git clone https://github.com/your-username/ruke-telegram-bot.git
cd ruke-telegram-bot
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
   - Create a `.env` file in the project root
   - Add your Telegram Bot Token (obtain from BotFather)
   - Add your Google API Key for Gemini
   - Example:
   ```
   TELEGRAM_TOKEN=your_telegram_token_here
   GOOGLE_API_KEY=your_google_api_key_here
   DEFAULT_LLM_MODEL=gemini-pro
   ```

### Running the Bot

```bash
python simple_ruke_bot.py
```

## Usage

### In Direct Messages
In private chats, the bot will respond to all messages.

### In Group Chats
In group chats, the bot will only respond to:
1. Commands like `/ryuk your message here`
2. Replies to the bot's previous messages

### Commands

- `/start` - Start the bot and get a welcome message
- `/help` - Display help information
- `/ryuk [message]` - Send a message to Ryuk (works in both private and group chats)
- `/debug` - Display debugging information about the bot

## Deploying to Replit

1. Fork this repository on GitHub
2. Create a new Replit project, selecting "Import from GitHub"
3. Enter your repository URL
4. In Replit, add your environment variables in the Secrets tab:
   - Add `TELEGRAM_TOKEN` with your Telegram bot token
   - Add `GOOGLE_API_KEY` with your Google Gemini API key
   - Add `DEFAULT_LLM_MODEL` with the model name (use `gemini-pro`)
5. Click "Run" to start your bot

## Troubleshooting

If you see an error like "unexpected model name format", you need to update the Gemini model name in your environment variables. Currently supported models include:
- `gemini-pro` (recommended)
- `gemini-1.5-pro`
- `gemini-1.5-flash`

## Notes

- The bot uses the Gemini AI model to generate responses
- All interactions are designed to mimic Ryuk's character from Death Note
- The bot maintains conversation context for 10 minutes
- The bot speaks Russian exclusively 