import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Lo-Fi Video Generator", page_icon="🎵", layout="centered")

st.title("🎵 One-Click Lo-Fi Video Generator")
st.write("আপনার অডিও এবং ছবি আপলোড করুন। এক ক্লিকেই তৈরি হবে ভাইরাল সিনেমাটিক লো-ফাই ভিডিও!")

# ফাইল আপলোডার
uploaded_audio = st.file_uploader("১. আপনার অডিও ফাইল আপলোড করুন (MP3/WAV)", type=["mp3", "wav"])
uploaded_image = st.file_uploader("২. আপনার ব্যাকগ্রাউন্ড ছবি আপলোড করুন (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_audio is not None and uploaded_image is not None:
    input_audio_path = "temp_audio.mp3"
    input_image_path = "temp_image.jpg"
    output_video_path = "lofi_masterpiece.mp4"
    
    # ফাইলগুলো সার্ভারে সেভ করা
    with open(input_audio_path, "wb") as f:
        f.write(uploaded_audio.read())
    with open(input_image_path, "wb") as f:
        f.write(uploaded_image.read())
        
    st.success("✅ অডিও এবং ছবি সফলভাবে আপলোড হয়েছে!")
    st.markdown("---")
    
    # প্রিভিউ দেখানো
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("🎵 অডিও প্রিভিউ:")
        st.audio(input_audio_path)
    with col2:
        st.markdown("🖼️ ছবির প্রিভিউ:")
        st.image(input_image_path, width=200)
        
    st.markdown("---")
    
    if st.button("🚀 Generate Viral Lo-Fi Video"):
        with st.spinner("অডিও লো-ফাই করা এবং ছবিটিকে জীবন্ত করার কাজ চলছে... একটু অপেক্ষা করুন ভাই..."):
            try:
                if os.path.exists(output_video_path):
                    os.remove(output_video_path)
                    
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                # ১. অডিও ফিল্টার: গতি ১২% স্লো করা এবং রিভার্ব/ইকো ইফেক্ট দিয়ে কপিরাইট ফ্রি করা
                # asetrate=44100*0.88 (সাউন্ড স্লো এবং গম্ভীর করবে), highpass ও lowpass আবহ তৈরি করবে
                af_filter = "asetrate=44100*0.88,highpass=f=200,lowpass=f=3500,aecho=0.8:0.88:60:0.4"
                
                # ২. ভিডিও ফিল্টার: ছবিকে হালকা পালস (Zoom in/out) করানো এবং লাইটিং টোন পরিবর্তন করা
                # zoompan ফিল্টার দিয়ে প্রতি ফ্রেমে হালকা সাইজ পরিবর্তন করা হয় যাতে ছবি নড়াচড়া করে
                vf_filter = (
                    "scale=1280:720,setsar=1,"
                    "zoompan=z='1.03+0.03*sin(2*PI*0.5*on/25)':x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2':d=1:s=1280x720,"
                    "eq=brightness=0.02:contrast=1.05:saturation=0.95"
                )
                
                # FFmpeg কম্যান্ড জেনারেটর
                command = [
                    ffmpeg_exe, '-y',
                    '-loop', '1', '-i', input_image_path,  # ছবি ইনপুট
                    '-i', input_audio_path,                # অডিও ইনপুট
                    '-vf', vf_filter,
                    '-af', af_filter,
                    '-c:v', 'libx264',
                    '-preset', 'veryfast',
                    '-crf', '24',
                    '-c:a', 'aac',
                    '-shortest',                           # অডিও শেষ হলেই ভিডিও শেষ হবে
                    output_video_path
                ]
                
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                    st.success("🎉 আলহামদুলিল্লাহ ভাই! আপনার চমৎকার লো-ফাই ভিডিওটি তৈরি হয়ে গেছে।")
                    
                    # ফাইনাল ভিডিও প্রিভিউ
                    with open(output_video_path, "rb") as video_file:
                        st.video(video_file.read())
                        
                    # ডাউনলোড বাটন
                    with open(output_video_path, "rb") as file:
                        st.download_button(
                            label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                            data=file,
                            file_name="lofi_viral_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("❌ ভিডিও তৈরি করা যায়নি। নিচে এরর দেওয়া হলো:")
                    st.code(result.stderr)
                    
                # সাময়িক ফাইল মুছে ফেলা
                if os.path.exists(input_audio_path): os.remove(input_audio_path)
                if os.path.exists(input_image_path): os.remove(input_image_path)
                
            except Exception as e:
                st.error(f"দুঃখিত ভাই, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")