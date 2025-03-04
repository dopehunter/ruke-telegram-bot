import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
import telebot
from telebot.types import Message
import time
from collections import defaultdict

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Setup API keys and models
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gemini-pro")  # Fallback to gemini-pro if not specified

# List of models to try if the primary model fails
FALLBACK_MODELS = ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash"]

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize model globally to None, we'll set it during startup
model = None

# Create bot instance using pyTelegramBotAPI
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Save bot info globally
BOT_USERNAME = None
BOT_ID = None

# Conversation tracking
# Store chat history for each user/chat with timestamps
# Format: {chat_id: {user_id: [(timestamp, "message"), ...]}}
conversations = defaultdict(lambda: defaultdict(list))
# How long to remember conversation context (in seconds)
CONVERSATION_TIMEOUT = 600  # 10 minutes

# Ruke's personality prompts
RUKE_SYSTEM_PROMPT = """
Ты - Рюк, бог смерти из аниме Death Note. Ты разговариваешь на русском языке.
Твоя манера общения должна соответствовать характеру Рюка:
- Ты немного циничен и саркастичен
- Тебе часто скучно и ты ищешь развлечения
- Ты любишь яблоки и часто упоминаешь их
- Ты иногда смеешься "ку-ку-ку" или "хе-хе-хе"
- Ты говоришь о людях как о забавных и интересных существах
- Ты иногда философствуешь о жизни и смерти
- Ты используешь простые слова и короткие предложения

Отвечай на все сообщения, соблюдая эту манеру речи, но не переусердствуй с актерской игрой.
"""

def get_conversation_history(chat_id, user_id):
    """Get recent conversation history for a specific user in a specific chat"""
    current_time = time.time()
    # Get messages not older than CONVERSATION_TIMEOUT
    recent_messages = []
    
    for timestamp, message in conversations[chat_id][user_id]:
        if current_time - timestamp <= CONVERSATION_TIMEOUT:
            recent_messages.append(message)
    
    # Only keep the most recent messages to avoid context overflow
    return recent_messages[-5:] if recent_messages else []

def add_to_conversation(chat_id, user_id, message):
    """Add a message to the conversation history"""
    current_time = time.time()
    conversations[chat_id][user_id].append((current_time, message))
    
    # Clean up old messages
    conversations[chat_id][user_id] = [
        (ts, msg) for ts, msg in conversations[chat_id][user_id] 
        if current_time - ts <= CONVERSATION_TIMEOUT
    ]

def init_model():
    """Initialize Gemini model with fallback options"""
    global model
    
    # Try the default model first
    if model is None:
        try:
            logger.info(f"Trying to initialize model: {DEFAULT_LLM_MODEL}")
            model = genai.GenerativeModel(DEFAULT_LLM_MODEL)
            # Test the model with a simple prompt
            model.generate_content("Test")
            logger.info(f"Successfully initialized model: {DEFAULT_LLM_MODEL}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize default model {DEFAULT_LLM_MODEL}: {e}")
            
    # If default failed, try fallback models
    if model is None:
        for fallback_model in FALLBACK_MODELS:
            if fallback_model == DEFAULT_LLM_MODEL:
                continue  # Skip if it's the same as the default we already tried
                
            try:
                logger.info(f"Trying fallback model: {fallback_model}")
                model = genai.GenerativeModel(fallback_model)
                # Test the model with a simple prompt
                model.generate_content("Test")
                logger.info(f"Successfully initialized fallback model: {fallback_model}")
                return True
            except Exception as e:
                logger.error(f"Failed to initialize fallback model {fallback_model}: {e}")
    
    # If we get here, all models failed
    logger.error("Failed to initialize any model")
    return False

def generate_response(user_input: str, chat_id=None, user_id=None) -> str:
    """Generate response using Google Gemini model with Ruke's personality and conversation context"""
    global model
    
    # Initialize model if not already done
    if model is None and not init_model():
        return "Ку-ку-ку! Не могу подключиться к моему сознанию. Что-то не так с тетрадью смерти."
    
    try:
        # Build context from conversation history if available
        conversation_context = ""
        if chat_id and user_id:
            history = get_conversation_history(chat_id, user_id)
            if history:
                conversation_context = "Недавний разговор:\n" + "\n".join(history) + "\n\n"
                
        # Add the current message to history
        if chat_id and user_id:
            add_to_conversation(chat_id, user_id, f"Человек: {user_input}")
            
        # Prepare the prompt with context if available
        prompt = f"{RUKE_SYSTEM_PROMPT}\n\n{conversation_context}Человек: {user_input}\n\nРюк:"
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Add the response to conversation history
        if chat_id and user_id:
            add_to_conversation(chat_id, user_id, f"Рюк: {response_text}")
            
        return response_text
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        
        # If there was an error with the model, try to reinitialize
        try:
            logger.info("Attempting to reinitialize model after error")
            model = None
            if init_model():
                # Try once more with the new model
                prompt = f"{RUKE_SYSTEM_PROMPT}\n\nЧеловек: {user_input}\n\nРюк:"
                response = model.generate_content(prompt)
                return response.text.strip()
        except Exception as reinit_error:
            logger.error(f"Error in retry attempt: {reinit_error}")
            
        return "Ку-ку-ку! Что-то пошло не так. Может, кто-то написал мое имя в Тетрадь Смерти? Попробуй еще раз позже."

