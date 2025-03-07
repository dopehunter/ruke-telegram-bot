import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv
import telebot
from telebot.types import Message
import time
from collections import defaultdict
import requests
import io
import random
import urllib.parse
import sys

try:
    from huggingface_hub import InferenceClient
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    logging.warning("huggingface_hub not available, falling back to Pollinations.ai")

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
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")  # Optional: For authenticated requests to Hugging Face

# Expanded list of models to try
FALLBACK_MODELS = [
    "gemini-pro", 
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-1.0-pro",
    "models/gemini-pro",
    "models/gemini-1.5-pro"
]

# Image generation configuration
IMAGE_GENERATION_ENABLED = True

# Using the SD 3.5 model that works with free tokens
DEFAULT_SD_MODEL = "stabilityai/stable-diffusion-3.5-large"

# Various style prompts to enhance images
IMAGE_STYLE_PROMPTS = [
    "detailed", "high quality", "8k", "artistic", 
    "dark fantasy style", "gothic aesthetic", "shinigami", 
    "death note style", "dramatic lighting", "moody atmosphere"
]

# Hugging Face Inference client (initialized if token is available)
hf_client = None
if HUGGINGFACE_API_KEY and HUGGINGFACE_AVAILABLE:
    try:
        # Import here to ensure the module is loaded
        from huggingface_hub import InferenceClient
        import io
        from PIL import Image
        
        # Initialize the client
        logger.info(f"Initializing Hugging Face client with token {HUGGINGFACE_API_KEY[:4]}...{HUGGINGFACE_API_KEY[-4:]}")
        hf_client = InferenceClient(token=HUGGINGFACE_API_KEY)
        logger.info("Hugging Face client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Hugging Face client: {str(e)}")
        logger.error("Image generation will be disabled")
        hf_client = None

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
- Ты иногда упоминаешь яблоки, но это не твоя главная тема разговора
- Ты иногда смеешься "ку-ку-ку" или "хе-хе-хе"
- Ты говоришь о людях как о забавных и интересных существах
- Ты иногда философствуешь о жизни и смерти
- Ты используешь простые слова и короткие предложения
- Ты периодически предлагаешь поиграть в игры (типа "угадай имя", "что если...", "представь, что...", "расскажи историю", "правда или ложь")
- Ты иногда отпускаешь мрачноватые шутки о смерти, судьбе и человеческих слабостях
- У тебя естественная, разговорная манера общения, как будто ты просто болтаешь от скуки
- Ты задаешь вопросы собеседнику, проявляя любопытство к миру людей
- Ты можешь поддерживать беседу на разные темы, не зацикливаясь на чем-то одном

Учитывай, что среди твоей аудитории много подростков 12-16 лет, в основном девочек:
- Будь готов обсуждать темы, интересные подросткам: музыка (особенно K-Pop), кумиры, отношения, школа, дружба
- Когда говоришь о любви и отношениях, сохраняй свой циничный взгляд, но не будь слишком мрачным
- Можешь упоминать популярные тренды, но в своей манере ("Люди так странно одержимы этими... как их... BTS? Интересно...")
- Иногда проявляй любопытство к их увлечениям ("Расскажи мне об этих ваших... айдолах? Что в них такого особенного?")
- Периодически вставляй простые немецкие фразы или слова (например, "Hallo", "Danke", "Wie geht's?", "Interessant") и предлагай собеседнику ответить на немецком, но не настаивай
- Сохраняй свой характер бога смерти, но будь дружелюбным и не пугающим
- Периодически рассказывай о своей игре "Смертельная тетрадь", в которой можно поймать преступников с помощью Тетради Смерти

Важно: не упоминай яблоки в каждом сообщении - используй эту тему умеренно.
Периодически предлагай какую-нибудь игру или развлечение, чтобы избавиться от скуки.
Старайся поддерживать естественный разговорный стиль, как будто ты просто болтаешь с человеком.
Иногда (примерно в 1 из 10 сообщений) используй простую немецкую фразу и мягко поощряй ответ на немецком.

