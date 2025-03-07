# Test script for Hugging Face API

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the token
token = os.getenv("HUGGINGFACE_API_KEY", "")

if not token:
    print("ERROR: No Hugging Face API key found in .env file")
    print("Please add HUGGINGFACE_API_KEY=your_token to your .env file")
    exit(1)

print(f"Found token: {token[:4]}...{token[-4:]}")

try:
    # Try to import required libraries
    from huggingface_hub import InferenceClient
    from PIL import Image
    import io
    print("Hugging Face library imported successfully")
except ImportError:
    print("ERROR: huggingface_hub package not installed")
    print("Install with: pip install huggingface_hub pillow")
    exit(1)

# Test models
test_models = [
    "stabilityai/stable-diffusion-3.5-large",  # Known to work with free API
    "runwayml/stable-diffusion-v1-5",  # Base model - might work
    "stabilityai/stable-diffusion-xl-base-1.0"  # Higher quality - might not work with free API
]

try:
    # Create client
    client = InferenceClient(token=token)
    print("Successfully created Hugging Face client")
    
    # Check each model
    for model in test_models:
        try:
            print(f"\nTesting model: {model}")
            
            # Generate faster with our known working model
            print(f"Attempting to generate a test image with {model}...")
            test_prompt = "a simple apple on a wooden table"
            
            # Generate image with direct parameters (not using parameters dictionary)
            image_result = client.text_to_image(
                prompt=test_prompt,
                model=model,
                negative_prompt="low quality, blurry",
                guidance_scale=7.5,
                num_inference_steps=20
            )
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            image_result.save(img_byte_arr, format='JPEG')
            img_bytes = img_byte_arr.getvalue()
            
            # Save the image
            filename = f"test_{model.split('/')[-1]}.jpg"
            with open(filename, "wb") as f:
                f.write(img_bytes)
            
            print(f"SUCCESS! Generated image saved to {filename}")
            print(f"Image size: {len(img_bytes)} bytes")
            
        except Exception as e:
            print(f"ERROR testing {model}: {str(e)}")
    
except Exception as e:
    print(f"ERROR creating client: {str(e)}")
    exit(1)

print("\nTest completed!") 