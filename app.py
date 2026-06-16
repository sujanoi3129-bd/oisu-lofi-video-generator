import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Lo-Fi Video Generator", page_icon="🎵", layout="centered")

st.title("🎵 One-Click Lo-Fi Video Generator")
st.write("মিউজিক ও বেইজ ঠিক রেখে গানের তালে তালে ঝাঁকুনি সহ পারফেক্ট লো-ফাই ভিডিও!")

# ফাইল আপলোডার
uploaded_audio = st.file_uploader("১. আপনার অডিও ফাইল আপলোড করুন (MP3/WAV)", type=["mp3", "wav"])
uploaded_image = st.file_uploader("২. আপনার ব্যাকগ্রাউন্ড ছবি আপলোড করুন (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_audio is not None and uploaded_image is not None:
    input_audio_path = "temp_audio.mp3"
    input_image_path = "temp_image.jpg"
    output_video_path = "lofi_masterpiece.mp4"
    
    with open(input_audio_path, "wb") as f:
        f.write(uploaded_audio.read())
    with open(input_image_path, "wb") as f:
        f.write(uploaded_image.read())
        
    st.success("✅ অডিও এবং ছবি সফলভাবে আপলোড হয়েছে!")
    st.markdown("---")
    
    if st.button("🚀 Generate Viral Lo-Fi Video"):
        with st.spinner("মিউজিক ও বেইজ ঠিক রেখে বিটের তালে তালে ভিডিও তৈরি হচ্ছে..."):
            try:
                if os.path.exists(output_video_path):
                    os.remove(output_video_path)
                    
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                # ১. উন্নত অডিও ফিল্টার: বেইজ ধরে রেখে মিষ্টি লো-ফাই সাউন্ড তৈরি
                # atempo=0.90 দিয়ে গানটি ১০% স্লো করা হয়েছে, আর bass=g=5 দিয়ে বেইজ বুস্ট করা হয়েছে
                af_filter = "aecho=0.8:0.88:40:0.3,bass=g=5,atempo=0.90"
                
                # ২. উন্নত ভিডিও ফিল্টার: গানের বিটের তালে তালে হালকা কাঁপানো বা ঝাঁকুনি (Beat Shake Effect)
                # sin(2*PI*2*on/25) এবং cos ফিল্টার ব্যবহার করে ছবিটিকে প্রতি সেকেন্ডে ২ বার হালকা বামে-ডানে এবং সামনে-পেছনে ঝাঁকুনি দেওয়া হচ্ছে
                vf_filter = (
                    "scale=1280:720,setsar=1,"
                    "zoompan=z='1.04+0.02*sin(2*PI*2*on/25)':x='iw/2-(iw/zoom)/2+5*cos(2*PI*2*on/25)':y='ih/2-(ih/zoom)/2+5*sin(2*PI*2*on/25)':d=1:s=1280x720,"
                    "eq=brightness=0.03:contrast=1.03:saturation=1.02"
                )
                
                command = [
                    ffmpeg_exe, '-y',
                    '-loop', '1', '-i', input_image_path,
                    '-i', input_audio_path,
                    '-vf', vf_filter,
                    '-af', af_filter,
                    '-c:v', 'libx264',
                    '-preset', 'veryfast',
                    '-crf', '24',
                    '-c:a', 'aac',
                    '-shortest',
                    output_video_path
                ]
                
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                    st.success("🎉 আলহামদুলিল্লাহ ভাই! আপনার বিট-শেকিং লো-ফাই ভিডিওটি তৈরি হয়ে গেছে।")
                    
                    with open(output_video_path, "rb") as video_file:
                        st.video(video_file.read())
                        
                    with open(output_video_path, "rb") as file:
                        st.download_button(
                            label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                            data=file,
                            file_name="lofi_beat_shake_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("❌ ভিডিও তৈরি করা যায়নি। নিচে এরর দেওয়া হলো:")
                    st.code(result.stderr)
                    
                if os.path.exists(input_audio_path): os.remove(input_audio_path)
                if os.path.exists(input_image_path): os.remove(input_image_path)
                
            except Exception as e:
                st.error(f"দুঃখিত ভাই, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")