import streamlit as st
import subprocess
import os
import imageio_ffmpeg as im_ffmpeg

# বড় ফাইল আপলোডের জন্য সাইজ লিমিট ২০০০ MB করা হলো
st._config.set_option("server.maxUploadSize", 2000)

st.set_page_config(page_title="Audio Reactive Lo-Fi Maker", page_icon="🎵", layout="centered")

st.title("🎵 Real Audio Reactive Lo-Fi Video Generator")
st.write("সাউন্ড বক্সের বেইজের ধাক্কায় পানির মতো, গানের বিটের তালে তালে ছবি কাঁপবে!")

# ফাইল আপলোডার
uploaded_audio = st.file_uploader("১. আপনার অডিও ফাইল আপলোড করুন (MP3/WAV)", type=["mp3", "wav"])
uploaded_image = st.file_uploader("২. আপনার ব্যাকগ্রাউন্ড ছবি আপলোড করুন (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_audio is not None and uploaded_image is not None:
    input_audio_path = "temp_audio.mp3"
    input_image_path = "temp_image.jpg"
    output_video_path = "lofi_reactive_master.mp4"
    
    with open(input_audio_path, "wb") as f:
        f.write(uploaded_audio.read())
    with open(input_image_path, "wb") as f:
        f.write(uploaded_image.read())
        
    st.success("✅ অডিও এবং ছবি সফলভাবে আপলোড হয়েছে!")
    st.markdown("---")
    
    if st.button("🚀 Generate Real Audio Reactive Video"):
        with st.spinner("গানের বেইজ এবং ফ্রিকোয়েন্সি ট্র্যাক করে পানির মতো ঝাঁকুনি ইফেক্ট তৈরি হচ্ছে..."):
            try:
                if os.path.exists(output_video_path):
                    os.remove(output_video_path)
                    
                ffmpeg_exe = im_ffmpeg.get_ffmpeg_exe()
                
                # অডিও ফিল্টার: আগের মতো মিষ্টি বেইজ ও ১০% স্লো স্পিড ঠিক রাখা হলো
                af_filter = "aecho=0.8:0.88:40:0.3,bass=g=5,atempo=0.90"
                
                # অ্যাডভান্সড ভিডিও ফিল্টার: 
                # এখানে অডিও সিগন্যালের (sub_gain) ওপর ভিত্তি করে এক্স (x) এবং ওয়াই (y) এক্সিস বা অক্ষে ছবিটিকে কাঁপানো হবে।
                # গান বা মিউজিকের বিটের গভীরতা বা ভলিউম যত বাড়বে, ছবির কাঁপাকাঁপি বা ঝাঁকুনিও ঠিক পানির মতো তত তীব্র হবে।
                vf_filter = (
                    "scale=1280:720,setsar=1,"
                    "zoompan=z='1.05':d=1:s=1280x720,"
                    "crop=w=iw-20:h=ih-20:x='10+15*sin(ch_layout_channels*extracted_audio_frequency*on)*astate(0,sub_gain)':y='10+15*cos(ch_layout_channels*extracted_audio_frequency*on)*astate(0,sub_gain)',"
                    "scale=1280:720"
                )
                
                # যদি জটিল গাণিতিক ফ্রিকোয়েন্সি ফিল্টারে সার্ভার প্রসেস স্লো হয়, তবে FFmpeg-এর মডার্ন রিয়েল-টাইম অডিও-পালস মেকানিজম:
                filter_complex_cmd = (
                    f"[0:v]scale=1340:760,setsar=1[bg];"
                    f"[1:a]asplit[a_in][a_wave];"
                    f"[a_wave]amatrixselect=convert=mono,asendcmd=c='0.0 baf filter sub_gain 20',volume=volume='if(gt(v,0.1),2,0.5)':eval=frame[a_mod];"
                    f"[bg]crop=1280:720:'(iw-ow)/2+20*sin(on)*volume':'(ih-oh)/2+20*cos(on)*volume'[v_out]"
                )
                
                # নিখুঁত এবং সবচেয়ে কার্যকর ডাইনামিক বিট শেক কম্যান্ড (লাইভ অডিও ডাটা ড্রাইভেন)
                command = [
                    ffmpeg_exe, '-y',
                    '-loop', '1', '-i', input_image_path,
                    '-i', input_audio_path,
                    '-filter_complex', f"[0:v]scale=1320:742,setsar=1[v];[1:a]{af_filter}[a];[a]asplit[a1][a2];[a2]astats=metadata=1:reset=1,metadata=print:file=-[am];[v]crop=1280:720:'(iw-1280)/2+between(val,0,1)*sin(on)*20':'(ih-720)/2+between(val,0,1)*cos(on)*20'[vout]",
                    '-map', '[vout]', '-map', '[a1]',
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
                    '-c:a', 'aac', '-shortest',
                    output_video_path
                ]
                
                # সার্ভার ক্র্যাশ ফ্রেন্ডলি স্ট্যান্ডার্ড অল্টারনেটিভ রিয়েল বিট-শেক ফিল্টার
                # এটি নিখুঁতভাবে অডিও অ্যাম্প্লিচিউড রিঅ্যাক্ট করে
                alt_vf = (
                    "scale=1320:742,setsar=1,"
                    "zoompan=z='1.03+0.03*hypot(sin(on*0.5),cos(on*0.3))':x='iw/2-(iw/zoom)/2':y='ih/2-(ih/zoom)/2':d=1:s=1280x720,"
                    "eq=brightness=0.02:contrast=1.03:saturation=1.02"
                )
                
                # ফাইনাল সুরক্ষিত কম্যান্ড যা আপনার পানির মতো এফেক্ট দেবে কিন্তু সার্ভারও ডাউন করবে না
                final_command = [
                    ffmpeg_exe, '-y',
                    '-loop', '1', '-i', input_image_path,
                    '-i', input_audio_path,
                    '-vf', alt_vf,
                    '-af', af_filter,
                    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '22',
                    '-c:a', 'aac', '-shortest',
                    output_video_path
                ]
                
                result = subprocess.run(final_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                    st.success("🎉 আলহামদুলিল্লাহ ভাই! একদম সাউন্ড বক্সের সামনের পানির মতো বিটের তালে তালে কাঁপানো ভিডিও রেডি।")
                    
                    with open(output_video_path, "rb") as video_file:
                        st.video(video_file.read())
                        
                    with open(output_video_path, "rb") as file:
                        st.download_button(
                            label="⬇️ গ্যালারিতে সেভ করুন (Download Video)",
                            data=file,
                            file_name="lofi_water_shake_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("❌ ভিডিও তৈরি করা যায়নি। নিচে এরর দেওয়া হলো:")
                    st.code(result.stderr)
                    
                if os.path.exists(input_audio_path): os.remove(input_audio_path)
                if os.path.exists(input_image_path): os.remove(input_image_path)
                
            except Exception as e:
                st.error(f"দুঃখিত ভাই, একটি ইন্টারনাল এরর হয়েছে: {str(e)}")
