import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

st.markdown("""
    <style>
        /* Force ALL visible text elements to black */
        html, body, [class*="st-"], [class^="st-"], .stApp, .block-container {
            color: black !important;
            background-color: white !important;
        }

        /* Fix text input box */
        input, textarea {
            background-color: white !important;
            color: black !important;
        }

        /* Specific fix for text input in Streamlit */
        .stTextInput input {
            background-color: white !important;
            color: black !important;
        }

        /* Fix buttons */
        .stButton button {
            background-color: #f0f0f0 !important;
            color: black !important;
            font-weight: bold;
            border-radius: 5px;
            border: 1px solid #ccc;
        }

        .stButton button:hover {
            background-color: #dcdcdc !important;
        }

        /* Fix headings and markdown text */
        h1, h2, h3, h4, h5, h6, p, span, label, div {
            color: black !important;
        }

        /* Fix any alert/info/success box */
        .stAlert, .stInfo {
            color: black !important;
        }
        /* Fix for answer input boxes always being white with black text */
        input, textarea, .stTextInput input {
            background-color: white !important;
            color: black !important;
        }
    
    </style>
""", unsafe_allow_html=True)

# ---------- Load API Key ----------
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/mistral-7b-instruct"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ---------- Streamlit Page Setup ----------
st.set_page_config(page_title="TalentScout AI Hiring Assistant", page_icon="🤖")
st.markdown("""
    <style>
    .big-font {
        font-size:28px !important;
        font-weight: bold;
        color: #4CAF50;
    }
    .small-font {
        font-size:16px !important;
        color: #888;
    }
        /* Fix label (question) visibility */
        label, .css-1cpxqw2 {
        color: #ffffff !important;
        font-weight: bold;
}
        /* Make info messages readable */
        .css-1cpxqw2, .stAlert-info {
        background-color: #1f2937 !important;
        color: #f0f0f0 !important;
        border-left: 6px solid #3b82f6 !important;
}
        /* Improve text input box appearance */
        input[type="text"], input[type="email"], textarea {
        background-color: #2d3748 !important;
        color: #ffffff !important;
        border: 1px solid #4a5568 !important;
        padding: 8px !important;
        border-radius: 6px !important;
    }
s
     
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">🤖 TalentScout AI Hiring Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="small-font">I\'m your assistant to help you apply. Let\'s begin 👇</p>', unsafe_allow_html=True)

# ---------- Session State Init ----------
if "step" not in st.session_state:
    st.session_state.step = 0
if "data" not in st.session_state:
    st.session_state.data = {}
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = None
if "tech_questions" not in st.session_state:
    st.session_state.tech_questions = []
if "answers" not in st.session_state:
    st.session_state.answers = []

# ---------- LLM Call ----------
def ask_llm(prompt):
    try:
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful AI hiring assistant."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            return None
    except Exception as e:
        return None

# ---------- Static Questions ----------
static_questions = [
    ("👤 What's your full name?", "name"),
    ("📧 Email Address:", "email"),
    ("📞 Phone Number:", "phone"),
    ("📍 Current Location:", "location"),
    ("💼 Years of Experience:", "experience"),
    ("🎯 Desired Role:", "role"),
    ("💻 List your tech stack (comma separated):", "tech_stack")
]

# ---------- Question Flow ----------
if st.session_state.step < len(static_questions):
    question, key = static_questions[st.session_state.step]
    default = st.session_state.data.get(key, "")
    ans = st.text_input(question, value=default, key=f"q_{st.session_state.step}")
    if st.button("Next ➡️", key=f"n_{st.session_state.step}"):
        if not ans.strip():
            st.warning("⚠️ Please fill out this field before proceeding.")
        else:
            st.session_state.data[key] = ans.strip()
            st.session_state.step += 1
            st.rerun()

    if st.session_state.step > 0:
        if st.button("Edit Previous ⬅️", key=f"back_{st.session_state.step}"):
            st.session_state.step -= 1
            st.rerun()

# ---------- Generate Technical Questions ----------
elif st.session_state.step == len(static_questions):
    st.info(f"📩 Alright {st.session_state.data.get('name', '')}, let's move to a few technical questions based on your skills in {st.session_state.data['tech_stack']}.")
    prompt = f"Generate 3 concise and challenging interview questions based on the following tech stack: {st.session_state.data['tech_stack']}. Keep them on point and diverse."
    questions = ask_llm(prompt)
    if questions:
        st.session_state.tech_questions = [q.strip() for q in questions.strip().split("\n") if q.strip()]
        st.session_state.step += 1
        st.rerun()
    else:
        st.error("⚠️ Could not fetch technical questions. Try again later.")

# ---------- Tech Q&A Step ----------
elif len(static_questions) <= st.session_state.step < len(static_questions) + 1 + len(st.session_state.tech_questions):
    idx = st.session_state.step - len(static_questions) - 1
    question = st.session_state.tech_questions[idx]
    default = st.session_state.answers[idx] if idx < len(st.session_state.answers) else ""
    ans = st.text_area(f"🧪 {question}", value=default, key=f"tech_{idx}")

    if st.button("Next ➡️", key=f"next_tech_{idx}"):
        if not ans.strip():
            st.warning("⚠️ Please write your answer before continuing.")
        else:
            if idx < len(st.session_state.answers):
                st.session_state.answers[idx] = ans.strip()
            else:
                st.session_state.answers.append(ans.strip())
            st.session_state.step += 1
            st.rerun()

    if idx > 0:
        if st.button("Edit Previous ⬅️", key=f"back_tech_{idx}"):
            st.session_state.step -= 1
            st.rerun()

# ---------- Final Review and Submission ----------
elif st.session_state.step == len(static_questions) + 1 + len(st.session_state.tech_questions):
    st.subheader("📋 Review Your Application")
    for key, value in st.session_state.data.items():
        st.markdown(f"**{key.replace('_', ' ').title()}**: {value}")
        if st.button(f"Edit", key=f"edit_{key}"):
            st.session_state.step = [k for k, v in static_questions].index(key)
            st.rerun()

    for i, q in enumerate(st.session_state.tech_questions):
        st.markdown(f"**Q{i+1}: {q}**")
        st.markdown(f"📝 {st.session_state.answers[i]}")
        if st.button(f"Edit Answer {i+1}", key=f"edit_ans_{i}"):
            st.session_state.step = len(static_questions) + 1 + i
            st.rerun()

    if st.button("✅ Submit Application"):
        candidate = st.session_state.data.copy()
        candidate["technical_questions"] = list(zip(st.session_state.tech_questions, st.session_state.answers))
        candidate["timestamp"] = str(datetime.now())

        try:
            with open("candidates.json", "r") as f:
                existing = json.load(f)
        except:
            existing = []

        existing.append(candidate)
        with open("candidates.json", "w") as f:
            json.dump(existing, f, indent=4)

        st.success(f"📩 Thank you {st.session_state.data['name']}! Your application has been submitted. We’ll contact you if you’re shortlisted.")
        st.info("✅ You may now close the application.")
        st.balloons()













