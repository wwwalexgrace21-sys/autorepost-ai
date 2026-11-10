import streamlit as st
from pathlib import Path
import tempfile, subprocess, json, textwrap
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg
from gtts import gTTS

st.set_page_config(page_title="AUTOPOST AI", page_icon="🎬", layout="wide")
st.title("🎬 AUTOPOST AI")
st.caption("Upload ordinary videos or create simple animated text-scene videos. Free starter version.")

with st.sidebar:
    st.header("Video settings")
    language = st.selectbox("Script language", ["မြန်မာ", "English"])
    aspect = st.selectbox("Video format", ["9:16 (TikTok / Shorts / Reels)", "16:9 (YouTube)"])
    seconds_per_scene = st.slider("Seconds per scene", 2, 7, 4)
    st.caption("Free text-scene video with optional Burmese narration. This does not generate realistic AI people or 3D footage.")

st.subheader("1. Upload an ordinary video")
uploaded = st.file_uploader("Choose an existing video", type=["mp4", "mov", "webm", "m4v"])
if uploaded:
    st.video(uploaded)
    st.download_button("Download original video", uploaded.getvalue(), uploaded.name, mime=uploaded.type or "video/mp4")
    st.markdown("#### Add Burmese voice to your uploaded video")
    voice_script = st.text_area(
        "စာဖတ်ပြမယ့် မြန်မာစာ",
        placeholder="ဒီ Video မှာ ပြောစေချင်တဲ့ စာသားကို ဒီမှာရေးပါ...",
        key="uploaded_voice_script"
    )
    if st.button("🔊 Add Burmese voice to uploaded video", disabled=not voice_script.strip()):
        with st.spinner("Adding Burmese voice to your video..."):
            work = Path(tempfile.mkdtemp(prefix="autopost_voice_"))
            original = work / uploaded.name
            original.write_bytes(uploaded.getvalue())
            audio_path = work / "burmese_voice.mp3"
            output = work / "video_with_burmese_voice.mp4"
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            try:
                gTTS(text=voice_script[:4500], lang="my", slow=False).save(str(audio_path))
                # Replace the original audio track with the Burmese narration.
                cmd = [ffmpeg, "-y", "-i", str(original), "-i", str(audio_path),
                       "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                       "-c:a", "aac", "-b:a", "128k", "-shortest",
                       "-movflags", "+faststart", str(output)]
                subprocess.run(cmd, check=True, capture_output=True)
                st.session_state["uploaded_voice_video"] = output.read_bytes()
                st.success("မြန်မာအသံကို Video ထဲ ထည့်ပြီးပါပြီ။ မူရင်း Video အသံကို အစားထိုးထားပါတယ်။")
            except Exception as e:
                st.error("အသံထည့်မရပါ။ Video format သို့မဟုတ် TTS အင်တာနက်ချိတ်ဆက်မှုကို စစ်ပါ။")
    if st.session_state.get("uploaded_voice_video"):
        st.video(st.session_state["uploaded_voice_video"])
        st.download_button("⬇️ Download video with Burmese voice",
                           st.session_state["uploaded_voice_video"],
                           "autopost_burmese_voice.mp4", "video/mp4")

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
    add_voice = st.checkbox("မြန်မာ AI အသံဖတ်ပြမှု ထည့်ရန် (အင်တာနက်လိုအပ်)", value=True)
    st.caption("Video is made from animated text scenes. Burmese voice uses the free gTTS service and may be unavailable if the service blocks requests.")
    if st.button("🎬 Render MP4 video", disabled=not scenes):
        with st.spinner("Creating your video. Please wait..."):
            work = Path(tempfile.mkdtemp(prefix="autopost_"))
            w, h = (720, 1280) if aspect.startswith("9:16") else (1280, 720)
            # Streamlit Community Cloud installs Noto Sans Myanmar from packages.txt.
            # Ask fontconfig for the actual font file rather than assuming a fixed path.
            font_path = None
            try:
                found = subprocess.run(
                    ["fc-match", "-f", "%{file}", "Noto Sans Myanmar"],
                    check=True, capture_output=True, text=True
                ).stdout.strip()
                if found and Path(found).exists():
                    font_path = found
            except Exception:
                pass
            if not font_path:
                candidates = [
                    "/usr/share/fonts/truetype/noto/NotoSansMyanmar-Regular.ttf",
                    "/usr/share/fonts/truetype/noto/NotoSansMyanmarUI-Regular.ttf",
                ]
                font_path = next((p for p in candidates if Path(p).exists()), None)
            try:
                engine = ImageFont.Layout.RAQM
                if font_path:
                    title_font = ImageFont.truetype(font_path, 48, layout_engine=engine)
                    body_font = ImageFont.truetype(font_path, 38, layout_engine=engine)
                    small_font = ImageFont.truetype(font_path, 24, layout_engine=engine)
                else:
                    raise RuntimeError("Noto Sans Myanmar font not found")
            except Exception:
                st.error("မြန်မာ Font မတွေ့ပါ။ packages.txt မှ fonts-noto-core ကို install လုပ်ပြီးမှ ပြန်စမ်းပါ။")
                st.stop()
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
                d.text((65, int(h*0.43)), hook[:90], font=title_font, fill="white", direction="ltr", language="my")
                wrapped = textwrap.wrap(scene, width=25 if w < h else 48)
                yy = int(h*0.56)
                for line in wrapped[:6]:
                    d.text((65,yy), line, font=body_font, fill=(225,235,245), direction="ltr", language="my")
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
            final_output = output
            if add_voice:
                narration = hook + "။ " + "။ ".join(scenes)
                audio_path = work / "narration.mp3"
                voiced_output = work / "autopost_ai_video_voice.mp4"
                try:
                    gTTS(text=narration[:4500], lang="my", slow=False).save(str(audio_path))
                    mux = [ffmpeg, "-y", "-i", str(output), "-i", str(audio_path),
                           "-filter:a", "apad", "-c:v", "copy", "-c:a", "aac",
                           "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(voiced_output)]
                    subprocess.run(mux, check=True, capture_output=True)
                    final_output = voiced_output
                    st.success("မြန်မာအသံဖတ်ပြမှု ထည့်ပြီးပါပြီ။")
                except Exception as e:
                    st.warning("အသံဖန်တီးမှု မအောင်မြင်ပါ။ အသံမပါသော Video ကို ဆက်ပေးထားပါတယ်။ အင်တာနက်ချိတ်ဆက်မှု သို့မဟုတ် TTS ဝန်ဆောင်မှုကို စစ်ပါ။")
            st.session_state["rendered_video"] = final_output.read_bytes()
            st.session_state["rendered_caption"] = caption + "\n\n" + hashtags
    if st.session_state.get("rendered_video"):
        st.video(st.session_state["rendered_video"])
        st.download_button("⬇️ Download MP4", st.session_state["rendered_video"], "autopost_ai_video.mp4", "video/mp4")
        st.download_button("⬇️ Download caption + hashtags", st.session_state["rendered_caption"], "caption.txt", "text/plain")

st.divider()
st.subheader("3. Social publishing")
st.info("Automatic publishing to TikTok, YouTube and Facebook is not connected yet. For now, download the MP4 and upload it to each platform. Official publishing needs each platform's authorization and API approval.")
st.caption("AUTOPOST AI V5 • Free starter build • Animated text scenes + optional Burmese TTS voice. Not realistic AI video generation.")
