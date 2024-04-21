# converter/views.py

from django.shortcuts import render
from django.http import HttpResponse
from pytube import YouTube 
import os 
import subprocess
import speech_recognition as sr
from pydub import AudioSegment


def converting(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url', '')
        if video_url:
            try:
                yt = YouTube(video_url)
                video = yt.streams.filter(only_audio=True).first()
                destination = '.'  # Output directory
                out_file = video.download(output_path=destination) 

                base, ext = os.path.splitext(out_file)
                new_file = base + '.mp3'
                os.rename(out_file, new_file) 

                converted_file = new_file
                subprocess.call(['ffmpeg', '-i', converted_file, 'converted_to_wav_file.wav'])
                os.remove(new_file)
                transcribe()
                return HttpResponse('Your Summary is on its way!')

            
            except Exception as e:
                return HttpResponse(f'Error occurred: {str(e)}')
    return render(request, 'index.html')

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

    from deepmultilingualpunctuation import PunctuationModel
    model = PunctuationModel()

    result = model.restore_punctuation(string_google)


    os.remove(os.path.join(current_directory, wav_files[0]))

    #tokenizing the text into different sentences
    from nltk.tokenize import sent_tokenize
    sentences = sent_tokenize(result)
    print("**********Number of sentences found: ",len(sentences), "************")
    QAG()
    return HttpResponse(result)




def QAG():
    def chunk_paragraph(text, max_words=300):
        words = result.split()
        chunks = []
        current_chunk = ""
        
        for word in words:
            if len(current_chunk.split()) + len(word.split()) <= max_words:
                current_chunk += word + " "
            else:
                # Find the last full stop in the current chunk
                last_full_stop_index = current_chunk.rfind('.')
                
                # If a full stop is found, append the chunk until the last full stop
                if last_full_stop_index != -1:
                    chunks.append(current_chunk[:last_full_stop_index + 1].strip())
                    current_chunk = current_chunk[last_full_stop_index + 1:].strip() + " " + word + " "
                # If no full stop is found, append the current chunk as it is
                else:
                    chunks.append(current_chunk.strip())
                    current_chunk = word + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    # Example usage:
    max_words_per_chunk = 300
    chunks = chunk_paragraph(result, max_words_per_chunk)

    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}: {chunk}\n")


    demo_chunk = chunks[0]
    from pprint import pprint
    from lmqg import TransformersQG

    model = TransformersQG('lmqg/t5-base-squad-qag')
    question_answer = model.generate_qa(demo_chunk)
    pprint(question_answer)
    return HttpResponse(question_answer)