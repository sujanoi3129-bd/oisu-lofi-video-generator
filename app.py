import streamlit as st
import subprocess
import os
import requests
import imageio_ffmpeg as im_ffmpeg
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Premium Lo-Fi Studio", page_icon="🎧", layout="centered")

st.title("🎬 Premium Lo-Fi Auto-Thumnail & Video Maker")
st.write("ঠিক ইউটিউব স্ক্রিনশটের মতো বিশাল বড় বোল্ড টেক্সট, কাস্টম স্টাইল এবং ডাইনামিক এআই ক্যারেক্টার জেনারেটর!")

# ট্যাব সিস্টেম
tab1, tab2, tab3 = st.tabs(["🤖 AI প্রিমিয়াম থাম্বনেইল", "🖼️ গ্যালারি থেকে ছবি", "🔊 শুধুমাত্র অডিও"])

input_image_path = "temp_image.jpg"
image_ready = False
mode = None

# স্ক্রিনশটের মতো হুবহু প্রিমিয়াম থাম্বনেইল বানানোর ম্যাজিক ফাংশন
def create_youtube_style_thumbnail(image_file, song_title):
    img = Image.open(image_file)
    # ছবিটিকে স্ট্যান্ডার্ড ইউটিউব থাম্বনেইল সাইজ (1280x720) এ ফিক্সড করা হলো
    img = img.resize((1280, 720), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # সব লেখা বড় হাতের (UPPERCASE) করা হলো স্ক্রিনশটের মতো
    song_title_clean = song_title.upper()
    
    # ফন্ট লোড করার চেষ্টা (সার্ভারে ফন্ট না থাকলে স্ট্যান্ডার্ড বোল্ড ব্যবহার হবে)
    try:
        font_main = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 85) # বিশাল বড় মেইন টাইটেল
        font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 45) # বাঁকা স্টাইলিশ ফন্ট
        font_corner = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30) # টপ কর্নার লফি মিক্স
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_corner = ImageFont.load_default()

    # ১. ডানদিকের উপরে "LO-FI MIX" লেখা বসানো (স্ক্রিনশটের মতো)
    corner_text = "LO-FI MIX"
    draw.text((width - 50, 40), corner_text, fill="white", font=font_corner, anchor="rt", stroke_width=2, stroke_fill="black")
    
    # ২. মাঝখানের চেয়ে একটু উপরে বিশাল বড় করে "গানের নাম" বসানো
    main_x, main_y = width / 2, 180
    # লেখার পেছনে মোটা কালো বর্ডার (যাতে যেকোনো ব্যাকগ্রাউন্ডে পরিষ্কার ফুটে ওঠে)
    for offset in [(-4, -4), (4, -4), (-4, 4), (4, 4), (-6, 0), (6, 0), (0, -6), (0, 6)]:
        draw.text((main_x + offset[0], main_y + offset[1]), song_title_clean, fill="black", font=font_main, anchor="mm")
    # মূল সাদা টেক্সট
    draw.text((main_x, main_y), song_title_clean, fill="white", font=font_main, anchor="mm")
    
    # ৩. মেইন টাইটেলের ঠিক নিচে ডানপাশে বাঁকা করে "Slowed + Reverb" বসানো
    sub_text = "Slowed + Reverb"
    sub_x, sub_y = width - 250, 300
    for offset in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        draw.text((sub_x + offset[0], sub_y + offset[1]), sub_text, fill="black", font=font_sub, anchor="mm")
    draw.text((sub_x, sub_y), sub_text, fill="white", font=font_sub, anchor="mm")
    
    img.save(image_file)

# ট্যাব ১: এআই ডাইনামিক ইমেজ ও প্রিমিয়াম টেক্সট
with tab1:
    song_name = st.text_input("১. গানের নাম লিখুন (থাম্বনেইলে বড় করে লেখা উঠবে):", placeholder="Fjord Moonlight")
    
    # ইউজারকে অপশন দেওয়া যাতে সে নিজের মতো করে ব্যাকগ্রাউন্ড মুড পাল্টাতে পারে
    bg_mood = st.selectbox("২. ব্যাকগ্রাউন্ডের পরিবেশ বা মুড সিলেক্ট করুন:", 
                           ["Moonlight River & Mountains (চাঁদনী রাত, পাহাড় ও নদী)", 
                            ["Neon City Night Rain (শহরের রাতের বৃষ্টি)", "Sunset Beach Lo-Fi Theme (সূর্যাস্ত ও সমুদ্র সৈকত)", 
                            "Cozy Room Rainy Window (ঘরের ভেতর বৃষ্টির আমেজ)", "Mysterious Anime Forest (রহস্যময় বনাঞ্চল)"]])
    
    if st.button("🎨 স্ক্রিনশটের মতো প্রিমিয়াম থাম্বনেইল তৈরি করুন"):
        if song_name:
            with st.spinner("এআই আপনার গানের নাম অনুযায়ী আলাদা ক্যারেক্টার ও ব্যাকগ্রাউন্ড তৈরি করছে..."):
                try:
                    if os.path.exists(input_image_path):
                        os.remove(input_image_path)
                    
                    # প্রম্পটটিকে এমনভাবে সাজানো হয়েছে যাতে প্রতিবার আলাদা আলাদা সুন্দর এআই ক্যারেক্টার এবং আপনার সিলেক্ট করা ব্যাকগ্রাউন্ড আসে
                    ai_prompt = f"Cinematic aesthetic lo-fi girl portrait with glasses, detailed beautiful face, distinct character, background of {bg_mood}, high quality, 4k wallpaper, masterfully detailed, no watermark"
                    encoded_prompt = quote(ai_prompt)
                    
                    img_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1280&height=720&nologo=true"
                    response = requests.get(img_url)
                    
                    if response.status_code == 200:
                        with open(input_image_path, "wb") as f:
                            f.write(response.content)
                        
                        # ম্যাজিক টেক্সট লেআউট ফাংশন রান করা হলো
                        create_youtube_style_thumbnail(input_image_path, song_name)
                        
                        st.image(input_image_path, caption="🎉 আপনার তৈরি হওয়া ১০০% প্রফেশনাল ইউটিউব থাম্বনেইল")
                        image_ready = True
                        mode = "AI"
                    else:
                        st.error("❌ এআই সার্ভার থেকে ছবি জেনারেট করা যায়নি।")
                except Exception as e:
                    st.error(f"এরর: {str(e)}")
        else:
            st.warning("ভাই, আগে ১ম বক্সে গানের নাম লিখুন।")

