import os
import logging
from dotenv import load_dotenv
import time

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
if not HUGGINGFACE_API_KEY:
    logger.error("No Hugging Face token found in environment variables!")
    exit(1)

logger.info(f"Using Hugging Face token: {HUGGINGFACE_API_KEY[:4]}...{HUGGINGFACE_API_KEY[-4:]}")

# Test models
DEFAULT_MODEL = "stabilityai/stable-diffusion-3.5-large"
TEST_PROMPT = "a shinigami watching over a city, dark fantasy style, detailed, 4k"

try:
    from huggingface_hub import InferenceClient
    from PIL import Image
    import io
    
    # Initialize client
    logger.info("Initializing Hugging Face client...")
    client = InferenceClient(token=HUGGINGFACE_API_KEY)
    logger.info("Client initialized")
    
    # First test: check if model can be accessed
    logger.info(f"Testing access to model: {DEFAULT_MODEL}")
    
    try:
        # Try to get model information
        logger.info("Checking model status...")
        
        # Some models may not have a status endpoint, so we'll just try to generate directly
        logger.info(f"Generating test image with prompt: {TEST_PROMPT}")
        start_time = time.time()
        
        # Generate image - using the correct method signature
        # Without parameters dictionary, just passing arguments directly
        image_result = client.text_to_image(
            prompt=TEST_PROMPT,
            model=DEFAULT_MODEL,
            negative_prompt="low quality, blurry, distorted",
            guidance_scale=7.5,
            num_inference_steps=25
        )
        
        generation_time = time.time() - start_time
        logger.info(f"Image generated successfully in {generation_time:.2f} seconds!")
        
        # Save the image - the API already returns a PIL Image
        output_file = "test_sd3_output.jpg"
        # No need to open with PIL, it's already a PIL Image
        image_result.save(output_file)
        logger.info(f"Image saved to {output_file}")
        
        # Also save to a byte buffer for testing how to convert to bytes
        img_byte_arr = io.BytesIO()
        image_result.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()
        logger.info(f"Successfully converted to bytes, size: {len(img_bytes)} bytes")
        
        print("\n✅ SUCCESS! The model worked with your token!")
        print(f"Image saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Error accessing model: {str(e)}")
        print("\n❌ ERROR: The model could not be accessed with your token.")
        print(f"Error message: {str(e)}")
        
        # Check if it's a permission error
        if "Not allowed" in str(e):
            print("\nThis appears to be a permission issue with your free token.")
            print("Free Hugging Face tokens have limited access to certain models.")
            print("You might need to:")
            print("1. Sign up for Hugging Face Pro")
            print("2. Try a different model that's available in the free tier")
            print("3. Continue using Pollinations.ai for image generation")
        
except ImportError as e:
    logger.error(f"Required library not found: {str(e)}")
    print(f"\nError: {str(e)}")
    print("Please install the required packages with:")
    print("pip install huggingface_hub pillow") 