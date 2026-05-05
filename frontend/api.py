"""
Flask API backend for the HTML/JS Shopping Assistant frontend.
Bridges browser requests to Amazon Bedrock AgentCore Runtime.

Usage:
    python3 api.py

This serves:
    - Static files (index.html, script.js, styles.css) on /
    - POST /chat endpoint that calls AgentCore Runtime
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import boto3
import json
import uuid
import os
import pathlib

# ============================================================================
# CONFIGURATION - Change these values for your environment
# ============================================================================

REGION = ""  # CHANGE THIS - Your AWS region (e.g., "us-east-1")
AGENT_RUNTIME_ARN = ""  # CHANGE THIS - From agentcore.py output (e.g., "arn:aws:bedrock-agentcore:us-east-1:accountid:runtime/search_agent-XXXXXXXX")

# ============================================================================

# Resolve the directory where this script lives (works both locally and on EC2)
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"[DEBUG] Serving static files from: {FRONTEND_DIR}")
print(f"[DEBUG] index.html exists: {os.path.isfile(os.path.join(FRONTEND_DIR, 'index.html'))}")

app = Flask(__name__)
CORS(app)

# Store session IDs per user
sessions = {}


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')

        # Get or create session for this user
        if user_id not in sessions:
            sessions[user_id] = str(uuid.uuid4())

        # Call AgentCore Runtime
        client = boto3.client("bedrock-agentcore", region_name=REGION)

        payload = json.dumps({"prompt": message})

        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            runtimeSessionId=sessions[user_id],
            payload=payload.encode('utf-8')
        )

        # Read the response
        response_body = response['response'].read().decode('utf-8')

        # Try to parse as JSON string (agent may return JSON-encoded string)
        try:
            parsed = json.loads(response_body)
            if isinstance(parsed, str):
                response_body = parsed
        except (json.JSONDecodeError, TypeError):
            pass

        # Clean up escaped newlines
        if "\\n" in response_body:
            response_body = response_body.replace("\\n", "\n")

        return jsonify({
            "success": True,
            "response": response_body
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/')
def serve_index():
    """Serve the main HTML page."""
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (JS, CSS, etc.)."""
    return send_from_directory(FRONTEND_DIR, filename)


if __name__ == '__main__':
    print(f"Starting Shopping Assistant API...")
    print(f"Region: {REGION}")
    print(f"Agent ARN: {AGENT_RUNTIME_ARN}")
    print(f"Open http://localhost:8080 in your browser")
    app.run(host='0.0.0.0', port=8501, debug=True)
