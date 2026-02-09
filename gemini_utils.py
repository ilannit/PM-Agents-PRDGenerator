import requests
import base64
import json

def generate_content_rest(api_key, text, images=None, model_name="gemini-1.5-flash"):
    """
    Generates content using the Gemini API via standard REST HTTP request.
    This bypasses the google-generativeai library version issues.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Construct the payload
    contents = []
    parts = []
    
    # Add text part
    if text:
        parts.append({"text": text})
    
    # Add image parts if any
    if images:
        for image_bytes, mime_type in images:
            # Encode image to base64
            b64_data = base64.b64encode(image_bytes).decode('utf-8')
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": b64_data
                }
            })
            
    contents.append({"parts": parts})
    
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192,
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx, 5xx)
        
        result = response.json()
        
        # Parse the response to get the text
        if "candidates" in result and len(result["candidates"]) > 0:
            candidate = result["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0]["text"]
            else:
                 return "Error: Unexpected response structure from Gemini API."
        else:
             return "Error: No candidates returned from Gemini API."
             
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error: {e}"
        try:
            # Try to parse the error detail from the response body
            error_data = response.json()
            if "error" in error_data:
                error_msg += f"\nDetails: {json.dumps(error_data['error'], indent=2)}"
        except:
            pass
        return error_msg
    except Exception as e:
        return f"An error occurred: {e}"
