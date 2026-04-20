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

REGION = "us-east-1"
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:652650038347:runtime/search_agent_2-wNW7PwFAyg"

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

def invoke_agent(user_prompt: str) -> dict:
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

        # Debug: print raw response to terminal
        print(f"[DEBUG] Raw response (first 200 chars): {repr(response_body[:200])}")

        # Clean up the response text
        cleaned = _clean_response(response_body)

        print(f"[DEBUG] Cleaned response (first 200 chars): {repr(cleaned[:200])}")

        # Return as dict with cleaned text and parsed products
        return {
            "text": cleaned,
            "products": extract_products(cleaned)
        }

    except Exception as e:
        return {
            "text": f"❌ Error invoking agent: {str(e)}",
            "products": []
        }


def _clean_response(text: str) -> str:
    """Clean up agent response: unescape, strip quotes, fix formatting."""
    import re

    # Try to parse as JSON string first (agent may return a JSON-encoded string)
    try:
        parsed = json.loads(text)
        if isinstance(parsed, str):
            text = parsed
    except (json.JSONDecodeError, TypeError):
        pass

    # If still contains literal \n, unescape them
    if "\\n" in text:
        text = text.replace("\\n", "\n")
    if "\\t" in text:
        text = text.replace("\\t", "\t")

    # Strip surrounding quotes if present
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
        # After stripping quotes, unescape again in case of double-encoding
        if "\\n" in text:
            text = text.replace("\\n", "\n")

    # Convert markdown links to images for image URLs
    # [View Image](https://...) or [any text](https://...img...) -> ![](url)
    text = re.sub(
        r'\[([^\]]*)\]\((https?://[^\)]*\.(?:png|jpg|jpeg|gif|webp)[^\)]*)\)',
        r'![\1](\2)',
        text,
        flags=re.IGNORECASE
    )

    # Escape $ signs so Streamlit doesn't interpret them as LaTeX
    text = text.replace("$", "\\$")

    return text.strip()


def extract_products(response_text: str) -> list:
    """Extract product information from agent response."""
    try:
        import re

        # Look for any JSON array in the response
        json_match = re.search(r'\[\s*\{.*?\}\s*\]', response_text, re.DOTALL)
        if json_match:
            products = json.loads(json_match.group(0))
            return products

        # Try to find "Found N products:" JSON block from the tool output
        found_match = re.search(r'Found \d+ products:\s*(\[.*?\])', response_text, re.DOTALL)
        if found_match:
            products = json.loads(found_match.group(1))
            return products

        # Parse image URLs from markdown-style links like [View Image](url)
        # or inline image references
        products = []
        image_pattern = re.compile(
            r'\*\*(.+?)\*\*.*?\$?([\d,]+\.?\d*)'
        )
        url_pattern = re.compile(r'(https://fakestoreapi\.com/img/[^\s\)]+)')

        lines = response_text.split('\n')
        current_product = {}

        for line in lines:
            # Look for product title in bold
            title_match = re.search(r'\*\*(.+?)\*\*', line)
            price_match = re.search(r'\$(\d+\.?\d*)', line)
            url_match = url_pattern.search(line)
            category_match = re.search(r'Category:\s*(.+)', line, re.IGNORECASE)

            if title_match and price_match:
                if current_product:
                    products.append(current_product)
                current_product = {
                    'title': title_match.group(1),
                    'price': float(price_match.group(1)),
                }
            elif title_match and not price_match and '–' in line or '-' in line:
                price_in_line = re.search(r'[\-–]\s*\$?(\d+\.?\d*)', line)
                if price_in_line:
                    if current_product:
                        products.append(current_product)
                    current_product = {
                        'title': title_match.group(1),
                        'price': float(price_in_line.group(1)),
                    }

            if url_match and current_product:
                current_product['image'] = url_match.group(1)
            if category_match and current_product:
                current_product['category'] = category_match.group(1).strip()

        if current_product:
            products.append(current_product)

        return products

    except Exception as e:
        print(f"Error extracting products: {e}")
        return []


def render_product_card(product: dict):
    """Render a product card with image."""
    col1, col2 = st.columns([1, 2])

    with col1:
        if product.get('image'):
            try:
                st.image(product['image'], use_container_width=True)
            except Exception as e:
                st.caption("🖼️ Image unavailable")

    with col2:
        st.markdown(f"**{product.get('title', 'N/A')}**")
        st.markdown(f"💰 ${product.get('price', 'N/A')}")
        if product.get('category'):
            st.caption(f"📂 {product['category']}")

    st.divider()


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

            # Display text response with inline images
            st.markdown(agent_response["text"])

    # Add assistant response to chat
    st.session_state.messages.append({"role": "assistant", "content": agent_response["text"]})