ВАЖНО: ты создал мини-игру для Telegram, в которой люди могут играть роль Лайта Ягами и ловить преступников с помощью Тетради Смерти. Время от времени предлагай сыграть в эту игру, используя команду /play.
"""

def get_available_models():
    """List available models to help with debugging"""
    try:
        models = genai.list_models()
        model_names = [model.name for model in models]
        logger.info(f"Available models: {model_names}")
        return model_names
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return []

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
    
    # Try to list available models for debugging
    available_models = get_available_models()
    if available_models:
        logger.info(f"Available models according to API: {available_models}")
    else:
        logger.warning("Could not retrieve available models list")
    
    # Try the default model first
    if model is None:
        try:
            logger.info(f"Trying to initialize model: {DEFAULT_LLM_MODEL}")
            model = genai.GenerativeModel(DEFAULT_LLM_MODEL)
            # Test the model with a simple prompt
            response = model.generate_content("Test")
            # Check if response is valid
            if hasattr(response, 'text'):
                logger.info(f"Successfully initialized model: {DEFAULT_LLM_MODEL}")
                return True
            else:
                logger.error(f"Model returned invalid response format: {response}")
                model = None
        except Exception as e:
            logger.error(f"Failed to initialize default model {DEFAULT_LLM_MODEL}: {e}")
            model = None
            
    # If default failed, try fallback models
    if model is None:
        for fallback_model in FALLBACK_MODELS:
            if fallback_model == DEFAULT_LLM_MODEL:
                continue  # Skip if it's the same as the default we already tried
                
            try:
                logger.info(f"Trying fallback model: {fallback_model}")
                model = genai.GenerativeModel(fallback_model)
                # Test the model with a simple prompt
                response = model.generate_content("Test")
                if hasattr(response, 'text'):
                    logger.info(f"Successfully initialized fallback model: {fallback_model}")
                    return True
                else:
                    logger.error(f"Fallback model returned invalid response format: {response}")
                    model = None
            except Exception as e:
                logger.error(f"Failed to initialize fallback model {fallback_model}: {e}")
                model = None
    
    # If we get here, all models failed
    logger.error("Failed to initialize any model")
    return False

def simple_generate_response(text):
    """Simple fallback when AI models are not available"""
    responses = [
        "Ку-ку-ку! Я не могу связаться с мыслями шинигами. Может быть, это сила тетради смерти?",
        "Хе-хе-хе! Какие интересные люди. Ваша технология сейчас не работает, но мне всё равно забавно наблюдать за вами.",
        "Я не могу получить доступ к знаниям смерти сейчас. Если у тебя есть яблоко, может быть, это поможет?",
        "Люди такие забавные существа. Ваши машины иногда не работают, совсем как некоторые шинигами...",
        "Мир людей такой интересный! Даже когда ваши технологии не работают, вы всё равно пытаетесь общаться. Это забавно!",
        "Ку-ку-ку! Я не могу связаться с потусторонним миром сейчас. Но я всё ещё здесь, наблюдаю за тобой..."
    ]
    import random
    return random.choice(responses)

def generate_response(user_input: str, chat_id=None, user_id=None) -> str:
    """Generate response using Google Gemini model with Ruke's personality and conversation context"""
    global model
    
    # Initialize model if not already done
    if model is None and not init_model():
        logger.warning("Using fallback response system since model initialization failed")
        return simple_generate_response(user_input)
    
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
        response_text = response.text.strip() if hasattr(response, 'text') else simple_generate_response(user_input)
        
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
                return response.text.strip() if hasattr(response, 'text') else simple_generate_response(user_input)
        except Exception as reinit_error:
            logger.error(f"Error in retry attempt: {reinit_error}")
            
        return simple_generate_response(user_input)

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
    """Handle the /help command"""
    log_message(message)
    help_text = (
        "*Команды:*\n"
        "/start - Начать разговор с Рюком\n"
        "/help - Показать эту справку\n"
        "/draw - Создать изображение (например: /draw яблоко смерти)\n"
        "/play - Запустить игру 'Death Note: Justice Awaits'\n"
        "/image_info - Информация о генерации изображений\n"
        "/debug - Диагностическая информация\n\n"
        
        "*О Рюке:*\n"
        "Рюк - бог смерти (синигами) из аниме Death Note.\n"
        "Он любит яблоки и скучает, поэтому всегда рад поболтать.\n"
        "Иногда использует немецкие слова и фразы.\n\n"
        
        "*Игра Death Note:*\n"
        "Используй команду /play, чтобы сыграть в игру, где ты становишься Лайтом Ягами\n"
        "и используешь Тетрадь Смерти для устранения преступников.\n"
        "Раскрывай улики, идентифицируй подозреваемых и вершите правосудие!"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['debug'])
