import streamlit as st
import subprocess
import os
import requests
import imageio_ffmpeg as im_ffmpeg
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Lo-Fi Ultimate Studio", page_icon="🎧", layout="centered")

st.title("🎧 Lo-Fi Ultimate Studio Pro")
st.write("এখন টপিক লিখলে এআই ছবির ওপর অটোমেটিক গানের নাম লিখে পরিপূর্ণ থাম্বনেইল তৈরি হবে!")

# ট্যাব সিস্টেম
tab1, tab2, tab3 = st.tabs(["🤖 AI পরিপূর্ণ থাম্বনেইল", "🖼️ গ্যালারি থেকে ছবি", "🔊 শুধুমাত্র অডিও"])

input_image_path = "temp_image.jpg"
image_ready = False
mode = None

# ছবির ওপর সুন্দর করে লেখার ফাংশন
def add_text_to_image(image_file, main_title, sub_title="Slowed + Reverb"):
    img = Image.open(image_file)
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # ফন্ট লোড করার চেষ্টা (ফন্ট না থাকলে ডিফল্ট ফন্ট কাজ করবে)
    try:
        # লিনাক্স সার্ভারের স্ট্যান্ডার্ড ফ্রি ফন্ট
        font_main = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 65)
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    # টেক্সটের পজিশন (ছবির নিচের দিকে মাঝ বরাবর)
    # মেইন টাইটেল (গানের নাম)
    draw.text((width/2, height - 150), main_title, fill="white", font=font_main, anchor="mm", stroke_width=4, stroke_fill="black")
    # সাব টাইটেল (লফি স্পেশাল)
    draw.text((width/2, height - 80), sub_title, fill="#FF69B4", font=font_sub, anchor="mm", stroke_width=3, stroke_fill="black")
    
    img.save(image_file)

# ট্যাব ১: এআই দিয়ে টেক্সট সহ পরিপূর্ণ থাম্বনেইল
with tab1:
    song_name = st.text_input("১. গানের নাম লিখুন (থাম্বনেইলে যা লেখা থাকবে):", placeholder="Fjord Moonlight")
    topic = st.text_input("২. ছবির ব্যাকগ্রাউন্ডের মুড বা টপিক লিখুন:", placeholder="Beautiful girl with glasses, night moon background, lofi style")
    
    if st.button("🎨 সম্পূর্ণ থাম্বনেইল তৈরি করুন"):
        if song_name and topic:
            with st.spinner("এআই ছবি বানিয়ে তার ওপর গানের নাম লিখছে..."):
                try:
                    if os.path.exists(input_image_path):
                        os.remove(input_image_path)
                        
                    encoded_prompt = quote(topic)
                    img_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1280&height=720&nologo=true"
                    response = requests.get(img_url)
                    
                    if response.status_code == 200:
                        with open(input_image_path, "wb") as f:
                            f.write(response.content)
                        
                        # ছবির ওপর অটোমেটিক গানের নাম বসানো হচ্ছে
                        add_text_to_image(input_image_path, song_name, "Slowed + Reverb")
                        
                        st.image(input_image_path, caption="🎉 আপনার তৈরি হওয়া পরিপূর্ণ থাম্বনেইল")
                        image_ready = True
                        mode = "AI"
                    else:
                        st.error("❌ এআই সার্ভার থেকে ছবি পাওয়া যায়নি।")
                except Exception as e:
                    st.error(f"এরর: {str(e)}")
        else:
            st.warning("ভাই, গানের নাম এবং ছবির টপিক—দুটি বক্সই পূরণ করুন।")

# ট্যাব ২: গ্যালারি থেকে আপলোড
with tab2:
    uploaded_image = st.file_uploader("আপনার তৈরি করা থাম্বনেইল আপলোড করুন", type=["jpg", "png"], key="uploader")
    if uploaded_image:
        with open(input_image_path, "wb") as f:
            f.write(uploaded_image.read())
        st.image(input_image_path)
        image_ready = True
        mode = "Upload"

# ট্যাব ৩: শুধুমাত্র অডিও
with tab3:
    st.info("আপনি শুধু অডিও প্রсеস করতে চাচ্ছেন (কোনো ভিডিও তৈরি হবে না)।")
    mode = "AudioOnly"

st.markdown("---")
st.subheader("৩. অডিও আপলোড ও ফাইনাল ভিডিও তৈরি")
uploaded_audio = st.file_uploader("আপনার অডিও ফাইল আপলোড করুন (MP3/WAV)", type=["mp3", "wav"])

if uploaded_audio:
    input_audio_path = "temp_audio.mp3"
    with open(input_audio_path, "wb") as f:
        f.write(uploaded_audio.read())

    if st.button("🚀 ভিডিও প্রসেস শুরু করুন"):
        output_video_path = "final_output.mp4"
        ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
        
        # মিষ্টি বেইজ ও ১০% স্লো স্পিড
        af_filter = "aecho=0.8:0.88:40:0.3,bass=g=6,atempo=0.90"
        
        if mode == "AudioOnly":
            # শুধুমাত্র অডিও কনভার্ট করে নামিয়ে দেবে
            output_audio_path = "lofi_processed_audio.mp3"
            command = [ffmpeg_exe, '-y', '-i', input_audio_path, '-af', af_filter, '-c:a', 'libmp3lame', output_audio_path]
            with st.spinner("অডিও প্রসেস হচ্ছে..."):
                subprocess.run(command)
            st.success("🎉 লফি অডিও রেডি!")
            with open(output_audio_path, "rb") as f:
                st.download_button("⬇️ অডিও ডাউনলোড করুন", f, "lofi_audio.mp3")
        else:
            if image_ready and os.path.exists(input_image_path):
                # থ্রিডি মোশন ও ভিনিয়েট ইফেক্ট সহ ভিডিও
                cinematic_vf = "scale=1320:742,setsar=1,zoompan=z='1.05':x='iw/2-(iw/zoom)/2+10*sin(on*0.05)':y='ih/2-(ih/zoom)/2+10*cos(on*0.05)':d=1:s=1280x720,vignette=angle=0.35"
                command = [ffmpeg_exe, '-y', '-loop', '1', '-i', input_image_path, '-i', input_audio_path, '-vf', cinematic_vf, '-af', af_filter, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-c:a', 'aac', '-shortest', output_video_path]
                
                with st.spinner("পানির মতো মোশন ইফেক্ট সহ ভিডিও তৈরি হচ্ছে..."):
                    subprocess.run(command)
                
                if os.path.exists(output_video_path):
                    st.success("🎉 আলহামদুলিল্লাহ! আপনার টেক্সট সহ ফুল প্রফেশনাল লফি ভিডিও তৈরি হয়ে গেছে।")
                    st.video(output_video_path)
                    with open(output_video_path, "rb") as f:
                        st.download_button("⬇️ গ্যালারিতে সেভ করুন (Download Video)", f, "final_lofi_video.mp4")
            else:
                st.error("❌ দয়া করে আগে ১ম বা ২য় ট্যাব থেকে ছবি রেডি করুন ভাই।")
