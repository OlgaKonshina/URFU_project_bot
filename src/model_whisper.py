#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import whisper

model = whisper.load_model('small')
result = model.transcribe('audio_6.ogg', fp16=False) # добавляем аудио для обработки
print(result['text'])