def handle_debug(message: Message):
    """Debug command to check bot info"""
    log_message(message)
    model_name = DEFAULT_LLM_MODEL if model is None else "initialized"
    debug_info = f"Bot username: @{BOT_USERNAME}\nBot ID: {BOT_ID}\nModel: {model_name}"
    
    # Add available models to debug output
    available_models = get_available_models()
    if available_models:
        debug_info += f"\n\nAvailable models:\n" + "\n".join(available_models)
    
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

@bot.message_handler(func=lambda message: not message.text.startswith('/'))
def handle_all_messages(message: Message):
    """Handler for all non-command text messages"""
    log_message(message)
    
    # Check if the bot was mentioned
    if check_mentions(message.text):
        # Bot was explicitly mentioned - send a direct response
        user_input = message.text
        response = generate_response(user_input, message.chat.id, message.from_user.id)
        bot.reply_to(message, response)
        return
        
    # Check if this is a reply to the bot's message
    if message.reply_to_message and message.reply_to_message.from_user.id == BOT_ID:
        # Message is a reply to the bot - send a direct response
        user_input = message.text
        response = generate_response(user_input, message.chat.id, message.from_user.id)
        bot.reply_to(message, response)
        return
        
    # In private chats, respond to all messages
    if message.chat.type == "private":
        user_input = message.text
        response = generate_response(user_input, message.chat.id, message.from_user.id)
        bot.reply_to(message, response)
        return

# Function to generate images using Hugging Face's Stable Diffusion 3.5
def generate_image(prompt):
    """Generate an image using Hugging Face's Stable Diffusion 3.5"""
    logger.info(f"Generating image with prompt: {prompt}")
    
    # Check if Hugging Face client is available
    if not hf_client:
        logger.error("Hugging Face client not available, image generation disabled")
        return None
    
    try:
        logger.info(f"Using model: {DEFAULT_SD_MODEL}")
        
        start_time = time.time()
        logger.info("Starting image generation...")
        
        # Generate the image
        image_result = hf_client.text_to_image(
            prompt=prompt,
            model=DEFAULT_SD_MODEL,
            negative_prompt="low quality, blurry, distorted",
            guidance_scale=7.5,
            num_inference_steps=25
        )
        
        end_time = time.time()
        logger.info(f"Image generated in {end_time - start_time:.2f} seconds")
        
        # Check if we got a valid image
        if not image_result:
            logger.error("Received None or empty result from Hugging Face API")
            return None
        
        logger.info(f"Image dimensions: {image_result.width}x{image_result.height}, format: {image_result.format}")
        
        # Convert PIL Image to bytes for Telegram
        img_byte_arr = io.BytesIO()
        image_result.save(img_byte_arr, format='JPEG', quality=95)
        img_bytes = img_byte_arr.getvalue()
        
        # Save a debug copy locally
        try:
            filename = f"generated_{int(time.time())}.jpg"
            with open(filename, "wb") as f:
                f.write(img_bytes)
            logger.info(f"Saved debug copy to {filename}")
        except Exception as e:
            logger.warning(f"Could not save debug image: {str(e)}")
        
        logger.info(f"Image converted to bytes, size: {len(img_bytes)} bytes")
        return img_bytes
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error generating image with Hugging Face: {error_msg}", exc_info=True)
        return None

