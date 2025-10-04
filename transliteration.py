import google.generativeai as genai
import time

def get_gemini_response(
    prompt: str,
    api_key: str,
    system_prompt: str = "You are a helpful AI assistant",
    model_name: str = "gemini-1.5-flash",
    temperature: float = 0.9,
    max_output_tokens: int = 2048,
    max_retries: int = 3
) -> str:
    """
    Get response from Gemini API with system prompt support and robust error handling
    
    Args:
        prompt: User input prompt
        api_key: Gemini API key
        system_prompt: System instruction to guide model behavior [1][2]
        model_name: Valid model name (default: gemini-1.5-flash)
        temperature: Creativity control (0.0-1.0)
        max_output_tokens: Response length limit
        max_retries: Number of retry attempts for API errors
        
    Returns:
        Generated text response or error message
    """
    # Configure API key
    genai.configure(api_key=api_key)
    
    try:
        # Initialize model with system prompt
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_prompt
        )
        
        # Start chat session
        chat = model.start_chat(history=[])
        
        # Retry mechanism for API errors
        for attempt in range(max_retries):
            try:
                # Send request with generation config
                response = chat.send_message(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                        max_output_tokens=max_output_tokens
                    )
                )
                
                # Return text if response is valid
                if response.text:
                    return response.text
                else:
                    return "Error: Empty response from model"
                    
            except genai.types.BlockedPromptException as e:
                return f"Error: Content blocked - {e}"
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                raise
    
    except Exception as e:
        return f"API Error: {str(e)}"


response = get_gemini_response(
    prompt=input("Enter text to transliterate to Kanglish: "),
    api_key="AIzaSyDvbqgXET_e6ThTMvEql6OAl8LbgyyqmP4",
    system_prompt="""You are a transliteration assistant that converts English sentences into Kanglish (Kannada written in English letters, not Kannada script).

Rules:
- Translate only the words that have Kannada equivalents into Kanglish.
- Keep modern English words like "mobile", "internet", "college", "software" as they are, unless there is a very common Kanglish equivalent.
- The output must be natural Kanglish, as people usually text in chat. 
- Do not output Kannada script, only English letters.
- Keep sentence structure casual, like everyday Kannada speech.

Example Conversions:
Input: "Hey bro, how are you?"
Output: "Hey bro, hegiddiya?"

Input: "I will call you in the evening."
Output: "Nan nin ge evening call madtini."

Input: "Let's go to college tomorrow."
Output: "Naale college ge hogona."
""",
    temperature=0.7
)

print(response)
