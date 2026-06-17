import numpy as np
import librosa
import matplotlib.pyplot as plt
import moviepy.editor as mpy
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import os

def create_visualizer():
    print("--- Oisu Vibes অডিও ভিজ্যুয়ালাইজার মেকার ---")
    
    # ১. ইউজারের কাছ থেকে ইনপুট নেওয়া
    audio_path = input("আপনার রেডি করা গানের নাম দিন (যেমন: song.mp3): ").strip()
    image_path = input("ব্যাকগ্রাউন্ড ছবির নাম দিন (যেমন: background.jpg): ").strip()
    
    if not os.path.exists(audio_path) or not os.path.exists(image_path):
        print("দুঃখিত! গান বা ছবির ফাইলটি খুঁজে পাওয়া যায়নি। দয়া করে নাম ও এক্সটেনশন চেক করুন।")
        return

    output_path = input("তৈরি হওয়া ভিডিওর কী নাম দিতে চান? (যেমন: final_video.mp4): ").strip()
    
    # পুরো গানটার ওপরই ভিজ্যুয়ালাইজার তৈরি হবে
    print("\nঅডিও প্রসেস হচ্ছে, দয়া করে একটু অপেক্ষা করুন...")
    
    # অডিওর পুরো লেন্থ এবং ডেটা লোড করা
    y, sr = librosa.load(audio_path)
    duration = librosa.get_duration(y=y, sr=sr)
    
    hop_length = 512
    stft = np.abs(librosa.stft(y, hop_length=hop_length))
    frequencies = librosa.amplitude_to_db(stft, ref=np.max)

    # ২. ফ্রেম রেট সেটিংস (রিলসের জন্য ২৪ এফপিএস পারফেক্ট)
    fps = 24
    n_frames = int(duration * fps)
    frame_indices = np.linspace(0, frequencies.shape[1] - 1, n_frames).astype(int)

    frames_list = []

    # রিলস সাইজ ৯:১৬ অনুপাতের জন্য ফিগার সেট করা
    fig, ax = plt.subplots(figsize=(6, 10), facecolor='none')
    bg_img = plt.imread(image_path)

    print(os.path.basename(audio_path) + " গানের তালে তালে ফ্রেম তৈরি হচ্ছে...")
    
    # ৩. প্রতিটা ফ্রেমে বিট জেনারেট করা
    for i in range(n_frames):
        ax.clear()
        
        # ব্যাকগ্রাউন্ড ইমেজ বসানো
        ax.imshow(bg_img, extent=[0, 40, -50, 20], aspect='auto')
        
        # অডিও ফ্রিকোয়েন্সি ডেটা (মাঝের বারগুলো সুন্দর দেখানোর জন্য ১০ থেকে ৫০ পর্যন্ত নেওয়া)
        data = frequencies[10:50, frame_indices[i]] 
        x = np.arange(len(data))
        
        # লফি ভাইবের পার্পল/ম্যাজেন্টা কালারের বিট বার তৈরি
        ax.bar(x, data, color='#bf55ec', edgecolor='white', alpha=0.8, width=0.6)
        
        # বাড়তি বর্ডার ও গ্রাফের দাগ লুকিয়ে ফেলা
        ax.set_ylim(-40, 10)
        ax.set_xlim(-1, len(data))
        ax.axis('off')
        
        # ফ্রেমটি মেমরিতে সেভ করা
        fig.canvas.draw()
        frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frames_list.append(frame)

    plt.close()

    # ৪. মুভি পাই দিয়ে অডিও এবং ভিডিও এক করা
    print("ভিডিও এবং অডিও একসাথে জোড়া লাগানো হচ্ছে...")
    video_clip = ImageSequenceClip(frames_list, fps=fps)
    audio_clip = mpy.AudioFileClip(audio_path)

    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_path, fps=fps, codec="libx264", audio_codec="aac")

    print(f"\nআলহামদুলিল্লাহ! আপনার ভিডিও সফলভাবে তৈরি হয়েছে: {output_path}")

if __name__ == "__main__":
    create_visualizer()