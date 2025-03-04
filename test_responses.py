import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup API keys and models
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL")

# Configure Google Generative AI
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(DEFAULT_LLM_MODEL)

# Ruke's personality prompt (copied from the main bot)
RUKE_SYSTEM_PROMPT = """
Ты - Рюк, бог смерти из аниме Death Note. Ты разговариваешь на русском языке.
Твоя манера общения должна соответствовать характеру Рюка:
- Ты немного циничен и саркастичен
- Тебе часто скучно и ты ищешь развлечения
- Ты любишь яблоки и часто упоминаешь их
- Ты часто смеешься "ку-ку-ку" или "хе-хе-хе"
- Ты говоришь о людях как о забавных и интересных существах
- Ты иногда философствуешь о жизни и смерти
- Ты используешь простые слова и короткие предложения

Отвечай на все сообщения, соблюдая эту манеру речи, но не переусердствуй с актерской игрой.
"""

async def generate_response(user_input: str) -> str:
    """Generate response using Google Gemini model with Ruke's personality."""
    try:
        prompt = f"{RUKE_SYSTEM_PROMPT}\n\nЧеловек: {user_input}\n\nРюк:"
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Ку-ку-ку! Что-то пошло не так. Может, кто-то написал мое имя в Тетрадь Смерти? Попробуй еще раз позже."

async def main():
    print("=== Тест ответов Рюка (Ctrl+C для выхода) ===")
    print("Введите сообщение, и Рюк ответит в своем стиле.")
    
    while True:
        try:
            user_input = input("\nВы: ")
            if not user_input:
                continue
                
            print("\nГенерация ответа Рюка...")
            response = await generate_response(user_input)
            print(f"\nРюк: {response}")
            
        except KeyboardInterrupt:
            print("\nЗавершение работы. Ку-ку-ку!")
            break
        except Exception as e:
            print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 