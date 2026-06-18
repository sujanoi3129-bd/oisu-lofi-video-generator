import streamlit as st
import subprocess
import os
import re
import imageio_ffmpeg as im_ffmpeg

st.set_page_config(page_title="Lo-Fi Video Maker", page_icon="🎵", layout="centered")

st.title("🎵 Lo-Fi Audio Copyright Remover & Live Video Creator")
st.write("সুজন ভাই, এবার ছবি স্মুথলি নড়াচড়া করবে এবং চমৎকার কালার ইফেক্টে ভিডিও জীবন্ত হয়ে উঠবে!")

# অস্থায়ী ফাইল পাথসমূহ
audio_input = "temp_input_audio.mp3"
image_input = "temp_input_image.jpg"
video_output = "final_live_reel.mp4"

if "step" not in st.session_state:
    st.session_state.step = 1

st.markdown(f"### 🎯 বর্তমান অবস্থান: **ধাপ {st.session_state.step}**")
st.markdown("---")

# প্রসেসিং বার ট্র্যাক করার ফাংশন
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
            status_text_display.markdown(f"⏳ আপনার রিলস ভিডিওটি তৈরি হচ্ছে: **{percent}%** সম্পন্ন")
            
    process.wait()
    progress_bar.progress(1.0)
    progress_bar.empty()

# ==========================================
# 🟢  ধাপ ১: ফাইল আপলোড ও ইফেক্ট সিলেকশন
# ==========================================
if st.session_state.step == 1:
    st.header("Step ১: অডিও এবং রিলস ছবি আপโหลด করুন")
    
    uploaded_audio = st.file_uploader("🎵 আপনার অডিও গানটি দিন (MP3/WAV)", type=["mp3", "wav"])
    uploaded_image = st.file_uploader("📷 রিলসের ব্যাকগ্রাউন্ড ছবি দিন (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    voice_style = st.selectbox("🎛️ কপিরাইট প্রটেকশন মোড:", [
        "🎵 Creative Lo-Fi Vibe (হালকা ইকো + ২% স্পিড চেঞ্জ)",
        "🔥 High Security Mode (পিচ ভারী + ৩% স্পিড পরিবর্তন)"
    ])
    
    video_effect = st.selectbox("✨ ভিডিও লাইভ ওভারলে ইফেক্ট সিলেক্ট করুন:", [
        "🌟 Cinematic Dream (উষ্ণ কালার টোন + ভাইব্রেন্ট লাইটিং)",
        "🪐 Neon Cyber (হালকা গ্লো এবং শার্প কন্ট্রাস্ট ইফেক্ট)",
        "🎬 Vintage Classic (পুরোনো মিউজিক ভিডিওর মতো মৃদু সফট লুক)"
    ])
    
    if uploaded_audio is not None and uploaded_image is not None:
        if st.button("🚀 চমৎকার রিলস ভিডিও তৈরি করুন"):
            status_text = st.empty()
            status_text.markdown("🎬 অডিও ফিল্টারিং এবং ভিডিও রেন্ডারিং শুরু হচ্ছে...")
            try:
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                # আগের ক্যাশ পরিষ্কার করা
                for f in [audio_input, image_input, video_output]:
                    if os.path.exists(f): os.remove(f)
                
                with open(audio_input, "wb") as f:
                    f.write(uploaded_audio.read())
                with open(image_input, "wb") as f:
                    f.write(uploaded_image.read())
                
                # ১. অডিওর মোট সময়কাল (Duration) বের করা
                probe_cmd = [ffmpeg_exe, '-i', audio_input]
                probe_result = subprocess.run(probe_cmd, stderr=subprocess.PIPE, text=True)
                total_seconds = 30.0
                for line in probe_result.stderr.split('\n'):
                    if 'Duration:' in line:
                        time_str = line.split('Duration:')[1].split(',')[0].strip()
                        h, m, s = time_str.split(':')
                        total_seconds = float(h)*3600 + float(m)*60 + float(s)
                        break

                # ২. কপিরাইট অডিও ফিল্টার
                if "High Security" in voice_style:
                    a_filter = "asetrate=44100*0.93,atempo=1.07,bass=g=4"
                else:
                    a_filter = "atempo=1.03,aecho=0.8:0.85:25:0.2,treble=g=2"
                
                # ৩. ব্যবহারকারীর পছন্দ অনুযায়ী ওভারলে কালার ইফেক্ট সেট করা
                if "Cinematic" in video_effect:
                    color_filter = "eq=brightness=0.02:contrast=1.15:saturation=1.3"
                elif "Neon" in video_effect:
                    color_filter = "eq=contrast=1.25:saturation=1.4:gamma=0.95"
                else:
                    color_filter = "eq=brightness=-0.02:contrast=1.05:saturation=0.9"

                # 🎯 ৪. আসল ট্রিক: ছবিকে ২৫ এফপিএস-এ স্মুথ মোশনে নড়াচড়া করানো এবং কালার ওভারলে দেওয়া
                # '1+0.05*sin(2*pi*t*0.1)' এর মাধ্যমে ছবি চমৎকারভাবে ধীরে ধীরে জুম-ইন ও আউট হয়ে জীবন্ত লাগবে
                cmd = [
                    ffmpeg_exe, '-y',
                    '-loop', '1', '-r', '25', '-i', image_input,
                    '-i', audio_input,
                    '-filter_complex', 
                    f"[1:a]{a_filter}[processed_audio];"
                    f"[0:v]scale=1280:2240,zoompan=z='1+0.05*sin(2*pi*time*0.1)':x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2':s=720x1280:fps=25,{color_filter},setpts=PTS-STARTPTS[out_v]",
                    '-map', '[out_v]', '-map', '[processed_audio]',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-pix_fmt', 'yuv420p',
                    '-shortest', video_output
                ]
                
                run_ffmpeg_with_progress(cmd, status_text, total_duration=total_seconds)
                
                if os.path.exists(video_output) and os.path.getsize(video_output) > 0:
                    st.session_state.step = 2
                    st.success("✅ আপনার জীবন্ত রিলস ভিডিও রেডি!")
                    st.rerun()
                else:
                    st.error("❌ ভিডিও তৈরি করা সম্ভব হয়নি।")
                    
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
                label="⬇️ গ্যালারিতে সেভ করুন (Download Music Reel)",
                data=file,
                file_name="sujon_live_reel.mp4",
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
