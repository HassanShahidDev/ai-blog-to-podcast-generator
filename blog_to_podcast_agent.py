import streamlit as st
import requests
from bs4 import BeautifulSoup
import ollama
import pyttsx3
import os

# -----------------------------------------------------
# Page UI Setup
# -----------------------------------------------------
st.set_page_config(page_title="📰 ➡️ 🎙️ Blog to Podcast (FREE)", page_icon="🎙️")
st.title("📰 ➡️ 🎙️ Blog to Podcast – FREE Version (Local Audio)")

# -----------------------------------------------------
# URL Input
# -----------------------------------------------------
url = st.text_input("Enter Blog URL:", "")

# -----------------------------------------------------
# Language Selection
# -----------------------------------------------------
language = st.radio(
    "🎧 Select Podcast Language:",
    ("English", "Urdu")
)

# -----------------------------------------------------
# TTS Function
# -----------------------------------------------------
def text_to_speech(summary, lang):
    engine = pyttsx3.init()
    
    voices = engine.getProperty("voices")

    # Urdu voice setup (Windows default Urdu voice)
    if lang == "Urdu":
        for v in voices:
            if "urdu" in v.name.lower() or "ur" in v.id.lower():
                engine.setProperty("voice", v.id)
    else:
        for v in voices:
            if "english" in v.name.lower() or "en" in v.id.lower():
                engine.setProperty("voice", v.id)

    engine.save_to_file(summary, "podcast.mp3")
    engine.runAndWait()

# -----------------------------------------------------
# MAIN ACTION
# -----------------------------------------------------
if st.button("🎙️ Generate Podcast"):
    if not url.strip():
        st.warning("Please enter a blog URL")
    else:
        try:
            # -------- SCRAPE BLOG --------
            with st.spinner("📄 Scraping blog content..."):
                page = requests.get(url)
                soup = BeautifulSoup(page.text, "html.parser")

                paragraphs = soup.find_all("p")
                text = "\n".join(p.get_text() for p in paragraphs)

                if len(text) < 500:
                    st.error("Blog content too short or scraping failed.")
                    st.stop()

            st.success("Scraping completed!")

            # -------- GENERATE SUMMARY --------
            with st.spinner("🧠 Generating summary using Qwen..."):

                if language == "Urdu":
                    prompt = f"""
                    Neeche diya gaya blog Urdu zaban me podcast narration jese andaaz me summarize karo.
                    Summary friendly, seedhi, conversational aur podcast wali style ho.

                    BLOG:
                    {text}
                    """
                else:
                    prompt = f"""
                    Summarize this blog article into a podcast-style narration.
                    Make it conversational, engaging, and clear.

                    BLOG:
                    {text}
                    """

                response = ollama.generate(model="qwen2.5:0.5b", prompt=prompt)
                summary = response.get("response", "")

            st.success(f"Summary ready in {language}!")

            # -------- GENERATE AUDIO --------
            with st.spinner("🎧 Generating podcast audio..."):
                text_to_speech(summary, language)

            st.success("Podcast audio ready!")

            # -------- AUDIO PLAYER --------
            st.audio("podcast.mp3")

            # -------- DOWNLOAD BUTTON --------
            st.download_button(
                "Download Podcast",
                open("podcast.mp3", "rb"),
                "podcast.mp3",
                "audio/mp3",
            )

            # -------- SHOW SUMMARY --------
            with st.expander(f"📄 {language} Podcast Summary"):
                st.write(summary)

        except Exception as e:
            st.error(f"Error: {e}")