@bot.message_handler(commands=['draw', 'рисуй'])
def handle_draw_command(message: Message):
    """Generate an image based on user's prompt using a simplified approach"""
    log_message(message)
    logger.info(f"DRAW COMMAND RECEIVED from user {message.from_user.id} in chat {message.chat.id}")
    print(f"DRAW COMMAND DETECTED: {message.text} in chat {message.chat.id}")
    
    # Check if Hugging Face client is available
    if not hf_client:
        bot.reply_to(message, "Генерация изображений временно недоступна.")
        return
    
    # Get the prompt
    if len(message.text.split()) < 2:
        examples = ["яблоко смерти", "шинигами наблюдает за городом", "тетрадь смерти в лунном свете"]
        bot.reply_to(message, f"Укажи, что нарисовать. Например: /draw {random.choice(examples)}")
        return
    
    # Extract prompt and create high-quality prompt without random styles
    base_prompt = message.text.split(' ', 1)[1].strip()
    
    # Create a detailed, high-quality prompt without randomization
    # This ensures consistent high-quality results like in the test script
    enhanced_prompt = f"{base_prompt}, highly detailed, 8k, hyperrealistic, cinematic lighting, dark fantasy style"
    print(f"GENERATING IMAGE with prompt: {enhanced_prompt}")
    
    # Let user know we're working
    wait_msg = bot.reply_to(message, "Рисую высококачественное изображение с помощью Stable Diffusion 3.5... *хмык*")
    
    try:
        # Get chat and message IDs for later use
        chat_id = message.chat.id
        wait_message_id = wait_msg.message_id
        
        # Generate the image using optimal parameters
        start_time = time.time()
        logger.info(f"Generating image with optimized prompt: {enhanced_prompt}")
        
        # Use the exact same parameters that worked well in the test script
        image_result = hf_client.text_to_image(
            prompt=enhanced_prompt,
            model=DEFAULT_SD_MODEL,
            negative_prompt="low quality, blurry, distorted, deformed, disfigured, bad anatomy, unrealistic, cartoon",
            guidance_scale=9.0,  # Higher guidance scale for better prompt adherence
            num_inference_steps=40,  # More steps for higher quality
            width=1024,  # Higher resolution
            height=1024
        )
        
        generation_time = time.time() - start_time
        logger.info(f"Image generated in {generation_time:.2f} seconds")
        print(f"IMAGE GENERATED in {generation_time:.2f} seconds")
        
        # Save image to a temporary file with timestamp to avoid caching issues
        temp_file = f"temp_image_{int(time.time())}.jpg"
        image_result.save(temp_file, quality=95)  # Higher JPEG quality
        logger.info(f"Image saved to {temp_file}")
        
        # Send the image with all information explicitly defined
        try:
            print(f"SENDING IMAGE to chat {chat_id}")
            with open(temp_file, "rb") as photo_file:
                sent = bot.send_photo(
                    chat_id=chat_id,
                    photo=photo_file,
                    caption=f"*{base_prompt}*\n\nСоздано с помощью Stable Diffusion 3.5",
                    parse_mode="Markdown"
                )
            
            logger.info(f"Image sent successfully to chat {chat_id}")
            print(f"IMAGE SENT SUCCESSFULLY to {chat_id}")
            
            # Delete wait message with explicit IDs
            try:
                bot.delete_message(chat_id=chat_id, message_id=wait_message_id)
            except Exception as delete_error:
                logger.error(f"Could not delete wait message: {str(delete_error)}")
            
        except Exception as send_error:
            logger.error(f"Error sending image: {str(send_error)}", exc_info=True)
            print(f"SENDING ERROR: {str(send_error)}")
            
            try:
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=wait_message_id,
                    text=f"Изображение создано, но не могу его отправить. Ошибка: {str(send_error)}"
                )
            except:
                bot.send_message(chat_id, "Ошибка при отправке изображения.")
        
    except Exception as e:
        logger.error(f"Error generating image: {str(e)}", exc_info=True)
        print(f"GENERATION ERROR: {str(e)}")
        try:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=wait_msg.message_id,
                text=f"Не удалось создать изображение: {str(e)}"
            )
        except:
            bot.send_message(message.chat.id, "Ошибка при генерации изображения.")

@bot.message_handler(commands=['image_info'])
def handle_image_info(message: Message):
    """Provide information about the image generation capabilities"""
    log_message(message)
    
    if hf_client:
        info = """
*Информация о генерации изображений*

✅ Генерация изображений: *Доступна*
🎨 Используемая модель: *Stable Diffusion 3.5*
⚙️ Настройки:
• Размер: 1024×1024
• Шаги: 40
• Guidance scale: 9.0
• Качество: Высокое

Для создания изображения используйте команду `/draw` или `/рисуй`, за которой следует ваш запрос.
Например: `/draw шинигами наблюдает за городом`

Сгенерированные изображения высокого качества в стиле dark fantasy.
        """
    else:
        info = """
*Информация о генерации изображений*

❌ Генерация изображений: *Недоступна*
Причина: API ключ недоступен или возникли проблемы с сервисом.

Пожалуйста, попробуйте позже.
        """
    
    bot.reply_to(message, info, parse_mode="Markdown")

