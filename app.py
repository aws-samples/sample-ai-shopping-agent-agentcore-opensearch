"""
Simple Streamlit frontend for AI Shopping Agent.

Usage:
    streamlit run app.py

Prerequisites:
    - Agent deployed to AgentCore Runtime
    - AWS credentials configured with bedrock-agentcore:InvokeAgentRuntime permission
"""

import streamlit as st
import boto3
import json
import uuid

# ============================================================================
# CONFIGURATION
# ============================================================================

REGION = ""
AGENT_RUNTIME_ARN = ""

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="AI Shopping Assistant",
    page_icon="🛍️",
    layout="centered"
)

# ============================================================================
# Initialize Session State
# ============================================================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())


# ============================================================================
# Helper Functions
# ============================================================================

def invoke_agent(user_prompt: str) -> str:
    """Invoke the AgentCore Runtime with user prompt."""
    try:
        client = boto3.client("bedrock-agentcore", region_name=REGION)

        payload = json.dumps({"prompt": user_prompt})

        response = client.invoke_agent_runtime(
            agentRuntimeArn=AGENT_RUNTIME_ARN,
            runtimeSessionId=st.session_state.session_id,
            payload=payload.encode('utf-8')
        )

        # Read the response body
        response_body = response['response'].read().decode('utf-8')

        # Try to parse as JSON first
        try:
            response_data = json.loads(response_body)
            if isinstance(response_data, str):
                return response_data
            return json.dumps(response_data, indent=2)
        except json.JSONDecodeError:
            # Return as plain text if not JSON
            return response_body

    except Exception as e:
        return f"❌ Error invoking agent: {str(e)}"


# ============================================================================
# UI Layout
# ============================================================================

st.title("🛍️ AI Shopping Assistant")
st.markdown("Ask me anything about products!")

# Sidebar
with st.sidebar:
    st.header("💬 Chat Info")
    st.caption(f"Session: `{st.session_state.session_id[:8]}...`")

    if st.button("🔄 New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.divider()

    st.subheader("💡 Try asking:")
    st.markdown("""
    - Search for jackets under $50
    - Find men's clothing
    - Show me jewelry
    - What t-shirts are available?
    """)

    st.divider()
    st.caption("Powered by Amazon Bedrock AgentCore and Amazon OpenSearch Service")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if user_input := st.chat_input("Type your question here..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching..."):
            agent_response = invoke_agent(user_input)
            st.markdown(agent_response)

    # Add assistant response to chat
    st.session_state.messages.append({"role": "assistant", "content": agent_response})
