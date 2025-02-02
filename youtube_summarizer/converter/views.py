from django.shortcuts import render
from django.http import HttpResponse
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os
import subprocess
import speech_recognition as sr
from pydub import AudioSegment
from deepmultilingualpunctuation import PunctuationModel
from nltk.tokenize import sent_tokenize
from lmqg import TransformersQG
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def api_summarize(request):
    from .serializers import YouTubeURLSerializer
    if request.method == 'POST':
        serializer = YouTubeURLSerializer(data=request.data)
        if serializer.is_valid():
            video_url = serializer.validated_data['video_url']
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
                summary = transcribe()
                return Response({'summary': summary})
            except Exception as e:
                return Response({'error': str(e)}, status=400)
        return Response(serializer.errors, status=400)

def converting(request):
    summary = ""
    if request.method == 'POST':
        video_url = request.POST.get('video_url', '')
        if video_url:
            try:
                yt = YouTube(video_url)
                video = yt.streams.filter(only_audio=True).first()
                destination = '.'
                out_file = video.download(output_path=destination)

                base, ext = os.path.splitext(out_file)
                new_file = base + '.mp3'
                os.rename(out_file, new_file)

                converted_file = new_file
                subprocess.call(['ffmpeg', '-i', converted_file, 'converted_to_wav_file.wav'])
                os.remove(new_file)
                summary = transcribe()
            except Exception as e:
                summary = f'Error occurred: {str(e)}'

    return render(request, 'converter/index.html', {'summary': summary})

def transcribe():
    global result
    current_directory = os.getcwd()
    all_files = os.listdir(current_directory)
    wav_files = [file for file in all_files if file.endswith('.wav')]

    file_audio = sr.AudioFile(wav_files[0])

    r = sr.Recognizer()
    with file_audio as source:
        audio_text = r.record(source)

    text_google = r.recognize_google(audio_text)
    string_google = str(text_google)

    model = PunctuationModel()
    result = model.restore_punctuation(string_google)

    os.remove(os.path.join(current_directory, wav_files[0]))

    sentences = sent_tokenize(result)
    QAG()
    return result

def QAG():
    def chunk_paragraph(text, max_words=300):
        words = result.split()
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
    chunks = chunk_paragraph(result, max_words_per_chunk)

    demo_chunk = chunks[0]
    model = TransformersQG('lmqg/t5-base-squad-qag')
    question_answer = model.generate_qa(demo_chunk)
    return question_answer
