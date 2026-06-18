import streamlit as st
import subprocess
import os
import re
import imageio_ffmpeg as im_ffmpeg

st.set_page_config(page_title="Lo-Fi Studio Pro", page_icon="🎧", layout="centered")

st.title("🎧 Lo-Fi Studio Pro")
st.write("সুজন ভাই, এবার ট্যাব ঝামেলার অবসান! ভিডিও এবং রিলস ১০০% নিখুঁতভাবে তৈরি হবে।")

input_image_path = "temp_image.jpg"
input_audio_path = "temp_audio.mp3"
output_video_path = "final_lofi_master.mp4"
output_audio_path = "processed_lofi_audio.mp3"

# ==========================================
# 🟢 ধাপ ১: মেকিং মোড সিলেক্ট করুন (সহজ ও ফিক্সড ডিজাইন)
# ==========================================
st.subheader("১. আপনি কী তৈরি করতে চান?")
making_mode = "ভিডিও বা রিলস তৈরি করব"  # ডিফল্ট ব্যাকআপ

making_mode = st.radio(
    "আপনার পছন্দটি বেছে নিন:",
    ["🎬 ভিডিও বা রিলস তৈরি করব (ছবি ও গান সহ)", "🔊 শুধুমাত্র অডিও প্রসেস করব (কোনো ভিডিও হবে না)"],
    index=0
)

# ==========================================
# 🟢 ধাপ ২: ছবি ও সাইজ সিলেকশন (যদি ভিডিও মোড হয়)
# ==========================================
image_ready = False
output_size_option = "📱 রিলস / শর্টস সাইজ (Reels 9:16 - 720x1280)"

if "ভিডিও বা রিলস" in making_mode:
    st.markdown("---")
    st.subheader("২. আপনার ব্যাকগ্রাউন্ড ছবিটি আপলোড করুন")
    uploaded_image = st.file_uploader("যেকোনো সাইজের ছবি আপলোড করুন (JPG/PNG)", type=["jpg", "jpeg", "png"])
    
    output_size_option = st.selectbox("📐 আউটপুট ভিডিওর সাইজ সিলেক্ট করুন:", [
        "📱 রিলস / শর্টস সাইজ (Reels 9:16 - 720x1280)",
        "🎬 ফুল এইচডি ভিডিও সাইজ (Video 16:9 - 1280x720)"
    ])
    
    if uploaded_image is not None:
        with open(input_image_path, "wb") as f:
            f.write(uploaded_image.read())
        st.image(input_image_path, caption="✅ ছবি সফলভাবে আপলোড হয়েছে", width=250)
        image_ready = True

# ==========================================
# 🟢 ধাপ ৩: অডিও ফাইল আপলোড
# ==========================================
st.markdown("---")
st.subheader("৩. আপনার মূল অডিও গানটি আপলোড করুন")
uploaded_audio = st.file_uploader("গান আপলোড করুন (MP3/WAV)", type=["mp3", "wav"])

# এফএফএমপ্যাগ প্রসেসিং লাইভ ট্র্যাক করার ফাংশন (পারসেন্টেজ দেখানোর জন্য)
def run_ffmpeg_with_progress(cmd, status_text_display, total_duration=10.0, msg="প্রসেস হচ্ছে"):
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
            status_text_display.markdown(f"⏳ {msg}: **{percent}%** সম্পন্ন")
            
    process.wait()
    progress_bar.progress(1.0)
    progress_bar.empty()

