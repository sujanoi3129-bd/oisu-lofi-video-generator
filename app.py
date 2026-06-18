import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Lo-Fi Studio Pro", page_icon="🎧", layout="centered")

st.title("🎧 Lo-Fi Studio Pro")
st.write("ঝামেলাহীন ও ত্রুটিমুক্ত লফি ভিডিও এবং অডিও মেকার।")

# নতুন সহজ ২-ট্যাব সিস্টেম
tab1, tab2 = st.tabs(["🖼️ গ্যালারি থেকে থাম্বনেইল", "🔊 শুধুমাত্র অডিও প্রসেস"])

input_image_path = "temp_image.jpg"
image_ready = False
mode = None

# ট্যাব ১: গ্যালারি থেকে আপলোড
with tab1:
    st.subheader("১. আপনার তৈরি করা সুন্দর থাম্বনেইলটি দিন")
    uploaded_image = st.file_uploader("আপনার ডিভাইস থেকে ছবি আপলোড করুন (JPG/PNG)", type=["jpg", "jpeg", "png"], key="user_gallery_uploader")
    if uploaded_image is not None:
        with open(input_image_path, "wb") as f:
            f.write(uploaded_image.read())
        st.image(input_image_path, caption="✅ আপনার আপলোড করা ফাইনাল থাম্বনেইল", use_column_width=True)
        image_ready = True
        mode = "Upload"

# ট্যাব ২: শুধুমাত্র অডিও মোড
with tab2:
    st.subheader("১. অডিও মোড সক্রিয়")
    st.info("💡 এই মোডে কোনো ভিডিও তৈরি হবে না। আপনার গানটি চমৎকার লফি (Slowed + Reverb) অডিও হিসেবে তৈরি হবে।")
    mode = "AudioOnly"

st.markdown("---")
st.subheader("২. অডিও ফাইল এবং ফাইনাল মেকিং")
uploaded_audio = st.file_uploader("আপনার অডিও ফাইলটি আপলোড করুন (MP3/WAV)", type=["mp3", "wav"])

if uploaded_audio is not None:
    input_audio_path = "temp_audio.mp3"
    output_video_path = "final_lofi_master.mp4"
    output_audio_path = "processed_lofi_audio.mp3"
    
    with open(input_audio_path, "wb") as f:
        f.write(uploaded_audio.read())
        
    if st.button("🚀 প্রসেস শুরু করুন (Run Conversion)"):
        ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
        
        # প্রিমিয়াম ইকো বেইজ বুস্ট এবং ১০% স্লো স্পিড লফি ফিল্টার
        af_filter = "aecho=0.8:0.88:40:0.3,bass=g=6,atempo=0.90"
        
        # মোড অনুযায়ী কাজ করা
        if mode == "AudioOnly":
            with st.spinner("আপনার গানটিকে মিষ্টি লফি সাউন্ডে রূপান্তর করা হচ্ছে..."):
                try:
                    if os.path.exists(output_audio_path):
                        os.remove(output_audio_path)
                        
                    command = [
                        ffmpeg_exe, '-y',
                        '-i', input_audio_path,
                        '-af', af_filter,
                        '-c:a', 'libmp3lame', '-b:a', '192k',
                        output_audio_path
                    ]
                    
                    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
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
                    
        elif mode == "Upload":
            if image_ready and os.path.exists(input_image_path):
                with st.spinner("আপনার দেওয়া ছবি ও পানির মতো মোশন ইফেক্ট সহ ভিডিও তৈরি হচ্ছে..."):
                    try:
                        if os.path.exists(output_video_path):
                            os.remove(output_video_path)
                        
                        # ১০০% সুরক্ষিত সিনেমাটিক মোশন ফিল্টার (কোনো ম্যাথ এরর আসবে না)
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
                            st.success("🎉 আলহামদুলিল্লাহ ভাই! আপনার প্রিমিয়াম লফি ভিডিও সফলভাবে তৈরি হয়েছে।")
                            st.video(output_video_path)
                            with open(output_video_path, "rb") as file:
                                st.download_button(
                                    label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                                    data=file,
                                    file_name="lofi_final_video.mp4",
                                    mime="video/mp4"
                               )
                        else:
                            st.error("❌ ভিডিও তৈরি করা যায়নি।")
                            st.code(result.stderr)
                    except Exception as e:
                        st.error(f"ভুল ত্রুটি: {str(e)}")
            else:
                st.error("❌ ভাই, দয়া করে আগে ১ম ট্যাব থেকে আপনার তৈরি করা থাম্বনেইলটি আপলোড করে নিন।")
                
    # কাজ শেষে টেম্পোরারি ফাইল ডিলিট
    if os.path.exists(input_audio_path): os.remove(input_audio_path)
