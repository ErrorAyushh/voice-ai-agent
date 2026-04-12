import streamlit as st
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import tempfile
import os
import time

from stt import transcribe_audio
from intent import classify_intent
from tools import execute_tool

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Voice AI Agent",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ Voice-Controlled Local AI Agent")
st.caption("Speak or upload audio → Transcribe → Detect Intent → Execute")

# ── Session state ─────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "intent_result" not in st.session_state:
    st.session_state.intent_result = None
if "awaiting_confirm" not in st.session_state:
    st.session_state.awaiting_confirm = False
if "executed" not in st.session_state:
    st.session_state.executed = False

# ── Audio Input ───────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🎤 Record Mic", "📂 Upload File", "⌨️ Type Command"])

with tab1:
    duration = st.slider("Recording duration (seconds)", 5, 15, 8)
    st.info("💡 Click record, wait for countdown, then speak clearly.")
    if st.button("⏺️ Start Recording"):
        countdown_placeholder = st.empty()
        for i in range(3, 0, -1):
            countdown_placeholder.warning(f"🟡 Get ready... starting in {i}")
            time.sleep(1)
        countdown_placeholder.success("🔴 Recording NOW — Speak!")
        fs = 16000
        audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        countdown_placeholder.empty()
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav.write(tmp.name, fs, audio_data)
        st.success("✅ Recording complete!")
        st.audio(tmp.name)
        with st.spinner("🔊 Transcribing..."):
            st.session_state.transcript = transcribe_audio(tmp.name)
        st.session_state.intent_result = None
        st.session_state.awaiting_confirm = False
        st.session_state.executed = False

with tab2:
    st.info("💡 Record on phone, send to laptop, upload here for best results.")
    uploaded = st.file_uploader("Upload audio file", type=["wav", "mp3", "m4a", "ogg"])
    if uploaded:
        ext = uploaded.name.split('.')[-1]
        tmp = tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False)
        tmp.write(uploaded.read())
        tmp.flush()
        st.audio(uploaded)
        st.success("✅ File uploaded!")
        with st.spinner("🔊 Transcribing..."):
            st.session_state.transcript = transcribe_audio(tmp.name)
        st.session_state.intent_result = None
        st.session_state.awaiting_confirm = False
        st.session_state.executed = False

with tab3:
    st.info("💡 Type a command directly to test without audio.")
    text_cmd = st.text_input(
        "Type your command:",
        placeholder="Create a Python file called sort.py with bubble sort function"
    )
    if st.button("▶️ Run Command") and text_cmd:
        st.session_state.transcript = text_cmd
        st.session_state.intent_result = None
        st.session_state.awaiting_confirm = False
        st.session_state.executed = False

# ── Pipeline ──────────────────────────────────────────────────
if st.session_state.transcript:
    st.divider()

    # Step 1 — Show transcript
    st.subheader("📝 Step 1 — Transcription")
    st.info(st.session_state.transcript)

    # Step 2 — Classify intent (only if not done yet)
    if st.session_state.intent_result is None:
        with st.spinner("🧠 Detecting intent..."):
            st.session_state.intent_result = classify_intent(st.session_state.transcript)

    intent_result = st.session_state.intent_result
    intent_label = intent_result.get("intent", "unknown")

    st.subheader("🎯 Step 2 — Detected Intent")
    badge_color = {
        "write_code": "🟢",
        "create_file": "🔵",
        "summarize": "🟡",
        "chat": "⚪",
        "error": "🔴"
    }
    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric("Intent", f"{badge_color.get(intent_label, '⚪')} {intent_label}")
    with col2:
        st.json(intent_result.get("parameters", {}))

    # Step 3 — Execute
    if intent_label in ["create_file", "write_code"]:
        if not st.session_state.executed:
            st.warning("⚠️ This action will create/modify a file in `output/` folder.")
            if st.button("✅ Confirm & Execute", type="primary"):
                st.session_state.awaiting_confirm = True

            if st.session_state.awaiting_confirm:
                with st.spinner("⚙️ Executing action..."):
                    output, file_path = execute_tool(intent_result)
                st.session_state.executed = True
                st.subheader("✅ Step 3 — Result")
                st.markdown(output)
                if file_path and os.path.exists(file_path):
                    with open(file_path, "r") as f:
                        file_content = f.read()
                    st.download_button(
                        label="⬇️ Download Output File",
                        data=file_content,
                        file_name=os.path.basename(file_path),
                        mime="text/plain"
                    )
                st.session_state.history.append({
                    "transcript": st.session_state.transcript,
                    "intent": intent_label,
                    "output": output[:200] + "..." if len(output) > 200 else output
                })
    else:
        if not st.session_state.executed:
            with st.spinner("⚙️ Executing action..."):
                output, file_path = execute_tool(intent_result)
            st.session_state.executed = True
            st.subheader("✅ Step 3 — Result")
            st.markdown(output)
            st.session_state.history.append({
                "transcript": st.session_state.transcript,
                "intent": intent_label,
                "output": output[:200] + "..." if len(output) > 200 else output
            })

# ── New Command Button ────────────────────────────────────────
if st.session_state.executed:
    st.divider()
    if st.button("🔄 New Command"):
        st.session_state.transcript = None
        st.session_state.intent_result = None
        st.session_state.awaiting_confirm = False
        st.session_state.executed = False
        st.rerun()

# ── Session History ───────────────────────────────────────────
if st.session_state.history:
    st.divider()
    with st.expander(f"🕓 Session History ({len(st.session_state.history)} actions)"):
        for i, entry in enumerate(reversed(st.session_state.history)):
            idx = len(st.session_state.history) - i
            badge = badge_color.get(entry['intent'], '⚪') if 'badge_color' in locals() else '⚪'
            st.markdown(f"**#{idx}** {badge} `{entry['intent']}`")
            st.caption(f"🎤 {entry['transcript'][:100]}")
            st.caption(f"📤 {entry['output']}")
            st.divider()