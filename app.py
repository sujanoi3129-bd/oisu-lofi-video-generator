import streamlit as st
import subprocess
import os
import re
import imageio_ffmpeg as im_ffmpeg
import numpy as np

# librosa লাইব্রেরি লোড করা (বিট ডিটেকশনের জন্য)
try:
    import librosa
    import soundfile as sf
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

st.set_page_config(page_title="Lo-Fi Audio Copyright Remover", page_icon="🎵", layout="centered")

st.title("🎵 Lo-Fi Audio Copyright Remover & Real Beat Sync Creator")
st.write("সুজন ভাই, এবার আমরা গানের আসল বিট মেপে ছবিকে কাপাবো!")

if not LIBROSA_AVAILABLE:
    st.error("⚠️ গিটহাবের requirements.txt ফাইলে 'librosa' এবং 'soundfile' যোগ করে commit করুন, তারপর এখানে Rerun দিন।")

# অস্থায়ী ফাইল পাথসমূহ
audio_input = "temp_input_audio.mp3"
audio_processed = "temp_processed_audio.wav"
image_input = "temp_input_image.jpg"
video_output = "final_beat_sync_video.mp4"

if "step" not in st.session_state:
    st.session_state.step = 1

st.markdown(f"### 🎯 বর্তমান অবস্থান: **ধাপ {st.session_state.step}**")
st.markdown("---")

def run_ffmpeg_with_progress(cmd, status_text_display, total_duration=10.0):
    progress_bar = st.progress(0)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    time_regex = re.compile(r'time=(\d+):(\d+):(\d+\.\d+)')
    
    while True:
        line = process.stdout.readline()
        if not line:
            break
        match = time_regex.search(line)
        if match:
            hours, minutes, seconds = match.groups()
            current_time = float(hours)*3600 + float(minutes)*60 + float(seconds)
            percent = min(int((current_time / total_duration) * 100), 100)
            progress_bar.progress(percent / 100.0)
            status_text_display.markdown(f"⏳ আপনার ভিডিওটি তৈরি হচ্ছে: **{percent}%** সম্পন্ন")
            
    process.wait()
    progress_bar.progress(1.0)
    progress_bar.empty()

