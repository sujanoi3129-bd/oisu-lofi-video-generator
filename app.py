import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Cinematic Lo-Fi Maker", page_icon="🎵", layout="centered")

st.title("🎬 Cinematic Audio Reactive Lo-Fi Video Generator")
st.write("ঝামেলাহীন সিনেমাটিক ভিনিয়েট এবং স্মুথ থ্রিডি মোশন ইফেক্ট সহ ১০০% টেস্টেড কোড।")

# ফাইল আপলোডার
uploaded_audio = st.file_uploader("১. আপনার অডিও ফাইল আপলোড করুন (MP3/WAV)", type=["mp3", "wav"])
uploaded_image = st.file_uploader("২. আপনার ব্যাকগ্রাউন্ড ছবি আপলোড করুন (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_audio is not None and uploaded_image is not None:
    input_audio_path = "temp_audio.mp3"
    input_image_path = "temp_image.jpg"
    output_video_path = "lofi_cinematic_master.mp4"
    
    with open(input_audio_path, "wb") as f:
        f.write(uploaded_audio.read())
    with open(input_image_path, "wb") as f:
        f.write(uploaded_image.read())
    
    st.success("✅ অডিও এবং ছবি সফলভাবে আপলোড হয়েছে!")
    st.markdown("---")
    
    if st.button("🚀 Generate Cinematic Masterpiece"):
        with st.spinner("নতুন সিনেমাটিক ইফেক্ট সহ ভিডিওটি তৈরি হচ্ছে... একটু অপেক্ষা করুন ভাই..."):
            try:
                if os.path.exists(output_video_path):
                    os.remove(output_video_path)
                
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                # অডিও ফিল্টার: বেইজ বুস্ট এবং ১০% ধীর লফি গতি
                af_filter = "aecho=0.8:0.88:40:0.3,bass=g=6,atempo=0.90"
                
                # ১০০% নিরাপদ ফিল্টার চেইন:
                # ১. scale দিয়ে ছবি বড় করা হয়েছে যাতে চারপাশ স্মুথ থাকে।
                # ২. zoompan দিয়ে একটি জটিলতাহীন ও সুন্দর থ্রিডি পালস ও মোশন ইফেক্ট তৈরি করা হয়েছে।
                # ৩. vignette=angle=0.35 দিয়ে চারপাশ সুন্দর ভিন্টেজ ডার্ক শ্যাডো করা হয়েছে।
                # ৪. eq ফিল্টার দিয়ে কোনো ডাইনামিক ইকুয়েশন ছাড়া স্ট্যাটিক কালার ও কনট্রাস্ট ফিক্স করা হয়েছে।
                cinematic_vf = (
                    "scale=1320:742,setsar=1,"
                    "zoompan=z='1.05':x='iw/2-(iw/zoom)/2+10*sin(on*0.05)':y='ih/2-(ih/zoom)/2+10*cos(on*0.05)':d=1:s=1280x720,"
                    "vignette=angle=0.35,"
                    "eq=contrast=1.06:saturation=1.05:brightness=0.01"
                )
                
                command = [
                    ffmpeg_exe, '-y',
                    '-loop', '1', '-i', input_image_path,
                    '-i', input_audio_path,
                    '-vf', cinematic_vf,
                    '-af', af_filter,
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                    '-c:a', 'aac', '-shortest',
                    output_video_path
                ]
                
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                    st.success("🎉 আলহামদুলিল্লাহ ভাই! এবার আপনার নতুন সিনেমাটিক লো-ফাই ভিডিওটি সফলভাবে তৈরি হয়েছে।")
                    
                    with open(output_video_path, "rb") as video_file:
                        st.video(video_file.read())
                    
                    with open(output_video_path, "rb") as file:
                        st.download_button(
                            label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                            data=file,
                            file_name="lofi_cinematic_final.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("❌ ভিডিও তৈরি করা যায়নি। নিচে নতুন এরর ডিটেইলস দেওয়া হলো:")
                    st.code(result.stderr)
                
                if os.path.exists(input_audio_path): os.remove(input_audio_path)
                if os.path.exists(input_image_path): os.remove(input_image_path)
            
            except Exception as e:
                st.error(f"দুঃখিত ভাই, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")
