import streamlit as st
from pathlib import Path
import tempfile, subprocess, json, textwrap
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

st.set_page_config(page_title="AUTOPOST AI", page_icon="🎬", layout="wide")
st.title("🎬 AUTOPOST AI")
st.caption("Upload ordinary videos or create simple animated text-scene videos. Free starter version.")

with st.sidebar:
    st.header("Video settings")
    language = st.selectbox("Script language", ["မြန်မာ", "English"])
    aspect = st.selectbox("Video format", ["9:16 (TikTok / Shorts / Reels)", "16:9 (YouTube)"])
    seconds_per_scene = st.slider("Seconds per scene", 2, 7, 4)
    st.caption("This free version uses editable text templates. It does not generate realistic AI people, 3D characters or cinematic footage.")

st.subheader("1. Upload an ordinary video")
uploaded = st.file_uploader("Choose an existing video", type=["mp4", "mov", "webm", "m4v"])
if uploaded:
    st.video(uploaded)
    st.download_button("Download original video", uploaded.getvalue(), uploaded.name, mime=uploaded.type or "video/mp4")

st.divider()
st.subheader("2. Create a simple motion video from a topic")
topic = st.text_input("Video topic", placeholder="ဥပမာ - အိမ်မှာ အသုံးဝင်တဲ့ နည်းပညာ ၅ ခု")
if st.button("Create script and scenes", type="primary", disabled=not topic.strip()):
    if language == "မြန်မာ":
        data = {
            "hook": f"{topic} အကြောင်း သိထားသင့်တဲ့ အချက်များ",
            "scenes": [
                f"{topic} ဆိုတာ ဘာလဲ။ အခြေခံကနေ စတင်လေ့လာကြရအောင်။",
                "ပထမဆုံး အရေးကြီးတဲ့ အချက်ကို နားလည်ထားဖို့ လိုပါတယ်။",
                "အသုံးဝင်တဲ့ နည်းလမ်းတွေကို လက်တွေ့ စမ်းသပ်ကြည့်နိုင်ပါတယ်။",
                "အသုံးမပြုခင် အချက်အလက်နဲ့ လုံခြုံရေးကို စစ်ဆေးပါ။",
                "ဒီအကြောင်းအရာကို ပိုမိုလေ့လာပြီး မိတ်ဆွေတွေနဲ့ မျှဝေပါ။"
            ],
            "caption": f"{topic} အကြောင်း အတိုချုံး မျှဝေထားပါတယ်။",
            "hashtags": "#ဗဟုသုတ #နည်းပညာ #မြန်မာ #Shorts"
        }
    else:
        data = {
            "hook": f"What to know about {topic}",
            "scenes": [
                f"What is {topic}? Start with the basic idea.",
                "Learn the most important point first.",
                "Try useful ideas carefully in real situations.",
                "Check facts and safety before taking action.",
                "Keep learning and share useful information."
            ],
            "caption": f"A quick introduction to {topic}.",
            "hashtags": "#learn #tips #explained #shorts"
        }
    st.session_state["draft"] = data

draft = st.session_state.get("draft")
if draft:
    st.markdown("#### Edit your video")
    hook = st.text_input("Opening title", value=draft["hook"], key="hook_edit")
    scene_text = st.text_area("Scene text (one scene per line)", value="\n".join(draft["scenes"]), height=180)
    caption = st.text_area("Post caption", value=draft["caption"])
    hashtags = st.text_input("Hashtags", value=draft["hashtags"])
    scenes = [x.strip() for x in scene_text.splitlines() if x.strip()]
    st.caption("The app creates animated text cards and combines them into an MP4. No paid AI service is used.")
    if st.button("🎬 Render MP4 video", disabled=not scenes):
        with st.spinner("Creating your video. Please wait..."):
            work = Path(tempfile.mkdtemp(prefix="autopost_"))
            w, h = (720, 1280) if aspect.startswith("9:16") else (1280, 720)
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            try:
                title_font = ImageFont.truetype(font_path, 48)
                body_font = ImageFont.truetype(font_path, 38)
                small_font = ImageFont.truetype(font_path, 24)
            except Exception:
                title_font = body_font = small_font = ImageFont.load_default()
            paths = []
            for i, scene in enumerate(scenes, 1):
                im = Image.new("RGB", (w,h), (12, 22, 42))
                d = ImageDraw.Draw(im)
                for y in range(h):
                    t = y / h
                    col = (int(10+12*t), int(22+18*t), int(45+28*t))
                    d.line((0,y,w,y), fill=col)
                d.rounded_rectangle((30,30,w-30,h-30), radius=32, outline=(70,145,205), width=3)
                d.text((65,75), "AUTOPOST AI", font=small_font, fill=(125,210,255))
                # Moving decorative orb gives each card a simple motion-like visual identity.
                cx = int(w * (0.25 + 0.5 * ((i % 2))))
                cy = int(h * 0.30)
                d.ellipse((cx-65,cy-65,cx+65,cy+65), fill=(32,105,160), outline=(130,210,255), width=4)
                d.text((65, int(h*0.43)), hook[:90], font=title_font, fill="white")
                wrapped = textwrap.wrap(scene, width=25 if w < h else 48)
                yy = int(h*0.56)
                for line in wrapped[:6]:
                    d.text((65,yy), line, font=body_font, fill=(225,235,245))
                    yy += 55
                d.text((65,h-100), f"Scene {i}/{len(scenes)}", font=small_font, fill=(150,205,235))
                p = work / f"scene_{i:02d}.png"
                im.save(p)
                paths.append(p)
            concat = work / "slides.txt"
            with concat.open("w", encoding="utf-8") as f:
                for p in paths:
                    f.write(f"file '{p.as_posix()}'\n")
                    f.write(f"duration {seconds_per_scene}\n")
                f.write(f"file '{paths[-1].as_posix()}'\n")
            output = work / "autopost_ai_video.mp4"
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            cmd = [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                   "-vf", "fps=24,format=yuv420p", "-r", "24", "-movflags", "+faststart", str(output)]
            subprocess.run(cmd, check=True, capture_output=True)
            st.session_state["rendered_video"] = output.read_bytes()
            st.session_state["rendered_caption"] = caption + "\n\n" + hashtags
    if st.session_state.get("rendered_video"):
        st.video(st.session_state["rendered_video"])
        st.download_button("⬇️ Download MP4", st.session_state["rendered_video"], "autopost_ai_video.mp4", "video/mp4")
        st.download_button("⬇️ Download caption + hashtags", st.session_state["rendered_caption"], "caption.txt", "text/plain")

st.divider()
st.subheader("3. Social publishing")
st.info("Automatic publishing to TikTok, YouTube and Facebook is not connected yet. For now, download the MP4 and upload it to each platform. Official publishing needs each platform's authorization and API approval.")
st.caption("AUTOPOST AI V2 • Free starter build • Text-template video generation, not realistic AI video generation.")
