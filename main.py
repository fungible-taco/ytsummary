import streamlit as st
from utils import is_valid_youtube_url, get_video_info, main_func

# Page configuration
st.set_page_config(
    page_title="YouTube Video Summarizer",
    page_icon="🎥",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
    }
    .stTextArea > div > div > textarea {
        background-color: #f0f2f6;
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        color: #155724;
        margin: 1rem 0;
    }
    .error-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        color: #721c24;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# App title and description
st.title("🎥 YouTube Video Summarizer")
st.markdown("""
    Get quick summaries of YouTube videos using AI. Enter a video URL and optional context 
    to receive a comprehensive summary.
""")

# Input section
col1, col2 = st.columns([2, 1])

with col1:
    youtube_url = st.text_input(
        "YouTube Video URL",
        placeholder="https://www.youtube.com/watch?v=..."
    )

    context = st.text_area(
        "Additional Context (Optional)",
        placeholder="Enter any additional context or specific aspects you'd like the summary to focus on...",
        max_chars=2000,
        height=100
    )

    if st.button("Generate Summary", type="primary"):
        if not youtube_url:
            st.error("Please enter a YouTube URL")
        elif not is_valid_youtube_url(youtube_url):
            st.error("Please enter a valid YouTube URL")
        else:
            try:
                with st.spinner("Fetching video information..."):
                    video_info = get_video_info(youtube_url)

                st.success(f"Video found: {video_info['title']}")

                with st.spinner("Generating summary..."):
                    summary = main_func(youtube_url)

                # Display results
                st.markdown("### 📝 Summary")
                st.markdown(summary)

                # Display video metadata
                st.markdown("### 📊 Video Information")
                st.markdown(f"""
                    - **Title**: {video_info['title']}
                    - **Author**: {video_info['author']}
                    - **Duration**: {video_info['duration']} seconds
                    - **Views**: {video_info['views']:,}
                """)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

with col2:
    st.markdown("### How to use")
    st.markdown("""
        1. Paste a YouTube video URL
        2. (Optional) Add context or specific areas of interest
        3. Click 'Generate Summary'
        4. Wait for the AI to analyze and summarize

        **Note**: Processing time may vary depending on video length and complexity.
    """)

# Footer
st.markdown("---")
st.markdown(
    "Made with ❤️ using Streamlit, OpenAI Whisper, Llama and pytubefix | "
    "Remember to respect YouTube's terms of service"
)