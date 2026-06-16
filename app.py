import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০۰۰ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Cinematic Lo-Fi Maker", page_icon="🎵", layout="centered")

st.title("🎬 Cinematic Audio Reactive Lo-Fi Video Generator")
st.write("পানির মতো ঝাঁকুনি, ভাসমান আলোর কণা (Particle) এবং সিনেমাটিক লাইটিং গ্লো ইফেক্ট সহ প্রিমিয়াম ভিডিও!")

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
        with st.spinner("ভিডিওতে লাইটিং গ্লো এবং ভাসমান পার্টিকেল ইফেক্ট রেন্ডার হচ্ছে... একটু সময় লাগবে ভাই..."):
            try:
                if os.path.exists(output_video_path):
                    os.remove(output_video_path)
                    
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                # অডিও ফিল্টার: বেইজ বুস্ট এবং ১০% ধীর লফি গতি
                af_filter = "aecho=0.8:0.88:40:0.3,bass=g=6,atempo=0.90"
                
                # অ্যাডভান্সড সিনেমাটিক ভিডিও ফিল্টার চেইন:
                # ১. ছবির সাইজ বড় করা (scale) যাতে ঝাঁকুনিতে চারপাশ কেটে না যায়।
                # ২. পানির মতো ঝাঁকুনি ও পালস ইফেক্ট (zoompan)।
                # ৩. Vignette ফিল্টার দিয়ে চারপাশ অন্ধকার করে মাঝখানে লাইটিং গ্লো করা।
                # ৪. ফ্রিকশন ও নয়েজ জেনারেটর দিয়ে স্ক্রিনে ভাসমান ডাস্ট/আলোর কণা (Particles) তৈরি করা।
                cinematic_vf = (
                    "scale=1320:742,setsar=1,"
                    "zoompan=z='1.04+0.02*hypot(sin(on*0.4),cos(on*0.25))':x='iw/2-(iw/zoom)/2+7*sin(on*0.4)':y='ih/2-(ih/zoom)/2+7*cos(on*0.25)':d=1:s=1280x720,"
                    "vignette=angle=0.5:x='iw/2':y='ih/2',"
                    "eq=brightness=0.01:contrast=1.04:saturation=0.95,"
                    "noise=alls=12:allf=t+u"
                )
                
                command = [
                    ffmpeg_exe, '-y',
                    '-loop', '1', '-i', input_image_path,
                    '-i', input_audio_path,
                    '-vf', cinematic_vf,
                    '-af', af_filter,
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
                    '-c:a', 'aac', '-shortest',
                    output_video_path
                ]
                
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                    st.success("🎉 আলহামদুলিল্লাহ ভাই! আপনার প্রিমিয়াম সিনেমাটিক লো-ফাই ভিডিওটি এখন সম্পূর্ণ তৈরি।")
                    
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
                    st.error("❌ ভিডিও তৈরি করা যায়নি। নিচে এরর দেওয়া হলো:")
                    st.code(result.stderr)
                    
                if os.path.exists(input_audio_path): os.remove(input_audio_path)
                if os.path.exists(input_image_path): os.remove(input_image_path)
                
            except Exception as e:
                st.error(f"দুঃখিত ভাই, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")
