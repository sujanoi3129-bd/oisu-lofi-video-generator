import streamlit as st
import subprocess
import os
import requests
import imageio_ffmpeg as im_ffmpeg
from urllib.parse import quote

st.set_page_config(page_title="Lo-Fi Ultimate Studio", page_icon="🎧", layout="centered")

st.title("🎧 Lo-Fi Ultimate Studio")
st.write("আপনার গানের জন্য ছবি তৈরি করুন, আপলোড করুন অথবা সরাসরি অডিও প্রসেস করুন!")

# ট্যাব সিস্টেম
tab1, tab2, tab3 = st.tabs(["🤖 AI ছবি তৈরি", "🖼️ গ্যালারি থেকে ছবি", "🔊 শুধুমাত্র অডিও"])

input_image_path = "temp_image.jpg"
image_ready = False
mode = None

# ট্যাব ১: এআই ইমেজ
with tab1:
    topic = st.text_input("ছবির টপিক লিখুন (যেমন: Fjord moonlight, aesthetic night)")
    if st.button("🎨 এআই দিয়ে ছবি তৈরি করুন"):
        with st.spinner("ছবি তৈরি হচ্ছে..."):
            encoded_prompt = quote(topic)
            img_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1280&height=720&nologo=true"
            response = requests.get(img_url)
            with open(input_image_path, "wb") as f:
                f.write(response.content)
            st.image(input_image_path)
            image_ready = True
            mode = "AI"

# ট্যাব ২: আপলোড
with tab2:
    uploaded_image = st.file_uploader("ছবি আপলোড করুন", type=["jpg", "png"], key="uploader")
    if uploaded_image:
        with open(input_image_path, "wb") as f:
            f.write(uploaded_image.read())
        st.image(input_image_path)
        image_ready = True
        mode = "Upload"

# ট্যাব ৩: অডিও
with tab3:
    st.info("আপনি শুধু অডিও প্রসেস করতে চাচ্ছেন।")
    mode = "AudioOnly"

st.markdown("---")
uploaded_audio = st.file_uploader("আপনার অডিও ফাইল আপলোড করুন", type=["mp3", "wav"])

if uploaded_audio:
    input_audio_path = "temp_audio.mp3"
    with open(input_audio_path, "wb") as f:
        f.write(uploaded_audio.read())

    if st.button("🚀 ভিডিও প্রসেস শুরু করুন"):
        output_video_path = "final_output.mp4"
        ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
        af_filter = "aecho=0.8:0.88:40:0.3,bass=g=6,atempo=0.90"
        
        # কমান্ড তৈরি
        if mode == "AudioOnly":
            command = [ffmpeg_exe, '-y', '-i', input_audio_path, '-c:a', 'aac', 'output_audio.mp3']
        else:
            cinematic_vf = "scale=1280:720,zoompan=z='1.05':x='iw/2-(iw/zoom)/2+10*sin(on*0.05)':y='ih/2-(ih/zoom)/2+10*cos(on*0.05)':d=1:s=1280x720,vignette=angle=0.35"
            command = [ffmpeg_exe, '-y', '-loop', '1', '-i', input_image_path, '-i', input_audio_path, '-vf', cinematic_vf, '-af', af_filter, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-c:a', 'aac', '-shortest', output_video_path]
        
        subprocess.run(command)
        
        if mode == "AudioOnly":
            st.success("অডিও প্রসেস হয়েছে!")
        else:
            st.video(output_video_path)
            with open(output_video_path, "rb") as f:
                st.download_button("⬇️ ডাউনলোড করুন", f, "final_video.mp4")
