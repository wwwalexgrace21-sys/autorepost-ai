import streamlit as st
from pathlib import Path
import tempfile
import subprocess
import sys

st.set_page_config(page_title="AUTOPOST AI", page_icon="🎬", layout="wide")

st.markdown("""
<style>
.main {background: #0b1020;}
.block-container {max-width: 1100px; padding-top: 2rem;}
.hero {padding: 1.5rem; border-radius: 18px; background: linear-gradient(120deg,#18264a,#39245d); color:white;}
.small-note {color:#9aa7c7; font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🎬 AUTOPOST AI</h1><p>AI ideas + ordinary video upload + video studio</p><p class="small-note">Free starter prototype • Upload and prepare videos • Social publishing integration comes later</p></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📤 Upload Video", "✨ Create from Topic", "📅 Publishing Planner"])

with tab1:
    st.subheader("Upload an ordinary video")
    uploaded = st.file_uploader("Choose a video file", type=["mp4", "mov", "webm", "m4v"])
    if uploaded:
        data = uploaded.getvalue()
        st.video(data)
        st.success(f"Video loaded: {uploaded.name} • {len(data)/1024/1024:.1f} MB")
        st.download_button("Download original video", data=data, file_name=uploaded.name, mime=uploaded.type or "video/mp4")
        st.markdown("#### Prepare your post")
        caption = st.text_area("Caption", placeholder="Write a caption for your video...")
        hashtags = st.text_input("Hashtags", value="#video #content")
        platform = st.multiselect("Platforms to prepare for", ["TikTok", "YouTube Shorts", "Facebook Reels"], default=["YouTube Shorts"])
        post_text = caption.strip() + ("\n\n" + hashtags.strip() if hashtags.strip() else "")
        st.text_area("Post text preview", value=post_text, height=100)
        st.download_button("Download caption (.txt)", data=post_text, file_name="caption.txt", mime="text/plain", disabled=not post_text.strip())
        if platform:
            st.info("Prepared for: " + ", ".join(platform))
        st.caption("This starter lets you upload, preview, and prepare video posts. It does not publish to social accounts yet.")

with tab2:
    st.subheader("Create a simple video from a topic")
    topic = st.text_input("Video topic", placeholder="Example: 5 tips to save money")
    language = st.selectbox("Script language", ["Burmese", "English"])
    length = st.selectbox("Video format", ["Vertical 9:16 (Shorts/Reels/TikTok)", "Landscape 16:9"])
    if st.button("Generate storyboard", type="primary"):
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            if language == "Burmese":
                script = f"{topic} အကြောင်း သိထားသင့်တဲ့ အချက် ၅ ချက်။\\nပထမအချက် — အခြေခံအချက်ကို ရှင်းပြပါ။\\nဒုတိယအချက် — လက်တွေ့အသုံးချနည်းကို ပြပါ။\\nတတိယအချက် — သတိထားရမယ့်အချက်ကို ပြောပါ။\\nနောက်ဆုံး — ကြည့်ရှုပေးတဲ့အတွက် ကျေးဇူးတင်ပါတယ်။"
                scenes = [f"{topic}", "အချက် (၁) — အခြေခံကို သိပါ", "အချက် (၂) — လက်တွေ့အသုံးချပါ", "အချက် (၃) — သတိထားပါ", "Follow လုပ်ထားပါ"]
                caption = f"{topic} အကြောင်း အရေးကြီးတဲ့ အချက်များကို မျှဝေပေးထားပါတယ်။"
                tags = "#ဗဟုသုတ #အကြံပြုချက် #Shorts"
            else:
                script = f"Here are five useful points about {topic}.\\nFirst, understand the basics.\\nSecond, apply the idea in practice.\\nThird, avoid common mistakes.\\nThanks for watching."
                scenes = [topic, "1. Understand the basics", "2. Apply it in practice", "3. Avoid common mistakes", "Follow for more"]
                caption = f"Useful things to know about {topic}."
                tags = "#tips #learning #shorts"
            st.session_state["script"] = script
            st.session_state["scenes"] = scenes
            st.session_state["caption"] = caption
            st.session_state["tags"] = tags
    if "script" in st.session_state:
        st.markdown("#### Draft script")
        st.text_area("Edit your script", value=st.session_state["script"], height=160, key="script_edit")
        st.markdown("#### Storyboard")
        for i, scene in enumerate(st.session_state["scenes"], 1):
            st.write(f"**Scene {i}:** {scene}")
        st.text_area("Caption", value=st.session_state["caption"], key="caption_edit")
        st.text_input("Hashtags", value=st.session_state["tags"], key="tags_edit")
        st.info("This is a storyboard/text-card prototype, not a generative AI motion-video engine. Realistic AI motion generation needs a compatible model and substantial GPU or a free hosted service with usage limits.")

with tab3:
    st.subheader("Publishing planner")
    st.write("Prepare a checklist before publishing your video.")
    chosen = st.multiselect("Choose platforms", ["TikTok", "YouTube Shorts", "Facebook Reels"])
    when = st.date_input("Planned publishing date")
    st.write("Selected platforms:", ", ".join(chosen) if chosen else "None selected")
    st.write("Planned date:", when)
    st.warning("Automatic publishing is not connected in this starter. Official platform APIs, account authorization, and sometimes app review are required. Do not share your passwords with third-party tools.")

st.divider()
st.caption("AUTOPOST AI Starter • Free prototype. Public deployment requires the owner to publish this project to a hosting provider. Free hosting has limits.")
