import random
import json
import self
import pickle
import numpy as np
import speech_recognition
import pyttsx3 as tts
import sys
import datetime
import time
import wikipedia
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

recognizer=speech_recognition.Recognizer()
speaker=tts.init()
voices=speaker.getProperty('voices')
speaker.setProperty('voice',voices[1].id)
speaker.setProperty('rate',170)
todo=[]

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import load_model

lemmatizer=WordNetLemmatizer
intents=json.loads(open('intents.json').read())

words=pickle.load(open('words.pkl','rb'))
classes=pickle.load(open('classes.pkl','rb'))
model=load_model('chatbot_model.h5')

import requests

api_key = "cd1a705e3a5f59b120ec6189e11f810e"

def get_weather(city_name):
    global temp
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}".format(city_name, api_key)

    response = requests.get(api_url)
    response_dict = response.json()

    weather = response_dict["weather"][0]["description"]
    temp=response_dict["main"]["temp"]
    temp="{:.2f}".format(temp-273.15)

    if response.status_code == 200:
        return weather
    else:
        print('[!] HTTP {0} calling [{1}]'.format(response.status_code, api_url))
        return None

import spacy
import requests

nlp=spacy.load("en_core_web_md")
#nlp=spacy.load("en_core_web_sm")
def chatbot(statement):
    weather=nlp("Current weather in city")
    statement=nlp(statement)
    min_similarity=0.4

    if weather.similarity(statement)>=min_similarity:
        for ent in statement.ents:
            if ent.label_ =="GPE":
                city=ent.text
                break
            else:
                res="You need to tell me a city to check"
                return res

        city_weather=get_weather(city)
        if city_weather is not None:
            res="In "+city+", the current weather is "+city_weather+ " and the temperature is "+str(temp)+" °C"
            return res
        else:
            res="something went wrong"
            return res
    else:
        res="sorry i don't understand that"
        return res

def yt(text):
    text = text.lower()
    co = Options()
    co.add_experimental_option("detach", True)
    driver = webdriver.Chrome(r"C:\chromedriver.exe", options=co)
    driver.implicitly_wait(1)
    driver.maximize_window()
    #ind = text.split()[2:]
    speaker.say("What do you want to play on Youtube?")
    speaker.runAndWait()
    ChatLog.config(state=NORMAL)
    ChatLog.insert(END, "Lyra : What do you want to play on Youtube?" + '\n\n')
    ChatLog.config(state=DISABLED)
    base.update()
    try:
        with speech_recognition.Microphone() as mic:
            recognizer.adjust_for_ambient_noise(mic,duration=0.2)
            audio=recognizer.listen(mic)
            name=recognizer.recognize_google(audio)
            ChatLog.config(state=NORMAL)
            ChatLog.insert(END, "You : " + name + '\n\n')
            ChatLog.config(state=DISABLED)
            base.update()
            name=name.split()
            driver.get("http://www.youtube.com/results?search_query=" + '+'.join(name))
            res="Youtube Opened"
            return res
    except(speech_recognition.UnknownValueError):
        res="Sorry could not understand that"
        return res



