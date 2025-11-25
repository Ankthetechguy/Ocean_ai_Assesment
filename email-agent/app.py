# app.py
import streamlit as st
import json
import os
from datetime import datetime
from typing import Dict, Any
from gemini_client import call_llm

DATA_DIR = "data"
MOCK_INBOX_FILE = os.path.join(DATA_DIR, "mock_inbox.json")
PROMPTS_FILE = os.path.join(DATA_DIR, "default_prompts.json")
PROCESSED_FILE = os.path.join(DATA_DIR, "processed.json")
DRAFTS_FILE = os.path.join(DATA_DIR, "drafts.json")

def read_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

inbox = read_json(MOCK_INBOX_FILE, default=[])
prompts = read_json(PROMPTS_FILE, default={})
processed = read_json(PROCESSED_FILE, default={})
drafts = read_json(DRAFTS_FILE, default={})

st.set_page_config(page_title="Prompt-Driven Email Agent", layout="wide")
st.title("📬 Prompt-Driven Email Productivity Agent (Streamlit + Gemini)")

# Sidebar: prompt brain and controls
with st.sidebar:
    st.header("Prompt Brain")
    cat_prompt = st.text_area("Categorization Prompt", value=prompts.get("categorization_prompt", ""), height=120)
    action_prompt = st.text_area("Action Item Prompt", value=prompts.get("action_item_prompt", ""), height=120)
    reply_prompt = st.text_area("Auto-reply Prompt", value=prompts.get("auto_reply_prompt", ""), height=140)

    if st.button("Save Prompts"):
        prompts["categorization_prompt"] = cat_prompt
        prompts["action_item_prompt"] = action_prompt
        prompts["auto_reply_prompt"] = reply_prompt
        write_json(PROMPTS_FILE, prompts)
        st.success("Prompts saved.")

    st.markdown("---")
    st.header("Batch Processing")
    st.markdown("Run categorization, extraction and draft generation across inbox.")
    if st.button("Run Batch Process"):
        if not inbox:
            st.error("No emails in mock inbox.")
        else:
            for email in inbox:
                eid = email["id"]
                email_text = f"Subject: {email['subject']}\nFrom: {email['sender']}\n\n{email['body']}"

                # Categorization
                cat_prompt_full = f"{prompts.get('categorization_prompt')}\n\nEmail:\n{email_text}"
                cat_out = call_llm(cat_prompt_full, system_instruction="You are an email categorizer.", temperature=0.0, max_tokens=50)

                # Action extraction
                action_prompt_full = f"{prompts.get('action_item_prompt')}\n\nEmail:\n{email_text}"
                action_out = call_llm(action_prompt_full, system_instruction="You are a JSON extractor that returns only a JSON array.", temperature=0.0, max_tokens=200)

                # Draft generation
                reply_prompt_full = f"{prompts.get('auto_reply_prompt')}\n\nEmail:\n{email_text}\n\nUser tone: professional, concise"
                draft_out = call_llm(reply_prompt_full, system_instruction="You are a helpful assistant that drafts email replies.", temperature=0.2, max_tokens=300)

                processed[eid] = {
                    "category": cat_out,
                    "actions_raw": action_out,
                    "draft_raw": draft_out,
                    "last_processed": datetime.utcnow().isoformat() + "Z"
                }

            write_json(PROCESSED_FILE, processed)
            st.success("Batch processing completed and saved to data/processed.json")

    st.markdown("---")
    has_key = bool(os.environ.get("GEMINI_API_KEY"))
    st.write(f"Gemini API key loaded: {'✅' if has_key else '❌'}")
    st.caption("Set GEMINI_API_KEY before running Streamlit. Use the Test button below to verify connectivity.")
    if st.button("Test Gemini connection"):
        # Run a small test to verify SDK/key
        with st.spinner("Testing Gemini..."):
            from gemini_client import test_connection
            result = test_connection()
            if result.startswith("ERROR_CALLING_GEMINI"):
                st.error(result)
            else:
                st.success("Gemini test OK")
                st.write(result)

# Main UI
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Inbox")
    if not inbox:
        st.info("Mock inbox empty. Put emails into data/mock_inbox.json")
    else:
        for email in inbox:
            eid = email["id"]
            cat = processed.get(eid, {}).get("category", "")
            label = f"{email['sender']} — {email['subject']} [{cat}]" if cat else f"{email['sender']} — {email['subject']}"
            if st.button(label, key=eid):
                st.session_state["selected_email"] = eid

with col2:
    sel = st.session_state.get("selected_email")
    if not sel:
        st.write("Select an email from the left to view details.")
    else:
        email = next((e for e in inbox if e["id"] == sel), None)
        if not email:
            st.error("Selected email not found.")
        else:
            st.markdown(f"### {email['subject']}")
            st.markdown(f"**From:** {email['sender']}  \n**Received:** {email['timestamp']}")
            st.markdown("**Body:**")
            st.write(email["body"])

            st.markdown("**Processed Data**")
            proc = processed.get(email["id"], {})
            st.json(proc)

            st.markdown("### Email Agent")
            user_q = st.text_input("Ask the agent about this email (e.g., 'Summarize', 'What tasks?', 'Draft reply in casual tone')", "")
            if st.button("Send Query"):
                if not user_q.strip():
                    st.warning("Type a question or instruction for the agent.")
                else:
                    # combine context + user question + reply prompt if requested
                    prompt_for_agent = f"Email:\nSubject: {email['subject']}\nFrom: {email['sender']}\nBody:\n{email['body']}\n\nUser instruction: {user_q}\n\nUse the following prompt templates when relevant:\nCategorization prompt:\n{prompts.get('categorization_prompt')}\n\nAction prompt:\n{prompts.get('action_item_prompt')}\n\nAuto-reply prompt:\n{prompts.get('auto_reply_prompt')}"
                    agent_out = call_llm(prompt_for_agent, system_instruction="You are an email assistant that uses the provided prompts when relevant.", temperature=0.2, max_tokens=400)
                    st.markdown("**Agent Response:**")
                    st.write(agent_out)

            st.markdown("### Drafts")
            existing = drafts.get(email["id"])
            if existing:
                st.write("Saved draft:")
                st.write(existing)
            else:
                if st.button("Save current generated draft"):
                    raw = proc.get("draft_raw", "")
                    if not raw:
                        st.warning("No draft available. Run batch processing or generate via agent.")
                    else:
                        drafts[email["id"]] = {
                            "subject": f"Re: {email['subject']}",
                            "body": raw,
                            "created": datetime.utcnow().isoformat() + "Z"
                        }
                        write_json(DRAFTS_FILE, drafts)
                        st.success("Draft saved to data/drafts.json")
