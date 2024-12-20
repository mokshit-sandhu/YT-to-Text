from flask import Flask, render_template, request, jsonify
import yt_dlp
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os

app = Flask(__name__)

def download_audio(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def split_audio(file_path):
    audio = AudioSegment.from_wav(file_path)
    chunks = split_on_silence(
        audio, 
        min_silence_len=1000,  
        silence_thresh=-40,    
        keep_silence=500       
    )
    return chunks

def audio_to_text(chunks):
    r = sr.Recognizer()
    full_text = ""
    for i, chunk in enumerate(chunks):
        chunk_file = f"chunk{i}.wav"
        chunk.export(chunk_file, format="wav")
        with sr.AudioFile(chunk_file) as source:
            audio = r.record(source)
            try:
                text = r.recognize_google(audio)
                full_text += text + " "
            except sr.UnknownValueError:
                full_text += "[Unrecognized speech] "
            except sr.RequestError as e:
                full_text += f"[Error: {e}] "
        
        # Delete the temporary chunk file
        os.remove(chunk_file)
    
    return full_text

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.get_json()
    video_url = data.get('youtube_url')
    
    download_audio(video_url)
    chunks = split_audio('audio.wav')
    transcription = audio_to_text(chunks)
    
    # Delete the main audio file
    os.remove('audio.wav')
    
    return jsonify({'transcription': transcription})

if __name__ == '__main__':
    app.run(debug=True)