def clean_up_sentence(sentence):
    sentence_words=nltk.word_tokenize(sentence)
    sentence_words=[lemmatizer.lemmatize(self,word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence,words,show_details=True):
    sentence_words=clean_up_sentence(sentence)
    bag=[0]*len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word==w:
                bag[i]=1

    return(np.array(bag))

def predict_class(sentence,model):
    bow=bag_of_words(sentence,words,show_details=False)
    res=model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD=0.25
    results=[[i,r]for i,r in enumerate(res) if r>ERROR_THRESHOLD]

    results.sort(key=lambda x:x[1],reverse=True)
    return_list=[]
    for r in results:
        return_list.append({'intent':classes[r[0]],'probability':str(r[1])})
    return return_list

def get_response(intents_list,intents_json):
    tag=intents_list[0]['intent']
    list_of_intents=intents_json['intents']
    for i in list_of_intents:
        if i['tag']==tag:
            result=random.choice(i['responses'])
            break
    return result

from PyDictionary import PyDictionary
dict=PyDictionary()

def meaning(text):
    return dict.meaning(str(text).split()[2])['Noun'][0]

todo=[]
def create_note():
    global recognizer
    note="What do you want to write onto your note?"
    speaker.say(note)
    speaker.runAndWait()
    ChatLog.config(state=NORMAL)
    ChatLog.insert(END, "Lyra : " + note + '\n\n')
    ChatLog.config(state=DISABLED)
    base.update()

    done=False
    while not done:
        try:
            with speech_recognition.Microphone() as mic:
                recognizer.adjust_for_ambient_noise(mic,duration=1)
                audio=recognizer.listen(mic)
                note=recognizer.recognize_google(audio)
                note=note.lower()
                ChatLog.config(state=NORMAL)
                ChatLog.insert(END, "You : " + note + '\n\n')
                ChatLog.config(state=DISABLED)
                base.update()

                speaker.say("Choose a filename")
                speaker.runAndWait()
                ChatLog.config(state=NORMAL)
                ChatLog.insert(END, "Lyra : Choose a filename" + '\n\n')
                ChatLog.config(state=DISABLED)
                base.update()
                recognizer.adjust_for_ambient_noise(mic,duration=0.6)
                audio=recognizer.listen(mic)
                filename=recognizer.recognize_google(audio)
                filename=filename.lower()
                ChatLog.config(state=NORMAL)
                ChatLog.insert(END, "You : " + filename + '\n\n')
                ChatLog.config(state=DISABLED)
                base.update()

                with open(filename,'w') as f:
                    f.write(note)
                    done=True
            res = "successfully created the note"
        except speech_recognition.UnknownValueError:
            res="Sorry could not Understand That"

    return res

def add_todo():
    speaker.say("What todo you want to add")
    speaker.runAndWait()
    ChatLog.config(state=NORMAL)
    ChatLog.insert(END, "Lyra : What todo you want to add" + '\n\n')
    ChatLog.config(state=DISABLED)
    base.update()

    done=False

    while not done:
        try:
            with speech_recognition.Microphone() as mic:
                recognizer.adjust_for_ambient_noise(mic,duration=0.5)
                audio=recognizer.listen(mic)

                item=recognizer.recognize_google(audio)
                item=item.lower()
                todo.append(item)

                speaker.say("Do you want to add more todo in the list")
                speaker.runAndWait()
                ChatLog.config(state=NORMAL)
                ChatLog.insert(END, "Lyra : Do you want to add more todo in the list"  + '\n\n')
                ChatLog.config(state=DISABLED)
                base.update()
                audio=recognizer.listen(mic)
                ans=recognizer.recognize_google(audio)
                ChatLog.config(state=NORMAL)
                ChatLog.insert(END, "You : " + ans + '\n\n')
                ChatLog.config(state=DISABLED)
                base.update()
                if 'yes' in ans:
                    done=False
                else:
                    done=True
            res = "Todos added in the list"
        except speech_recognition.UnknownValueError:
            res="Sorry could not Understand That"
    return res

def show_todo():
    ChatLog.config(state=NORMAL)
    ChatLog.insert(END, "Lyra : The items on your list are" + '\n')
    #ChatLog.config(state=DISABLED)
    speaker.say("The items on your list are ")
    for item in todo:
        speaker.say(item)
        #ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "Lyra : " + item + '\n\n')
        ChatLog.config(state=DISABLED)
    speaker.runAndWait()





print("Bot is Running")
def chatbot_res(text):
    intents_list = predict_class(text, model)
    if intents_list[0]['intent']=='weather':
        res=chatbot(text)
        print('weather')
        speaker.say(res)
        speaker.runAndWait()
        return res
    elif 'search' in text:
        text=text.lower()
        #text = text.replace("search", "")
        co = Options()
        co.add_experimental_option("detach", True)
        driver = webdriver.Chrome(r"C:\chromedriver.exe", options=co)
        driver.implicitly_wait(1)
        driver.maximize_window()
        indx = text.split().index("search")
        ind = text.split()[indx + 1:]
        driver.get("https://www.google.com/search?client=firefox-b-d&q="+'+'.join(ind))
        print("https://www.google.com/search?client=firefox-b-d&q="+'+'.join(ind))
        speaker.say("Opened website")
        speaker.runAndWait()
        return ("searched "+text)
    elif intents_list[0]['intent']=='meaning':
        res=meaning(text)
        speaker.say(res)
        speaker.runAndWait()
        return res
    elif 'time' in text:
        res=datetime.datetime.now().strftime("%H:%M:%S")
        speaker.say(f"The time is {res}")
        speaker.runAndWait()
        return res
    elif intents_list[0]['intent']=='song':
        res=yt(text)
        speaker.say(res)
        speaker.runAndWait()
        return res
    elif intents_list[0]['intent']=='createnote':
        res=create_note()
        return res
    elif intents_list[0]['intent']=='addtodo':
        res=add_todo()
        return res
    elif intents_list[0]['intent']=='showtodo':
        res=show_todo()
        return res
    elif intents_list[0]['intent']=='bye':
        res=get_response(intents_list,intents)
        speaker.say(res)
        speaker.runAndWait()
        ChatLog.config(state=NORMAL)
        #ChatLog.insert(END, "You : " + text + '\n\n')

        ChatLog.insert(END, "Lyra : " + res + '\n\n')
        ChatLog.config(state=DISABLED)
        base.update()
        time.sleep(4)
        base.destroy()

    else:
        res = get_response(intents_list, intents)
        speaker.say(res)
        speaker.runAndWait()
        return res


import tkinter
from tkinter import *
from PIL import Image,ImageTk

def send():
    msg=EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0",END)

    if msg!='':
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END,"You : "+msg+'\n\n')

        ChatLog.config(foreground="#442265",font=("Verdana",12))
        ChatLog.config(state=DISABLED)
        base.update()
        res=chatbot_res(msg)
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END,"Lyra : "+res+'\n\n')
        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)

