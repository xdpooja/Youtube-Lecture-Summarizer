from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
import subprocess
import speech_recognition as sr
from deepmultilingualpunctuation import PunctuationModel
from nltk.tokenize import sent_tokenize
from lmqg import TransformersQG

def download_audio(video_url):
    try:
        yt = YouTube(video_url,  on_progress_callback=on_progress)
        video = yt.streams.get_audio_only()
        destination = '.'
        out_file = video.download(output_path=destination)

        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)

        converted_file = new_file
        subprocess.call(['ffmpeg', '-i', converted_file, 'converted_to_wav_file.wav'])
        os.remove(new_file)

        return 'converted_to_wav_file.wav'
    except Exception as e:
        print(f"Error occurred during download or conversion: {str(e)}")
        return None

def transcribe(audio_file):
    try:
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_text = r.record(source)

        text_google = r.recognize_google(audio_text)
        string_google = str(text_google)

        # Add punctuation
        model = PunctuationModel()
        result = model.restore_punctuation(string_google)

        # Clean up
        os.remove(audio_file)

        return result
    except Exception as e:
        print(f"Error occurred during transcription: {str(e)}")
        return None

def generate_summary(text):
    try:
        # Tokenize text into sentences
        sentences = sent_tokenize(text)

        # Generate summary with QAG
        def chunk_paragraph(text, max_words=300):
            words = text.split()
            chunks = []
            current_chunk = ""
            for word in words:
                if len(current_chunk.split()) + len(word.split()) <= max_words:
                    current_chunk += word + " "
                else:
                    last_full_stop_index = current_chunk.rfind('.')
                    if last_full_stop_index != -1:
                        chunks.append(current_chunk[:last_full_stop_index + 1].strip())
                        current_chunk = current_chunk[last_full_stop_index + 1:].strip() + " " + word + " "
                    else:
                        chunks.append(current_chunk.strip())
                        current_chunk = word + " "

            if current_chunk:
                chunks.append(current_chunk.strip())

            return chunks

        max_words_per_chunk = 300
        chunks = chunk_paragraph(text, max_words_per_chunk)

        demo_chunk = chunks[0]
        model = TransformersQG('lmqg/t5-base-squad-qag')
        question_answer = model.generate_qa(demo_chunk)

        return question_answer
    except Exception as e:
        print(f"Error occurred during summary generation: {str(e)}")
        return None

def summarize_youtube_video(video_url):
    # Step 1: Download and convert audio
    audio_file = download_audio(video_url)
    if not audio_file:
        return "Error occurred during video processing."

    # Step 2: Transcribe the audio
    transcription = transcribe(audio_file)
    if not transcription:
        return "Error occurred during transcription."

    # Step 3: Generate summary
    summary = generate_summary(transcription)
    if not summary:
        return "Error occurred during summary generation."

    return summary

if __name__ == "__main__":
    video_url = input("Enter YouTube video URL: ")
    result = summarize_youtube_video(video_url)
    print("Summary:")
    print(result)
