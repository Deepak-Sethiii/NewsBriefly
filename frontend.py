import streamlit as st
import requests
from typing import Literal

# Constants
SOURCE_TYPES = Literal["news", "reddit", "both"]
BACKEND_URL = "http://localhost:1234"  # Update if backend runs on another port

def main():
    st.set_page_config(page_title="🗞️ NewsBriefly", layout="centered")
    st.title("🗞️ NewsBriefly")
    st.markdown("#### 📢 Get summaries of the latest trends from News & Reddit")

    # Initialize session state
    if 'topics' not in st.session_state:
        st.session_state.topics = []
    if 'input_key' not in st.session_state:
        st.session_state.input_key = 0

    # Sidebar
    with st.sidebar:
        st.header("Settings")
        source_type = st.selectbox(
            "Choose Source",
            options=["both", "news", "reddit"],
            format_func=lambda x: f"🌐 {x.capitalize()}" if x == "news" else f"💬 {x.capitalize()}" if x == "reddit" else "🌀 Both"
        )

    # Add topic
    st.markdown("### 📝 Add Topic")
    col1, col2 = st.columns([4, 1])
    with col1:
        new_topic = st.text_input(
            "Enter a topic (e.g. AI, Bitcoin)",
            key=f"topic_input_{st.session_state.input_key}"
        )
    with col2:
        add_disabled = len(st.session_state.topics) >= 3 or not new_topic.strip()
        if st.button("➕ Add", disabled=add_disabled):
            st.session_state.topics.append(new_topic.strip())
            st.session_state.input_key += 1
            st.rerun()

    # Show selected topics
    if st.session_state.topics:
        st.markdown("### ✅ Selected Topics")
        for i, topic in enumerate(st.session_state.topics):
            cols = st.columns([4, 1])
            cols[0].write(f"{i + 1}. {topic}")
            if cols[1].button("❌ Remove", key=f"remove_{i}"):
                del st.session_state.topics[i]
                st.rerun()

    st.markdown("---")
    st.subheader("📄 Summary Output")

    # Generate summary
    if st.button("🚀 Generate Summary", disabled=len(st.session_state.topics) == 0):
        if not st.session_state.topics:
            st.warning("Please add at least one topic.")
        else:
            with st.spinner("Generating summary..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/generate-news-summary",
                        json={
                            "topics": st.session_state.topics,
                            "source_type": source_type
                        }
                    )

                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Summary generated successfully!")
                        st.text_area("📝 News Summary", value=result["summary"], height=400)

                    else:
                        handle_api_error(response)

                except requests.exceptions.ConnectionError:
                    st.error("🔌 Could not connect to the backend server.")
                except Exception as e:
                    st.error(f"⚠️ Unexpected Error: {str(e)}")

def handle_api_error(response):
    try:
        error_detail = response.json().get("detail", "Unknown error")
        st.error(f"API Error ({response.status_code}): {error_detail}")
    except ValueError:
        st.error(f"Unexpected API Response: {response.text}")

if __name__ == "__main__":
    main()