def micsend():
    global res,msg,msg1
    with speech_recognition.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic,duration=0.2)
        print("say anything")
        audio=recognizer.listen(mic)
        try:
            msg=recognizer.recognize_google(audio)
            ChatLog.config(state=NORMAL)
            ChatLog.insert(END, "You : " + msg + '\n\n')
            ChatLog.config(state=DISABLED)
            base.update()
            res = chatbot_res(msg)

        except:
            speaker.say("Sorry could not understand that")
            speaker.runAndWait()
            msg="Sorry could not Understand That"

    if msg=="Sorry could not Understand That":
        res=msg
    ChatLog.config(state=NORMAL)
    #ChatLog.insert(END, "You : " + msg + '\n\n')
    ChatLog.config(foreground="#442265", font=("Verdana", 12))
    ChatLog.insert(END, "Lyra : " + res + '\n\n')
    ChatLog.config(state=DISABLED)
    ChatLog.yview(END)


import tkinter
from tkinter import *
from PIL import Image,ImageTk
base=Tk()
base.title("LYRA")
base.geometry("500x550")
base.resizable(width=False,height=False)
#bg=ImageTk.PhotoImage(file="img.png")
bg1=Image.open("img2.jpg")
resi=bg1.resize((500,530),Image.ANTIALIAS)
bg1=ImageTk.PhotoImage(resi)

bg=Image.open("img3.png")
resize=bg.resize((200,330),Image.ANTIALIAS)
bg=ImageTk.PhotoImage(resize)

micb=Image.open("mic.jpg")
resiz=micb.resize((80,80),Image.ANTIALIAS)
micb=ImageTk.PhotoImage(resiz)

canvas=Canvas(base,width=40,height=20)
canvas.pack(expand=True,fill=BOTH)
#canvas.create_image(0,0,image=bg1,anchor="nw")
#canvas.create_image(295,60,image=bg,anchor="nw")
bg2=Image.open("bg.jpg")
re=bg2.resize((500,600),Image.ANTIALIAS)
bg2=ImageTk.PhotoImage(re)
canvas.create_image(0,0,image=bg2,anchor="nw")


ChatLog=Text(base,bd=0,bg="#e6e2c1",height="8",width="40",font="Arial")

ChatLog.config(state=DISABLED)

scrollbar=Scrollbar(base,command=ChatLog.yview,cursor="heart")
ChatLog['yscrollcommand']=scrollbar.set


sendbutton=Button(base,font=("Arial Black",15,'bold'),text="Send",width='9',height=5,bd=0,bg="#c9b940",activebackground='#2c12c4',fg="#b80920",command=send)

micbutton=Button(base,image=micb,font=("Arial Black",12),text="Mic",width='55',height=5,bg="#f5e5ab",bd=2,activebackground='#91e4e6',fg='#cf1d38',command=micsend)

EntryBox=Text(base, bd=0,bg='#e6e2c1',width='29',height='5',font='Arial')


scrollbar.place(x=450,y=60,height=330)
ChatLog.place(x=67,y=60,height=330,width=375)
EntryBox.place(x=200,y=411,height=90,width=265)
sendbutton.place(x=60,y=411,height=90)
micbutton.place(x=240,y=10,height=50)

base.mainloop()