import streamlit as st
import subprocess
import os
import re
import imageio_ffmpeg as im_ffmpeg

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Lo-Fi Audio Copyright Remover", page_icon="🎵", layout="centered")

st.title("🎵 Lo-Fi Audio Copyright Remover & Reels Creator")
st.write("সুjon ভাই, আপনার আগের আসল কোডটি এখানে দেওয়া হলো। এবার রিলসের ছবিও সুন্দর কাজ করবে।")

# অস্থায়ী ফাইল পাথসমূহ
audio_input = "temp_input_audio.mp3"
image_input = "temp_input_image.jpg"
video_output = "final_reels_video.mp4"

# সেশন স্টেট ইনিশিয়েলাইজেশন
if "step" not in st.session_state:
    st.session_state.step = 1

st.markdown(f"### 🎯 বর্তমান অবস্থান: **ধাপ {st.session_state.step}**")
st.markdown("---")

# এফএফএমপ্যাগ প্রসেসিং লাইভ ট্র্যাক করার ফাংশন
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
            status_text_display.markdown(f"⏳ প্রসেসিং হচ্ছে: **{percent}%** সম্পন্ন")
            
    process.wait()
    progress_bar.progress(1.0)
    progress_bar.empty()

# ==========================================
# 🟢  ধাপ ১: অডিও ও রিলস ছবি আপলোড
# ==========================================
if st.session_state.step == 1:
    st.header("Step ১: অডিও এবং রিলস ব্যাকগ্রাউন্ড ছবি আপলোড")
    
    uploaded_audio = st.file_uploader("🎵 আপনার মূল অডিও গানটি আপলোড করুন (MP3/WAV)", type=["mp3", "wav"])
    uploaded_image = st.file_uploader("📷 রিলসের জন্য লম্বা ব্যাকগ্রাউন্ড ছবিটি আপলোড করুন (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    voice_style = st.selectbox("🎛️ কপিরাইট প্রটেকশন ফিল্টার মোড:", [
        "🎵 Creative Lo-Fi Vibe (হালকা ইকো + ২% স্পিড চেঞ্জ + সেফ ফিল্টার)",
        "🔥 High Security Audio Changer (পিচ ভারী + ৩% স্পিড পরিবর্তন)",
        "🎙️ Deep Cinematic Echo (রহস্যময় গম্ভীর ব্যাকগ্রাউন্ড সাউন্ড)"
    ])
    
    if uploaded_audio is not None and uploaded_image is not None:
        if st.button("🚀 ভিডিও তৈরি শুরু করুন"):
            status_text = st.empty()
            status_text.markdown("🎬 অডিও প্রসেসিং এবং ভিডিও রেন্ডারিং শুরু হচ্ছে...")
            try:
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                # আগের ক্যাশ ফাইল পরিষ্কার করা
                for f in [audio_input, image_input, video_output]:
                    if os.path.exists(f): os.remove(f)
                
                # ফাইলগুলো সেভ করা
                with open(audio_input, "wb") as f:
                    f.write(uploaded_audio.read())
                with open(image_input, "wb") as f:
                    f.write(uploaded_image.read())
                
                # ১. অডিওর মোট সময়কাল (Duration) বের করা
                probe_cmd = [ffmpeg_exe, '-i', audio_input]
                probe_result = subprocess.run(probe_cmd, stderr=subprocess.PIPE, text=True)
                total_seconds = 30.0  # ডিফল্ট ব্যাকআপ
                for line in probe_result.stderr.split('\n'):
                    if 'Duration:' in line:
                        time_str = line.split('Duration:')[1].split(',')[0].strip()
                        h, m, s = time_str.split(':')
                        total_seconds = float(h)*3600 + float(m)*60 + float(s)
                        break

                # ২. অডিওর কপিরাইট রিমুভাল ফিল্টার সেট করা
                if "High Security" in voice_style:
                    a_filter = "asetrate=44100*0.93,atempo=1.07,bass=g=4"
                elif "Lo-Fi" in voice_style:
                    a_filter = "atempo=1.03,aecho=0.8:0.85:25:0.2,treble=g=2"
                else:
                    a_filter = "asetrate=44100*0.90,atempo=1.11,aecho=0.8:0.90:35:0.3,bass=g=5"
                
                # ৩. আগের সেই আসল সুন্দর কমান্ড (শুধু রিলস ছবির বিজোড় পিক্সেল ফিক্সড করা হয়েছে)
                cmd = [
                    ffmpeg_exe, '-y',
                    '-loop', '1', '-i', image_input,
                    '-i', audio_input,
                    '-filter_complex', f"[1:a]{a_filter}[out_a];[0:v]scale=trunc(iw/2)*2:trunc(ih/2)*2[out_v]",
                    '-map', '[out_v]', '-map', '[out_a]',
                    '-c:v', 'libx264', '-tune', 'stillimage',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-pix_fmt', 'yuv420p',
                    '-shortest', video_output
                ]
                
                run_ffmpeg_with_progress(cmd, status_text, total_duration=total_seconds)
                
                if os.path.exists(video_output) and os.path.getsize(video_output) > 0:
                    st.session_state.step = 2
                    st.success("✅ ভিডিও সফলভাবে তৈরি হয়েছে!")
                    st.rerun()
                else:
                    st.error("❌ ভিডিও তৈরি করা সম্ভব হয়নি। দয়া করে ফাইল পরিবর্তন করে চেষ্টা করুন।")
                    
            except Exception as e:
                st.error(f"ত্রুটি ঘটেছে: {str(e)}")

# ==========================================
# 🟢  ধাপ ২: প্লেব্যাক এবং ফাইনাল ডাউনলোড
# ==========================================
elif st.session_state.step == 2:
    st.header("Step ২: আপনার ফাইনাল ভিডিও ডাউনলোড করুন")
    
    if os.path.exists(video_output):
        st.markdown("### 📺 ভিডিও প্রিভিউ:")
        with open(video_output, "rb") as f:
            st.video(f.read())
            
        with open(video_output, "rb") as file:
            st.download_button(
                label="⬇️ গ্যালারিতে সেভ করুন (Download Reels Video)",
                data=file,
                file_name="sujon_lofi_reels.mp4",
                mime="video/mp4"
            )
    else:
        st.error("আউটপুট ফাইলটি খুঁজে পাওয়া যায়নি।")
        
    st.markdown("---")
    if st.button("🔄 নতুন গান দিয়ে ভিডিও তৈরি করুন"):
        for f in [audio_input, image_input, video_output]:
            if os.path.exists(f): os.remove(f)
        st.session_state.step = 1
        st.rerun()
