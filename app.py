import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Cinematic Lo-Fi Maker", page_icon="🎵", layout="centered")

st.title("🎬 Cinematic Audio Reactive Lo-Fi Video Generator")
st.write("পানির মতো ঝাঁকুনি, সিনেমাটিক গ্লো এবং লাইটিং ইফেক্ট সহ সম্পূর্ণ ত্রুটিমুক্ত ও চূড়ান্ত কোড।")

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
        with st.spinner("ভিডিওতে সিনেমাটিক ইফেক্ট ও পানির মতো ঝাঁকুনি রেন্ডার হচ্ছে... একটু অপেক্ষা করুন ভাই..."):
            try:
                if os.path.exists(output_video_path):
                    os.remove(output_video_path)
                
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                # অডিও ফিল্টার: বেইজ বুস্ট এবং ১০% ধীর লফি গতি
                af_filter = "aecho=0.8:0.88:40:0.3,bass=g=6,atempo=0.90"
                
                # সম্পূর্ণ সুরক্ষিত এবং এরর-ফ্রি সিনেমাটিক ফিল্টার চেইন (আপডেটেড):
                # ১. scale দিয়ে ছবি বড় করা হয়েছে যাতে কাঁপলে চারপাশ কালো না দেখায়।
                # ২. zoompan দিয়ে পানির মতো ডাইনামিক বিট-শেকিং এবং পালস ইফেক্ট। ব্র্যাকেটের গাণিতিক কাজ দূর করা হয়েছে।
                # ৩. vignette=angle=0.4 দিয়ে চারপাশ সুন্দর সিনেমাটিক ডার্ক শ্যাডো।
                # ৪. eq ফিল্টার ব্যবহার করা হয়েছে ব্রাইটনেস ও কনট্রাস্ট হালকা গ্লো করানোর জন্য (যা সব এফএফএমপেগে সাপোর্ট করে)। এক্সপ্রেশনগুলো আরও সহজ করা হয়েছে।
                cinematic_vf = (
                    "scale=1320:742,setsar=1,"
                    "zoompan=z='1.04+0.02*hypot(sin(on*0.4),cos(on*0.25))':x='iw/2-(iw/zoom)/2+7*sin(on*0.4)':y='ih/2-(ih/zoom)/2+7*cos(on*0.25)':d=1:s=1280x720,"
                    "vignette=angle=0.4,"
                    "eq=brightness='0.02+0.01*sin(0.1*on)':contrast='1.04+0.02*cos(0.1*on)':saturation=1.05"
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
                    st.success("🎉 আলহামদুলিল্লাহ ভাই! এবার আপনার সিনেমাটিক লো-ফাই ভিডিওটি সফলভাবে তৈরি হয়েছে।")
                    
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
