"""
This is a minimal standalone script to test image generation and sending with Telegram.
It uses a very simple approach to isolate any issues.
"""

import os
import logging
from dotenv import load_dotenv
import telebot
from huggingface_hub import InferenceClient
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API keys
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
CHAT_ID = os.getenv("TEST_CHAT_ID")  # Optional: Your chat ID for testing

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN not found in environment variables")
    exit(1)

if not HUGGINGFACE_API_KEY:
    logger.error("HUGGINGFACE_API_KEY not found in environment variables")
    exit(1)

if not CHAT_ID:
    logger.info("TEST_CHAT_ID not set. Will need to manually provide chat ID for testing.")
    CHAT_ID = input("Enter the chat ID to send the test image to: ")

# Initialize Telegram bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Initialize Hugging Face client
hf_client = InferenceClient(token=HUGGINGFACE_API_KEY)

# Generate and send a test image
def test_image_generation_and_sending():
    # Simple prompt
    prompt = "shinigami watching over a city, dark fantasy style, detailed"
    
    try:
        logger.info(f"Generating image with prompt: {prompt}")
        start_time = time.time()
        
        # Generate image with Stable Diffusion 3.5
        image = hf_client.text_to_image(
            prompt=prompt,
            model="stabilityai/stable-diffusion-3.5-large",
            negative_prompt="low quality, blurry",
            guidance_scale=7.5,
            num_inference_steps=25
        )
        
        logger.info(f"Image generated in {time.time() - start_time:.2f} seconds")
        
        # Save the image to a file
        image_path = "test_telegram_image.jpg"
        image.save(image_path)
        logger.info(f"Image saved to {image_path}")
        
        # Send the image to Telegram
        logger.info(f"Sending image to chat ID: {CHAT_ID}")
        with open(image_path, "rb") as photo:
            message = bot.send_photo(
                chat_id=CHAT_ID,
                photo=photo,
                caption="Test image generated with Stable Diffusion 3.5"
            )
        
        logger.info(f"Image sent successfully, message ID: {message.message_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("Starting test...")
    result = test_image_generation_and_sending()
    if result:
        logger.info("Test completed successfully!")
    else:
        logger.error("Test failed.") 