# ==========================================
# 🟢  ধাপ ১: ফাইল আপলোড ও প্রসেসিং
# ==========================================
if st.session_state.step == 1:
    st.header("Step ১: অডিও এবং রিলস ব্যাকগ্রাউন্ড ছবি আপলোড")
    
    uploaded_audio = st.file_uploader("🎵 আপনার মূল অডিও গানটি আপলোড করুন (MP3/WAV)", type=["mp3", "wav"])
    uploaded_image = st.file_uploader("📷 রিলসের জন্য লম্বা ব্যাকগ্রাউন্ড ছবিটি আপলোড করুন (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    voice_style = st.selectbox("🎛️ কপিরাইট প্রটেকশন ফিল্টার মোড:", [
        "🎵 Creative Lo-Fi Vibe (হালকা ইকো + ২% স্পিড চেঞ্জ + সেফ ফিল্টার)",
        "🔥 High Security Audio Changer (পিচ ভারী + ৩% স্পিড পরিবর্তন)"
    ])
    
    # সুজন ভাই, এখান থেকে বিটের পাওয়ার কতটা বাড়াতে চান তা সিলেক্ট করতে পারবেন
    beat_strength = st.slider("💥 ছবি কাঁপানোর পাওয়ার (Beat Shake Strength):", 1.0, 3.0, 1.8, step=0.1)
    
    if uploaded_audio is not None and uploaded_image is not None and LIBROSA_AVAILABLE:
        if st.button("🚀 রিয়েল বিট-সিঙ্ক ভিডিও তৈরি করুন"):
            status_text = st.empty()
            status_text.markdown("🎧 গানের বিট এবং সাউন্ড এনার্জি অ্যানালাইসিস করা হচ্ছে...")
            try:
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                for f in [audio_input, audio_processed, image_input, video_output]:
                    if os.path.exists(f): os.remove(f)
                
                with open(audio_input, "wb") as f:
                    f.write(uploaded_audio.read())
                with open(image_input, "wb") as f:
                    f.write(uploaded_image.read())
                
                # ১. কপিরাইট রিমুভাল অডিও প্রসেস করা
                if "High Security" in voice_style:
                    a_filter = "asetrate=44100*0.93,atempo=1.07,bass=g=4"
                else:
                    a_filter = "atempo=1.03,aecho=0.8:0.85:25:0.2,treble=g=2"
                
                cmd_audio = [ffmpeg_exe, '-y', '-i', audio_input, '-af', a_filter, audio_processed]
                subprocess.run(cmd_audio, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # ২. লিঁব্রোসা দিয়ে প্রসেসড অডিওর বিট ডাটা বের করা
                y, sr = librosa.load(audio_processed, sr=None)
                duration = librosa.get_duration(y=y, sr=sr)
                
                # প্রতি সেকেন্ডে ২৫ ফ্রেমের জন্য এনার্জি বের করা
                hop_length = int(sr / 25) 
                rms = librosa.feature.rms(y=y, frame_length=hop_length*2, hop_length=hop_length)[0]
                
                # এনার্জি নরমালইজ করা যাতে বেশি জোরে না কাঁপে
                if np.max(rms) > 0:
                    rms = rms / np.max(rms)
                
                # ৩. জুম এক্সপ্রেশন তৈরি করা (গানের প্রতি ফ্রেমে ছবির সাইজ পরিবর্তন হবে)
                # বেস জুম ১.০০, বিট আসলে সেটা বেড়ে যাবে
                zoom_expr = ""
                for idx, val in enumerate(rms[:int(duration*25)]):
                    z_val = 1.0 + (float(val) * 0.05 * beat_strength)
                    zoom_expr += f"eq(n,{idx})*{z_val:4f}+"
                zoom_expr += "1.0" # ডিফল্ট ব্যাকআপ
                
                status_text.markdown("🎬 গানের ছন্দে ভিডিও ফ্রেম সাজানো হচ্ছে...")
                
                # 🎯 ৪. এফএফএমপ্যাগ রান করা (বিটের এক্সপ্রেশনসহ)
                cmd_video = [
                    ffmpeg_exe, '-y',
                    '-loop', '1', '-r', '25', '-i', image_input,
                    '-i', audio_processed,
                    '-filter_complex', 
                    f"[0:v]scale=720:1280,zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2':s=720x1280:fps=25,setpts=PTS-STARTPTS[v]",
                    '-map', '[v]', '-map', '1:a',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '24',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-pix_fmt', 'yuv420p',
                    '-shortest', video_output
                ]
                
                run_ffmpeg_with_progress(cmd_video, status_text, total_duration=duration)
                
                if os.path.exists(video_output) and os.path.getsize(video_output) > 0:
                    st.session_state.step = 2
                    st.success("✅ ভিডিও সফলভাবে তৈরি হয়েছে!")
                    st.rerun()
                else:
                    st.error("❌ ভিডিও তৈরি করা সম্ভব হয়নি।")
                    
            except Exception as e:
                st.error(f"ত্রুটি ঘটেছে: {str(e)}")

# ==========================================
# 🟢  ধাপ ২: প্লেব্যাক এবং ডাউনলোড
# ==========================================
elif st.session_state.step == 2:
    st.header("Step ২: আপনার ফাইনাল ভিডিও ডাউনলোড করুন")
    
    if os.path.exists(video_output):
        st.markdown("### 📺 ভিডিও প্রিভিউ:")
        with open(video_output, "rb") as f:
            st.video(f.read())
            
        with open(video_output, "rb") as file:
            st.download_button(
                label="⬇️ গ্যালারিতে সেভ করুন (Download Music Reel)",
                data=file,
                file_name="sujon_real_beat_sync.mp4",
                mime="video/mp4"
            )
    else:
        st.error("আউটপুট ফাইলটি খুঁজে পাওয়া যায়নি।")
        
    st.markdown("---")
    if st.button("🔄 নতুন গান দিয়ে ভিডিও তৈরি করুন"):
        for f in [audio_input, audio_processed, image_input, video_output]:
            if os.path.exists(f): os.remove(f)
        st.session_state.step = 1
        st.rerun()
