import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Fynd AI Feedback System", layout="wide")
DATA_FILE = "reviews_data.csv"

# --- API SETUP ---
# Try to get key from Secrets (for deployed version) or Sidebar (for testing)
api_key = st.secrets.get("GEMINI_API_KEY") 

# --- HELPER FUNCTIONS ---
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["timestamp", "rating", "review", "ai_response", "ai_summary", "ai_action"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def get_gemini_response(prompt, key):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["User Dashboard", "Admin Dashboard"])

# If key is missing in secrets, ask for it
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not api_key:
    st.warning("⚠️ Waiting for API Key to start...")
    st.stop()

# ==========================================
# PAGE 1: USER DASHBOARD (Public Facing)
# ==========================================
if page == "User Dashboard":
    st.title("📝 Customer Feedback")
    st.write("Share your experience with us!")

    with st.form("review_form"):
        rating = st.slider("Rate your experience:", 1, 5, 5)
        review_text = st.text_area("Write your review here:", height=150)
        submitted = st.form_submit_button("Submit Review")

        if submitted and review_text:
            with st.spinner("AI is analyzing your feedback..."):
                # 1. Generate User Reply
                user_prompt = f"Write a short, polite response to a customer who gave a {rating}-star rating and wrote: '{review_text}'"
                ai_reply = get_gemini_response(user_prompt, api_key)

                # 2. Generate Admin Insights
                admin_prompt = f"Analyze this review: Rating {rating}, Text: '{review_text}'. 1. Summarize in 1 sentence. 2. Suggest 1 action. Output format: Summary | Action"
                admin_analysis = get_gemini_response(admin_prompt, api_key)
                
                if "|" in admin_analysis:
                    summary, action = admin_analysis.split("|", 1)
                else:
                    summary, action = admin_analysis, "Manual Review Needed"

                # 3. Save Data
                new_data = pd.DataFrame({
                    "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "rating": [rating],
                    "review": [review_text],
                    "ai_response": [ai_reply],
                    "ai_summary": [summary.strip()],
                    "ai_action": [action.strip()]
                })
                
                df = load_data()
                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)

            st.success("Thank you! Your feedback has been recorded.")
            st.info(f"**Our Response:** {ai_reply}")

# ==========================================
# PAGE 2: ADMIN DASHBOARD (Internal Facing)
# ==========================================
elif page == "Admin Dashboard":
    st.title("📊 Admin Insights")
    st.write("Live feed of incoming reviews and AI analysis.")

    df = load_data()

    if df.empty:
        st.info("No reviews yet.")
    else:
        # Analytics
        col1, col2 = st.columns(2)
        col1.metric("Total Reviews", len(df))
        col1.metric("Average Rating", f"{df['rating'].mean():.1f} ⭐")
        col2.bar_chart(df["rating"].value_counts())

        # Data Table
        st.subheader("Recent Submissions")
        st.dataframe(df[["timestamp", "rating", "review", "ai_summary", "ai_action"]].sort_values(by="timestamp", ascending=False))