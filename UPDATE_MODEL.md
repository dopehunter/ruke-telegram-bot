# Update Gemini Model Name

The error you're seeing is because the model name format in your environment variables is not recognized by the Google Generative AI API.

## How to Fix:

1. In Replit, go to the **Secrets** tab in the left sidebar
2. Find the secret named `DEFAULT_LLM_MODEL`
3. Change its value from `gemini-2.0-flash-001` to one of the following:
   - `gemini-pro` (recommended)
   - `gemini-1.5-pro`
   - `gemini-1.5-flash`

4. After updating the secret, click on the **Stop** button and then **Run** again to restart your bot

This should resolve the "unexpected model name format" error and allow your bot to generate responses properly. 