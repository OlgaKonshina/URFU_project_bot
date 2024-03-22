import whisper
import subprocess

subprocess.run(['ffmpeg', '-i', 'file_17.oga', 'file_17.wav'])
model = whisper.load_model('small')
print('Model loaded')
result = model.transcribe('file_17.wav', fp16 = False) # добавляем аудио для обработки
print(result['text'])