# importing libraries 
import speech_recognition as sr  
import os
import re
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from pydub import AudioSegment
from pydub.silence import split_on_silence
from ibm_watson.websocket import RecognizeCallback, AudioSource

  
class Speetch:
    
    # create a speech recognition object
    def __init__(self):
      
        apikey="PO4LUUqowvXZZWm34enwHpV4twziHGEfa8GZVDhazGUR"
        url="https://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/08a8717e-1908-461f-974c-5c0ee0b37d19"
        authenticator=IAMAuthenticator(apikey)
        self.service = SpeechToTextV1(authenticator = authenticator)
        self.service.set_service_url(url)

  
    def decontracted(self,phrase):
      # specific
      phrase = re.sub(r"won\'t", "will not", phrase)
      phrase = re.sub(r"can\'t", "can not", phrase)
      # general
      phrase = re.sub(r"n\'t", " not", phrase)
      phrase = re.sub(r"\'re", " are", phrase)
      phrase = re.sub(r"\'d", " would", phrase)
      phrase = re.sub(r"\'ll", " will", phrase)
      phrase = re.sub(r"\'t", " not", phrase)
      phrase = re.sub(r"\'ve", " have", phrase)
      phrase = re.sub(r"\'m", " am", phrase)
      return phrase

    def get_large_audio_transcription(self,path):
        self.folder_name = "audio-chunks"
        if not os.path.isdir(self.folder_name):
            os.mkdir(self.folder_name)
        sound =AudioSegment.from_wav(path)  
        chunks = split_on_silence(sound,
        min_silence_len = 1000,
        silence_thresh = sound.dBFS-15,
        keep_silence=1000,
        )
        whole_text = ""
        for i, audio_chunk in enumerate(chunks, start=1):
            str=""
            try:
              chunk_filename = os.path.join(self.folder_name, f"chunk{path[:-4],i}.wav")
              audio_chunk.export(chunk_filename, format="wav")
              with open(chunk_filename, 'rb') as audio_file:
                try:
                  res=self.service.recognize(audio=audio_file,content_type="audio/wav",model='en-US_NarrowbandModel',continuous=True).get_result() 
                except sr.UnknownValueError as e:
                      pass
                else:
                  while bool(res.get('results')):
                    str = res.get('results').pop().get('alternatives').pop().get('transcript')+str[:]
                  whole_text += str
            except:
              pass
        
        whole_text=self.decontracted(whole_text)  
        print(whole_text)  
        return whole_text

if __name__=="__main__":
    print(Speetch().get_large_audio_transcription("vocals.wav"))