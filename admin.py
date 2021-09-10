from flask import  Flask, jsonify,request, render_template, abort,url_for,send_file
from werkzeug.utils import secure_filename
import nltk
from pydub import AudioSegment
from collections import Counter
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from speetch import  Speetch
from flask_cors import CORS
import subprocess
import  os
import shutil
import re
import string
from flask_ngrok import run_with_ngrok
from nltk.corpus import stopwords
import spacy
from spacy import displacy
from nltk.tokenize import WhitespaceTokenizer,WordPunctTokenizer,TreebankWordTokenizer,RegexpTokenizer
nlp = spacy.load('en_core_web_sm')
app=Flask(__name__)
cors = CORS(app, resources={r"/templates": {"origins": "*"}})
stop_words=set(stopwords.words("english"))  
output = {}
audio_to_text=Speetch()
audio_file_path=""
sid = SentimentIntensityAnalyzer()

def preprocessing(doc3):
  #remove repeated word
  doc1=' '.join(dict.fromkeys(doc3.split()))
  #sentence convert into token
  doc1 = WhitespaceTokenizer().tokenize(doc1)
  doc1=" ".join(doc1)
  doc1=RegexpTokenizer(r'\w+').tokenize(doc1)
  #we are able to extract the tokens from string of words or sentences in the form of Alphabetic and Non-Alphabetic
  filtered_sent=[]
  #remove stop word
  filtered_sent = [w for w in doc1 if not w in stop_words]
  tagged = nltk.pos_tag(filtered_sent)
  person_words=['NN' ,'PRP','NNP','CD','NNS']
  word=  [i[0] for i in tagged if not i[1] in person_words]
  doc1=' '.join(w for w in word)
  return doc1


def separate_pos_neg_neu(words_sent):
  words = WhitespaceTokenizer().tokenize(words_sent)
  pos_word_list=[]
  neu_word_list=[]
  neg_word_list=[]
  for word in words:
    my_dict=sid.polarity_scores(word)
    k = Counter(my_dict)
    high = k.most_common(1)
    if high[0][1]==0.0:
      pass
    elif high[0][0]=="pos":
      pos_word_list.append(word)
    elif high[0][0]=="neg":
      neg_word_list.append(word)
    else:
      neu_word_list.append(word)  
  Dict = {'Postive': pos_word_list,'Negative':neg_word_list,'Neutral':neu_word_list}
  return Dict

def sentiment(sentence):
    sentence=preprocessing(sentence)
    score = sid.polarity_scores(sentence)['compound']
    print(sid.polarity_scores(sentence))
    if(score>= 0.5):
        result= "Positive"
    elif (score <= -0.5):
        result= "Negative"
    else:
        result= "netural"
    dict={"percentage":sid.polarity_scores(sentence),"result":result}
    return dict
    
def sentimentRequest(text):
    sentence = text
    sent = sentiment(sentence)
    output['sentiment'] = sent
    return output


def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))

      


def highlight_text(doc1,positive,negative,neutral):
  tokenized_word=WhitespaceTokenizer().tokenize(doc1)
  filtered_sent=[]
  for w in tokenized_word:
    for pos in positive:
      if (w==pos):
        w=f'<span id="postive">{w}</span>'
    for neg in negative:
      if (w==neg):
        w=f'<span id="negative">{w}</span>'    
    for neu in neutral:
      if (w==neu):
        w=f'<span id="neutral">{w}</span>'                
    filtered_sent.append(w)
  return " ".join([t  for t in filtered_sent])

def delete_file_tree(file):
  try:
    folder_name = "audio-chunks"
    if  os.path.isdir(folder_name):
      shutil.rmtree(folder_name)
    if os.path.exists(file):
      os.remove(file)
  except :
    pass 

def all_code(file):
    print(file)
    AudioSegment.from_wav(f"{file}").export(f"static/audio/mp3/{file[:-4]}.mp3", format="mp3")
    audio_to_text_var=audio_to_text.get_large_audio_transcription(file)
    delete_file_tree(file)
    result=sentimentRequest(audio_to_text_var)
    positive=result['sentiment']['percentage']['pos']*100
    negative=result['sentiment']['percentage']['neg']*100
    netural=result['sentiment']['percentage']['neu']*100
    sent_result=result['sentiment']['result']
    
    separate_word=separate_pos_neg_neu(preprocessing(audio_to_text_var))
    hight_text=highlight_text(audio_to_text_var,separate_word['Postive'],separate_word['Negative'],separate_word['Neutral'])
    return jsonify(data=f"{file[:-4]}.mp3",sentiment_result=sent_result,postive=int(positive),negative=int(negative),netural=int(netural),song=hight_text)
    
@app.route('/')
def upload_file():
   return render_template('admin.html')
@app.route('/admin')
def upload_file1():
   return render_template('file_upload_form.html')



@app.route("/upload" ,methods = ['GET', 'POST'],endpoint='testpge')
def dummy_api():
  if request.method == 'POST':
    f = request.files['file']
    f.save(secure_filename(f.filename))
  file=secure_filename(f.filename) 
  print(file)
  return all_code(file) 
  

if __name__=="__main__":
    app.run()