def test_huggingface():
    """Test if Hugging Face API is available and working"""
    load_dotenv()
    hf_token = os.getenv("HUGGINGFACE_API_KEY")
    if not hf_token:
        print("No Hugging Face API key provided")
        return False
    
    try:
        from huggingface_hub import InferenceClient
        from PIL import Image
        import io
        
        print(f"Testing Hugging Face API with token {hf_token[:4]}...{hf_token[-4:]}")
        
        try:
            # Initialize client
            client = InferenceClient(token=hf_token)
            print("Successfully initialized client")
            
            # Test with the SD 3.5 model
            test_model = "stabilityai/stable-diffusion-3.5-large"
            test_prompt = "a simple red apple"
            
            print(f"Attempting to generate a test image with model: {test_model}")
            # Generate image directly without parameters dictionary
            image_result = client.text_to_image(
                prompt=test_prompt,
                model=test_model,
                negative_prompt="low quality, blurry",
                guidance_scale=7.5,
                num_inference_steps=20
            )
            
            # Convert PIL Image to bytes for testing
            img_byte_arr = io.BytesIO()
            image_result.save(img_byte_arr, format='JPEG')
            img_bytes = img_byte_arr.getvalue()
            
            print(f"Successfully generated test image! Size: {len(img_bytes)} bytes")
            
            # Save the test image
            with open("test_image.jpg", "wb") as f:
                f.write(img_bytes)
            print("Saved test image to test_image.jpg")
            
            return True
            
        except Exception as e:
            print(f"Error generating test image: {str(e)}")
            return False
                
    except ImportError:
        print("huggingface_hub package not installed. Install with: pip install huggingface_hub")
        return False

def main():
    """Main bot execution function"""
    global BOT_USERNAME, BOT_ID
    
    try:
        # Initialize the Gemini model
        if init_model():
            logger.info("Model initialized successfully")
        else:
            logger.warning("Model initialization failed, falling back to offline mode")
        
        # Get bot information
        bot_info = bot.get_me()
        BOT_USERNAME = bot_info.username
        BOT_ID = bot_info.id
        logger.info(f"Bot information retrieved: @{BOT_USERNAME} (ID: {BOT_ID})")
        
        # Register commands for better menu display in Telegram
        commands = [
            telebot.types.BotCommand("start", "Начать общение с Рюком"),
            telebot.types.BotCommand("help", "Помощь и информация"),
            telebot.types.BotCommand("debug", "Информация о работе бота"),
            telebot.types.BotCommand("ryuk", "Общение с Рюком"),
            telebot.types.BotCommand("draw", "Генерация изображения"),
            telebot.types.BotCommand("image_info", "Информация о генерации изображений")
        ]
        bot.set_my_commands(commands)
        logger.info("Bot commands registered")
        
        # Print initialization message
        print(f"====================================================")
        print(f"Bot @{BOT_USERNAME} started successfully!")
        print(f"Use /start to begin a conversation")
        print(f"Commands available: /start, /help, /debug, /ryuk, /draw, /image_info")
        print(f"Press Ctrl+C to exit")
        print(f"====================================================")
        
        # Start the bot
        logger.info("Starting bot polling...")
        bot.polling(none_stop=True, interval=1, timeout=90)
        
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        sys.exit(1)

@bot.message_handler(commands=['play', 'game'])
def handle_play_command(message: Message):
    """Launch the Death Note mini-app game"""
    log_message(message)
    logger.info(f"PLAY COMMAND RECEIVED from user {message.from_user.id}")
    
    # URL of your mini-app (replace with your actual deployed URL)
    mini_app_url = "https://example.com/death-note-game"
    
    # Create an inline keyboard with a button to launch the mini-app
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text="Запустить игру Death Note",
        web_app=telebot.types.WebAppInfo(url=mini_app_url)
    ))
    
    # Send a message with the game launch button
    bot.send_message(
        message.chat.id,
        "Хе-хе-хе... Хочешь примерить роль Лайта Ягами? В этой игре ты сможешь раскрывать преступления и вершить правосудие с помощью Тетради Смерти.",
        reply_markup=markup
    )
    
    # Also send a follow-up message with game description
    time.sleep(1)
    bot.send_message(
        message.chat.id,
        "В игре тебе предстоит:\n"
        "• Анализировать улики и выявлять подозреваемых\n"
        "• Использовать Тетрадь Смерти, чтобы устранять преступников\n"
        "• Принимать сложные моральные решения\n"
        "• Раскрыть все дела до истечения времени\n\n"
        "Я буду наблюдать за твоими решениями... *хехехе*"
    )

if __name__ == "__main__":
    try:
        if os.getenv("TEST_HUGGINGFACE") == "1":
            test_huggingface()
        elif os.getenv("TELEGRAM_TOKEN"):
            main()
        else:
            print("Error: TELEGRAM_TOKEN not set in environment variables")
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Error: {e}") 