# ==========================================
# 🟢 ধাপ ৪: কনভার্সন এবং ডাউনলোড
# ==========================================
if uploaded_audio is not None:
    if st.button("🚀 লফি কনভার্সন শুরু করুন (Run Conversion)"):
        ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
        
        # আগের পুরনো ফাইল পরিষ্কার করা
        for f in [input_audio_path, output_video_path, output_audio_path]:
            if os.path.exists(f): os.remove(f)
            
        with open(input_audio_path, "wb") as f:
            f.write(uploaded_audio.read())
            
        # অডিওর মোট সময়কাল বের করা
        probe_cmd = [ffmpeg_exe, '-i', input_audio_path]
        probe_result = subprocess.run(probe_cmd, stderr=subprocess.PIPE, text=True)
        total_seconds = 30.0
        for line in probe_result.stderr.split('\n'):
            if 'Duration:' in line:
                time_str = line.split('Duration:')[1].split(',')[0].strip()
                h, m, s = time_str.split(':')
                total_seconds = float(h)*3600 + float(m)*60 + float(s)
                break
                
        # প্রিমিয়াম লফি ফিল্টার (Slowed + Reverb + Bass)
        af_filter = "aecho=0.8:0.88:40:0.3,bass=g=6,atempo=0.90"
        
        # 💥 অপশন ১: শুধুমাত্র অডিও প্রসেস করা
        if "শুধুমাত্র অডিও" in making_mode:
            status_text = st.empty()
            status_text.markdown("🎧 আপনার গানটিকে লফি সাউন্ডে রূপান্তর করা হচ্ছে...")
            try:
                command = [
                    ffmpeg_exe, '-y',
                    '-i', input_audio_path,
                    '-af', af_filter,
                    '-c:a', 'libmp3lame', '-b:a', '192k',
                    output_audio_path
                ]
                run_ffmpeg_with_progress(command, status_text, total_duration=total_seconds, msg="লফি অডিও তৈরি হচ্ছে")
                
                if os.path.exists(output_audio_path) and os.path.getsize(output_audio_path) > 0:
                    st.success("🎉 আলহামদুলিল্লাহ ভাই! লফি অডিও ট্র্যাকটি সফলভাবে তৈরি হয়েছে।")
                    st.audio(output_audio_path)
                    with open(output_audio_path, "rb") as file:
                        st.download_button(
                            label="⬇️ লফি অডিও ডাউনলোড করুন (Download MP3)",
                            data=file,
                            file_name="lofi_slowed_reverb.mp3",
                            mime="audio/mp3"
                        )
                else:
                    st.error("❌ অডিও প্রসেস করা যায়নি।")
            except Exception as e:
                st.error(f"ভুল ত্রুটি: {str(e)}")
                
        # 💥 অপশন ২: ছবি সহ ভিডিও বা রিলস তৈরি করা
        elif "ভিডিও বা রিলস" in making_mode:
            if image_ready and os.path.exists(input_image_path):
                status_text = st.empty()
                status_text.markdown("🎬 আপনার দেওয়া ছবি ও চমৎকার লাইভ মোশন সহ ভিডিও তৈরি হচ্ছে...")
                try:
                    if "রিলস" in output_size_option:
                        # রিলস সাইজ ফিল্টার (৭২০x১২৮০)
                        cinematic_vf = (
                            "scale=1280:2240:force_original_aspect_ratio=increase,crop=1280:2240,"
                            "zoompan=z='1+0.05*sin(in/40)':x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2':s=720x1280:fps=25,"
                            "eq=brightness=0.02:contrast=1.15:saturation=1.3"
                        )
                        final_name = "lofi_final_reel.mp4"
                    else:
                        # ফুল এইচডি ভিডিও সাইজ ফিল্টার (১২৮০x৭২০)
                        cinematic_vf = (
                            "scale=2240:1280:force_original_aspect_ratio=increase,crop=2240:1280,"
                            "zoompan=z='1+0.05*sin(in/40)':x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2':s=1280x720:fps=25,"
                            "eq=brightness=0.02:contrast=1.15:saturation=1.3"
                        )
                        final_name = "lofi_final_video.mp4"
                        
                    command = [
                        ffmpeg_exe, '-y',
                        '-loop', '1', '-r', '25', '-i', input_image_path,
                        '-i', input_audio_path,
                        '-vf', cinematic_vf,
                        '-af', af_filter,
                        '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                        '-c:a', 'aac', '-shortest',
                        output_video_path
                    ]
                    run_ffmpeg_with_progress(command, status_text, total_duration=total_seconds, msg="আপনার লফি ভিডিওটি তৈরি হচ্ছে")
                    
                    if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                        st.success("🎉 আলহামদুলিল্লাহ ভাই! আপনার প্রিমিয়াম লফি ভিডিও সফলভাবে তৈরি হয়েছে।")
                        st.video(output_video_path)
                        with open(output_video_path, "rb") as file:
                            st.download_button(
                                label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                                data=file,
                                file_name=final_name,
                                mime="video/mp4"
                            )
                    else:
                        st.error("❌ ভিডিও তৈরি করা সম্ভব হয়নি।")
                except Exception as e:
                    st.error(f"ভুল ত্রুটি: {str(e)}")
            else:
                st.error("❌ ভাই, দয়া করে আগে উপর থেকে আপনার ব্যাকগ্রাউন্ড ছবিটি আপলোড করে নিন।")
                
    # কাজ শেষে টেম্পোরারি অডিও ফাইল ডিলিট
    if os.path.exists(input_audio_path): os.remove(input_audio_path)
