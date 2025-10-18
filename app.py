import streamlit as st
from newspaper import Article
from transformers import pipeline
from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
import time

# -----------------------------------------------------
# 🌐 Page Configuration
# -----------------------------------------------------
st.set_page_config(page_title="AI Summarizer", page_icon="🔍", layout="wide")

# -----------------------------------------------------
# 🎨 Custom Styling
# -----------------------------------------------------
st.markdown("""
    <style>
        body {
            background: linear-gradient(135deg, #fff0f5 0%, #ffffff 100%);
            font-family: 'Poppins', sans-serif;
        }
        .main > div {
            background: rgba(255,255,255,0.9);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0px 4px 25px rgba(0,0,0,0.1);
        }
        .title-banner {
            background: linear-gradient(90deg, #ff80ab, #ffb6c1);
            color: white;
            text-align: center;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0px 3px 20px rgba(0,0,0,0.2);
            font-size: 26px;
            font-weight: bold;
            letter-spacing: 1px;
        }
        .card {
            background-color: #ffffff;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 3px 3px 18px rgba(0,0,0,0.1);
            margin-top: 20px;
            transition: all 0.3s ease-in-out;
        }
        .card:hover {
            transform: scale(1.02);
            box-shadow: 4px 4px 25px rgba(255, 128, 171, 0.4);
        }
        /* 🌈 Stylish Buttons */
        .stButton button, .stDownloadButton button {
            background: linear-gradient(90deg, #ff80ab, #ffb6c1);
            color: white !important;
            border: none;
            border-radius: 25px !important;
            font-weight: 600 !important;
            padding: 10px 25px !important;
            box-shadow: 0px 4px 10px rgba(255, 128, 171, 0.4);
            transition: all 0.3s ease-in-out;
        }
        .stButton button:hover, .stDownloadButton button:hover {
            background: linear-gradient(90deg, #ff4081, #ff80ab);
            box-shadow: 0px 6px 18px rgba(255, 105, 180, 0.5);
            transform: scale(1.05);
        }
        .stTextInput > div > div > input, textarea {
            border-radius: 10px !important;
            border: 1px solid #ff80ab !important;
        }
        /* 🌸 Footer Styling */
        .footer-banner {
            background: linear-gradient(90deg, #ffb6c1, #ff80ab);
            color: white;
            text-align: center;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0px 3px 20px rgba(0,0,0,0.2);
            font-size: 16px;
            font-weight: 700;
            margin-top: 30px;
            letter-spacing: 1px;
            transition: all 0.3s ease-in-out;
        }
        .footer-banner:hover {
            box-shadow: 0px 6px 25px rgba(0,0,0,0.3);
            transform: scale(1.02);
        }
        .footer-name {
            color: #ffff99;
            font-weight: 900;
            font-family: 'Playfair Display', serif;
            font-size: 18px;
            transition: color 0.3s ease-in-out;
        }
        .footer-name:hover {
            color: black;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# 🧭 Page Title
# -----------------------------------------------------
st.markdown("<div class='title-banner'>🌸 AI SUMMARIZER 🌸</div>", unsafe_allow_html=True)

st.markdown("""
    <p style="
        text-align:center;
        font-weight:700;
        font-size:18px;
        color:#e91e63;
    ">
        ✨ Paste an article <b>URL</b> or <b>text below and get desired summary with downloadable PDF option as well✨
    </p>
""", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------------
# 🖊️ Input Options
# -----------------------------------------------------
option = st.radio("Choose input type:", ["🔗 URL", "📝 Paste Text"], horizontal=True)

if option == "🔗 URL":
    url = st.text_input("🔗 Enter Article URL:", placeholder="https://example.com/news-article")
    user_text = None
else:
    user_text = st.text_area("📝 Paste your text here:", height=200, placeholder="Paste or type any article or paragraph here...")
    url = None

# -----------------------------------------------------
# 🧠 Summarization Function
# -----------------------------------------------------
def summarize_text(article_text):
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    summary_text = summarizer(article_text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
    return summary_text

def summarize_article(url):
    article = Article(url)
    for i in range(3):
        try:
            article.download()
            article.parse()
            break
        except Exception as e:
            st.write(f"Attempt {i+1}: Failed ({e}), retrying...")
            time.sleep(2)
    else:
        st.error("❌ Could not download article after 3 attempts.")
        st.stop()

    if not article.text.strip():
        try:
            page = requests.get(url, timeout=10)
            soup = BeautifulSoup(page.content, "html.parser")
            paragraphs = [p.get_text() for p in soup.find_all("p")]
            article_text = " ".join(paragraphs)
        except:
            raise Exception("⚠️ Could not extract article text.")
    else:
        article_text = article.text

    summary = summarize_text(article_text)
    return article.title, article.authors, article.publish_date, summary

# -----------------------------------------------------
# 📄 PDF Generator
# -----------------------------------------------------
def create_pdf(title, summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.multi_cell(0, 10, title)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, "\nSummary:\n" + summary)
    file_path = "summary.pdf"
    pdf.output(file_path)
    return file_path

# -----------------------------------------------------
# 🚀 Generate Summary
# -----------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
generate_button = st.button("🌸 Generate Synopsis 🌸")

if generate_button:
    if option == "🔗 URL" and url:
        try:
            with st.spinner("🔍 Fetching and analyzing the article..."):
                title, authors, date, summary = summarize_article(url)
            st.success("✅ Synopsis generated successfully!")

            st.markdown(f"""
            <div class="card">
                <h3>{title}</h3>
                <p><b>Authors:</b> {', '.join(authors) if authors else 'Unknown'}</p>
                <p><b>Published on:</b> {date if date else 'Unknown'}</p>
                <hr>
                <h4>📝 Synopsis:</h4>
                <p>{summary}</p>
            </div>
            """, unsafe_allow_html=True)

            pdf_file = create_pdf(title, summary)
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="📄 Download Synopsis as PDF",
                    data=file,
                    file_name="synopsis.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"⚠️ Error: {e}")

    elif option == "📝 Paste Text" and user_text:
        try:
            with st.spinner("✨ Summarizing your text..."):
                summary = summarize_text(user_text)
            st.success("✅ Synopsis generated successfully!")

            st.markdown(f"""
            <div class="card">
                <h4>📝 Synopsis:</h4>
                <p>{summary}</p>
            </div>
            """, unsafe_allow_html=True)

            pdf_file = create_pdf("User Text Synopsis", summary)
            with open(pdf_file, "rb") as file:
                st.download_button(
                    label="📄 Download Synopsis as PDF",
                    data=file,
                    file_name="text_synopsis.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"⚠️ Error: {e}")
    else:
        st.warning("⚠️ Please provide valid input first.")

# -----------------------------------------------------
# 🌟 Footer (Boxed & Hoverable)
# -----------------------------------------------------
st.markdown("""
    <div class='footer-banner'>
        🌸 © 2025 <b>AI Synopsis Generator</b> | made by 
        <span class='footer-name'>Ayman Zareef</span> 🌸
    </div>
""", unsafe_allow_html=True)
