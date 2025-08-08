import requests

def get_suggested_message_ollama(original_text):
    payload = {
        "model": "llama3",
        "prompt": f"Suggest a short and friendly reply to this message:\n\n{original_text}",
        "stream": False
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        return f"Error generating suggestion: {str(e)}"
