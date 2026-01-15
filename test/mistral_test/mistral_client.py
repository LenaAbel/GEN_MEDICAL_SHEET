import os
from pathlib import Path
from dotenv import load_dotenv
from mistralai import Mistral

# Load .env from parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


def get_mistral_client():
    """Initialize and return a Mistral client."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is not set")
    return Mistral(api_key=api_key)


def chat_with_mistral(prompt: str, model: str = "mistral-large-latest") -> str:
    """
    Send a prompt to Mistral LLM and return the response.
    
    Args:
        prompt: The user's input message
        model: The Mistral model to use (default: mistral-large-latest)
    
    Returns:
        The assistant's response text
    """
    client = get_mistral_client()
    
    response = client.chat.complete(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content


if __name__ == "__main__":
    # Example usage
    user_prompt = "Explain what a medical sheet is in one sentence."
    
    print(f"Prompt: {user_prompt}\n")
    response = chat_with_mistral(user_prompt)
    print(f"Response: {response}")