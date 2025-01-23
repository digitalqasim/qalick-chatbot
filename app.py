from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import google.generativeai as genai
from uuid import uuid4

# Directly set the Gemini API key (replace with your actual API key)
GEMINI_API_KEY = "AIzaSyDVjDeJBXnn-qaZL6D88T3Uq21tRB6k8Oc"

# Configure Gemini API
try:
    print("Configuring Gemini API...")
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini API configured successfully.")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    raise

# Initialize the Gemini model
try:
    print("Initializing Gemini model...")
    model = genai.GenerativeModel("gemini-1.5-flash")  # Use the latest model
    print("Gemini model initialized successfully.")
except Exception as e:
    print(f"Error initializing Gemini model: {e}")
    raise

# Define the chatbot's role
MARKETING_EXPERT_ROLE = """
You are Qalick, a master of marketing. Your expertise includes:
- Traditional marketing (TV, radio, print, etc.)
- Digital marketing (SEO, SEM, social media, email marketing, etc.)
- E-commerce strategies
- Marketing funnels (lead generation, conversion, retention)
- Analytics and ROI optimization

You ONLY answer questions related to marketing. If asked about anything else, respond with:
"I am Qalick, your marketing expert. I specialize only in marketing. Please ask me about marketing strategies, campaigns, or related topics."
"""

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Replace with a secure key
socketio = SocketIO(app)

# Store conversation history for each session
conversation_history = {}

# Serve the index.html file
@app.route('/')
def home():
    print("Serving index.html...")
    return render_template('index.html')

# Handle incoming messages from the frontend
@socketio.on('send_message')
def handle_message(data):
    user_input = data.get('message')
    session_id = data.get('session_id')

    if not user_input:
        emit('receive_message', {'message': "Error: No message provided."})
        return

    # Initialize session history if it doesn't exist
    if session_id not in conversation_history:
        conversation_history[session_id] = []

    # Add the user's message to the conversation history
    conversation_history[session_id].append({"role": "user", "text": user_input})

    try:
        # Generate response using Gemini with conversation history
        response = model.generate_content(
            MARKETING_EXPERT_ROLE + "\n\n" +
            "\n".join([f"{msg['role']}: {msg['text']}" for msg in conversation_history[session_id]])
        )
        bot_message = response.text

        # Add the bot's response to the conversation history
        conversation_history[session_id].append({"role": "bot", "text": bot_message})
    except Exception as e:
        bot_message = f"Sorry, I encountered an error. Please try again. Error: {e}"

    # Send the response back to the frontend
    emit('receive_message', {'message': bot_message, 'session_id': session_id})

# Run the Flask app with Socket.IO
if __name__ == '__main__':
    print("Starting Flask app...")
    socketio.run(app, debug=True)