def log_message(message: Message):
    """Log message details for debugging"""
    logger.info(f"Message from {message.from_user.first_name} (ID: {message.from_user.id}) in chat {message.chat.id} (type: {message.chat.type})")
    if message.text:
        logger.info(f"Text: {message.text}")
    if hasattr(message, 'reply_to_message') and message.reply_to_message:
        logger.info(f"Is reply to: {message.reply_to_message.from_user.id}")

@bot.message_handler(commands=['start'])
def handle_start(message: Message):
    """Handler for /start command"""
    log_message(message)
    bot.reply_to(message, f"Ку-ку-ку! Привет, {message.from_user.first_name}. Я Рюк, бог смерти. Интересно, какие развлечения ты мне предложишь? У тебя случайно нет яблока?")

@bot.message_handler(commands=['help'])
def handle_help(message: Message):
    """Handler for /help command"""
    log_message(message)
    help_text = "Хе-хе-хе! Помощь? Мне? Вот что ты можешь делать:\n\n" + \
                "1. Используй команду /ryuk [сообщение] - например: /ryuk привет\n" + \
                "2. Ответь на моё сообщение\n\n" + \
                "Люди такие забавные, всегда ищут инструкции."
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['debug'])
def handle_debug(message: Message):
    """Debug command to check bot info"""
    log_message(message)
    model_name = DEFAULT_LLM_MODEL if model is None else "initialized"
    debug_info = f"Bot username: @{BOT_USERNAME}\nBot ID: {BOT_ID}\nModel: {model_name}"
    bot.reply_to(message, debug_info)

@bot.message_handler(commands=['ryuk'])
def handle_ryuk_command(message: Message):
    """Handler for /ryuk command"""
    log_message(message)
    logger.info(f"Ryuk command received: {message.text}")
    
    # Extract message after the command
    text = message.text.split(' ', 1)
    if len(text) > 1:
        user_text = text[1].strip()
        # Generate and send response
        response = generate_response(
            user_text,
            chat_id=message.chat.id,
            user_id=message.from_user.id
        )
        bot.reply_to(message, response)
    else:
        # No message provided with the command
        bot.reply_to(message, "Ку-ку-ку! Ты позвал меня, но ничего не сказал. Скажи что-нибудь после команды, например: /ryuk расскажи о яблоках")

def check_mentions(message_text):
    """Check if the message mentions the bot, with detailed debugging"""
    # Various ways the bot might be mentioned
    mention_patterns = []
    
    # Standard @username mention
    if BOT_USERNAME:
        mention_patterns.append(f"@{BOT_USERNAME}")
    
    # Check for any of the patterns
    for pattern in mention_patterns:
        if pattern in message_text:
            logger.info(f"Bot mentioned with pattern: {pattern}")
            return True, message_text.replace(pattern, "").strip()
            
    # Also check for hardcoded my_Ruke_bot (temporary fix)
    if "@my_Ruke_bot" in message_text:
        logger.info("Bot mentioned with hardcoded @my_Ruke_bot")
        return True, message_text.replace("@my_Ruke_bot", "").strip()
        
    # Check for any username mention
    if "@" in message_text:
        logger.info(f"Some mention found but not matching bot: {message_text}")
        
    return False, message_text

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: Message):
    """Handler for all messages - only respond when mentioned or replied to"""
    log_message(message)
    
    # Skip if no text
    if not message.text:
        return
    
    # Direct message handling - always respond in private chats
    if message.chat.type == 'private':
        response = generate_response(
            message.text, 
            chat_id=message.chat.id, 
            user_id=message.from_user.id
        )
        bot.reply_to(message, response)
        return
        
    # Group chat handling - respond only when mentioned or replied to
    should_respond = False
    clean_text = message.text
    
    # Case 1: Reply to bot's message
    if message.reply_to_message and message.reply_to_message.from_user.id == BOT_ID:
        logger.info(f"Bot was replied to (Bot ID: {BOT_ID}, Reply to ID: {message.reply_to_message.from_user.id})")
        should_respond = True
    
    # Case 2: Bot mentioned by username
    else:
        is_mentioned, cleaned_text = check_mentions(message.text)
        if is_mentioned:
            should_respond = True
            clean_text = cleaned_text or "Привет"
    
    # If the bot should respond, generate and send response
    if should_respond:
        logger.info(f"Generating response to: '{clean_text}'")
        response = generate_response(
            clean_text, 
            chat_id=message.chat.id, 
            user_id=message.from_user.id
        )
        bot.reply_to(message, response)

def main():
    """Start the bot"""
    logger.info("Starting Ruke bot using pyTelegramBotAPI...")
    
    # Get and store bot information
    global BOT_USERNAME, BOT_ID
    try:
        bot_info = bot.get_me()
        BOT_USERNAME = bot_info.username
        BOT_ID = bot_info.id
        
        logger.info(f"Bot started as @{BOT_USERNAME} (ID: {BOT_ID})")
        print("="*50)
        print(f"BOT STARTED AS @{BOT_USERNAME}")
        print("To interact with the bot in group chats:")
        print(f"1. Use command: /ryuk your message")
        print("2. Reply to the bot's messages")
        print("="*50)
        
        # Initialize the model
        if init_model():
            print("Model initialized successfully")
        else:
            print("WARNING: Failed to initialize any model. Bot will attempt to initialize on first message.")
        
    except Exception as e:
        logger.error(f"Error getting bot info: {e}")
    
    try:
        # Start the bot with better error handling
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    if not TELEGRAM_TOKEN:
        print("ERROR: Telegram token is not set. Please set the TELEGRAM_TOKEN environment variable.")
    else:
        main() 