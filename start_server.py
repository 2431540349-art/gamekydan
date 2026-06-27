#!/usr/bin/env python3
"""
Automated startup script for DataGuard VN Quiz Game.
This script:
1. Runs database migrations (migrate.py)
2. Seeds initial questions & badges (seed_questions.py)
3. Starts a background ngrok tunnel if pyngrok is installed and NGROK_AUTHTOKEN is set.
4. Launches the Flask-SocketIO development server.
"""

import os
import sys
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_db_setup():
    print("=== [1/2] Database Setup ===")
    try:
        from migrate import migrate
        print("Running migrations...")
        migrate()
    except Exception as e:
        print(f"Error running database migrations: {e}")
        sys.exit(1)

    try:
        from seed_questions import seed
        print("Seeding database questions and badges...")
        seed()
    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)
    print("Database setup complete!\n")

def start_ngrok():
    print("=== [2/2] Optional Ngrok Tunnel ===")
    ngrok_token = os.getenv("NGROK_AUTHTOKEN")
    
    if not ngrok_token:
        print("Note: NGROK_AUTHTOKEN not found in environment/.env file.")
        print("To expose this server to the internet, add 'NGROK_AUTHTOKEN=your_token' to your .env file.")
        print("Running server locally only on http://localhost:5000\n")
        return None

    try:
        from pyngrok import ngrok, conf
        
        # Set auth token
        ngrok.set_auth_token(ngrok_token)
        
        # Open tunnel on port 5000
        print("Opening ngrok tunnel on port 5000...")
        public_url = ngrok.connect(5000, bind_tls=True).public_url
        print("=================================================================")
        print(f"🎉 ngrok tunnel active! Share this link for others to join:")
        print(f"👉 {public_url}")
        print("=================================================================\n")
        return public_url
    except ImportError:
        print("pyngrok package is not installed. To use ngrok tunnels, install it with:")
        print("  pip install pyngrok")
        print("Running server locally only on http://localhost:5000\n")
    except Exception as e:
        print(f"Failed to start ngrok tunnel: {e}")
        print("Running server locally only on http://localhost:5000\n")
    return None

def start_server():
    print("Starting Flask-SocketIO Server...")
    from app import app, socketio
    
    # Run the server
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    run_db_setup()
    
    # Start ngrok in background / prints link
    start_ngrok()
    
    # Start Flask server
    start_server()
