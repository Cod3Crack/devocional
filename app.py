import os
import random
import requests
from flask import Flask, render_template, request, jsonify

# Initialize the Flask application
app = Flask(__name__)

# --- API Key Configuration ---
# IMPORTANT: It is highly recommended to store your API keys as environment variables
# for security. Hardcoding them here is a risk.
# Example for loading from environment variables:
# API_KEYS = os.getenv("GEMINI_API_KEYS", "").split(",")

# For demonstration purposes, the keys are listed here.
# PLEASE REPLACE THESE WITH YOUR OWN KEYS AND MOVE THEM TO ENVIRONMENT VARIABLES.
API_KEYS = [
    'AIzaSyDh7VMx3iIWJWLUjypzoTuZCSSmpGBPX_A',
    'AIzaSyAZVXmhJp4ZGLyGr9nSvnjJ0NoAVvPco-Y',
    'AIzaSyCTIIbrnMt_B3_w0oTE4nP-pC-eLPPODIA',
    'AIzaSyCgD165YrA5Eh9b5gVSi-R_BnHJleonq2Y',
    'AIzaSyBnDaGDJ8q92G61W7qv8WBYaASd3A77sYE',
    'AIzaSyBMJmQaKTIQDdT1UCIjhPo7JM1l5KXJx9E',
    'AIzaSyDkHKHzPkWkzsRHmUmvwBUdcHw0Wqbv0ZQ',
    'AIzaSyChlqSiRbljWspRqRJodIuluk9PLVhQQdU',
    'AIzaSyApSWJEpCaX_JO0qhegjBDz77aNgkHu9ec',
]

# --- Flask Routes ---

@app.route('/')
def index():
    """
    Renders the main page of the application.
    """
    return render_template('index.html')

@app.route('/correct', methods=['POST'])
def correct_text():
    """
    Handles the AI correction request for a single piece of text.
    """
    if not request.is_json:
        return jsonify({"error": "Invalid request: Content-Type must be application/json"}), 400

    data = request.get_json()
    conversation_history = data.get('history')

    if not conversation_history or not isinstance(conversation_history, list):
        return jsonify({"error": "Invalid data: 'history' array is required."}), 400

    # Prepare data for the Gemini API
    post_data = {
        'contents': conversation_history,
        'generationConfig': {
            'temperature': 0.3,
            'topK': 1,
            'topP': 1,
            'maxOutputTokens': 2048,
        },
        'safetySettings': [
            {'category': 'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
            {'category': 'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
            {'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
            {'category': 'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'BLOCK_MEDIUM_AND_ABOVE'},
        ]
    }

    # --- Try all API keys until one succeeds ---
    if not API_KEYS or not API_KEYS[0]:
         return jsonify({"error": "No API Keys have been configured on the server."}), 503

    shuffled_keys = random.sample(API_KEYS, len(API_KEYS))

    for api_key in shuffled_keys:
        api_url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'
        
        try:
            response = requests.post(api_url, json=post_data, timeout=20)
            
            if response.status_code == 200:
                response_data = response.json()
                bot_text = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                
                bot_text = bot_text.strip()
                if 'texto corregido:' in bot_text.lower():
                    bot_text = bot_text.split(':')[-1].strip()

                return jsonify({'response': bot_text})

        except requests.exceptions.RequestException as e:
            print(f"Connection error with key {api_key[:4]}...: {e}. Trying next key.")
            continue

    # If all keys failed
    return jsonify({
        "error": "All API Keys failed. The service may be temporarily unavailable."
    }), 503


if __name__ == '__main__':
    # Runs the Flask app. Use debug=False in a production environment.
    app.run(debug=True, port=5001)