# ট্যাব ২: ম্যানুয়াল আপলোড
with tab2:
    uploaded_image = st.file_uploader("আপনার ডিভাইস থেকে কোনো থাম্বনেইল আপলোড করতে চাইলে করুন", type=["jpg", "png"], key="uploader")
    if uploaded_image:
        with open(input_image_path, "wb") as f:
            f.write(uploaded_image.read())
        st.image(input_image_path)
        image_ready = True
        mode = "Upload"

# ট্যাব ৩: অডিও কনভার্টার
with tab3:
    st.info("এখানে শুধু অডিও প্রসেস হবে, কোনো ভিডিও তৈরি হবে না।")
    mode = "AudioOnly"

st.markdown("---")
st.subheader("৩. লফি অডিও আপলোড এবং ফাইনাল রেন্ডারিং")
uploaded_audio = st.file_uploader("আপনার অよいよ ফাইলটি আপলোড করুন (MP3/WAV)", type=["mp3", "wav"])

if uploaded_audio:
    input_audio_path = "temp_audio.mp3"
    with open(input_audio_path, "wb") as f:
        f.write(uploaded_audio.read())

    if st.button("🚀 ফাইনাল লফি ভিডিও প্রসেস শুরু করুন"):
        output_video_path = "final_output.mp4"
        ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
        
        # প্রিমিয়াম ইকো বেইজ বুস্ট এবং স্লো স্পিড ফিল্টার
        af_filter = "aecho=0.8:0.88:40:0.3,bass=g=6,atempo=0.90"
        
        if mode == "AudioOnly":
            output_audio_path = "lofi_processed_audio.mp3"
            command = [ffmpeg_exe, '-y', '-i', input_audio_path, '-af', af_filter, '-c:a', 'libmp3lame', output_audio_path]
            with st.spinner("অডিও ফিল্টারিং হচ্ছে..."):
                subprocess.run(command)
            st.success("🎉 লফি অডিও রেডি!")
            with open(output_audio_path, "rb") as f:
                st.download_button("⬇️ অডিও ডাউনলোড করুন", f, "lofi_audio.mp3")
        else:
            if image_ready and os.path.exists(input_image_path):
                # থ্রিডি সিনেমাটিক স্মুথ মোশন
                cinematic_vf = "scale=1320:742,setsar=1,zoompan=z='1.05':x='iw/2-(iw/zoom)/2+10*sin(on*0.05)':y='ih/2-(ih/zoom)/2+10*cos(on*0.05)':d=1:s=1280x720,vignette=angle=0.35"
                command = [ffmpeg_exe, '-y', '-loop', '1', '-i', input_image_path, '-i', input_audio_path, '-vf', cinematic_vf, '-af', af_filter, '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23', '-c:a', 'aac', '-shortest', output_video_path]
                
                with st.spinner("ইউটিউব কোয়ালিটি ভিডিও রেন্ডার হচ্ছে... একটু অপেক্ষা করুন ভাই..."):
                    subprocess.run(command)
                
                if os.path.exists(output_video_path):
                    st.success("🎉 আলহামদুলিল্লাহ ভাই! স্ক্রিনশটের মতো হুবহু প্রিমিয়াম কোয়ালিটি ভিডিও তৈরি সম্পন্ন হয়েছে।")
                    st.video(output_video_path)
                    with open(output_video_path, "rb") as f:
                        st.download_button("⬇️ গ্যালারিতে সেভ করুন (Download Video)", f, "final_lofi_video.mp4")
            else:
                st.error("❌ দয়া করে আগে ১ম বা ২য় ট্যাব থেকে ছবি জেনারেট করে নিন ভাই।")
