#!/usr/bin/env python
# coding: utf-8

# In[18]:

from InstagramAPI import InstagramAPI
import time
from datetime import datetime
import requests
import pandas as pd
import pathlib
from google.cloud import storage
import os
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"V:\Analisis\BMW\GCP\Credenciales\apisrrss-cafafda4cd06.json"
#import re


# In[4]:

API = InstagramAPI('LorenIpsum__','Delfin13')
#API = InstagramAPI('anadrion@gmail.com','mpizmmku')
API.login()
print("Cuantas veces entra aqui")

def get_media_id(url):
    #print ('INICIO RUTINA GET URL', time.strftime("%H:%M:%S"))
    try:
        req = requests.get('https://api.instagram.com/oembed/?url={}'.format(url))
        media_id = req.json()['media_id']
        #print ('FIN RUTINA GET URL', time.strftime("%H:%M:%S"))
        return media_id
    except: 
        print ("URL no válida, sorry")


# In[5]:


def date_conversor (created_date):
    from datetime import datetime
    fecha = created_date
    dt_object = datetime.fromtimestamp(fecha)

    return dt_object


# In[6]:


def get_posts_like(API, media_id):
    #print ('INICIO RUTINA GET LIKE', time.strftime("%H:%M:%S"))
    
    '''Retrieve all likers on one post'''
    likers = []
    API.getMediaLikers(media_id)
    li = API.LastJson
    for position in range (0, len(li.get('users'))):
        likers.append((li.get('users')[position]['username']))   
    counter = len(likers)
    #print ('FIN RUTINA GET LIKE', time.strftime("%H:%M:%S"))

    return likers, counter


# In[7]:


def save_comments(API, media_id):
    #print ('INICIO RUTINA SAVE COMMENTRS', time.strftime("%H:%M:%S"))
    has_more_comments = True
    max_id = ''
    comments = []
    #guarda en COMMENTS todos los cometnarios del post. 

    until_date = '2019-03-31'
    count = 10000
    while has_more_comments:

        _ = API.getMediaComments(media_id, max_id=max_id)
        # comments' page come from older to newer, lets preserve desc order in full list
        print("El valor de media_id es: " + str(media_id))
        for c in reversed(API.LastJson['comments']):
            comments.append(c)
        has_more_comments = API.LastJson.get('has_more_comments', False)
        # evaluate stop conditions
        if count and len(comments) >= count:
            comments = comments[:count]
            
            # stop loop
            has_more_comments = False
            print ('stopped by count')
        if until_date:
            older_comment = comments[-1]
            dt = datetime.utcfromtimestamp(older_comment.get('created_at_utc', 0))
            # only check all records if the last is older than stop condition
            if dt.isoformat() <= until_date:
                # keep comments after until_date
                comments = [
                    c
                    for c in comments
                    #if datetime.utcfromtimestamp(c.get('created_at_utc', 0)) > until_date
                ]
                # stop loop
                has_more_comments = False
                print ('stopped by until_date')
        # next page
        if has_more_comments:
            max_id = API.LastJson.get('next_max_id', '')
            time.sleep(2)
            
    #print ('FIN RUTINA SAVE COMMENTRS', time.strftime("%H:%M:%S"))

    return comments


# In[8]:


def sentiment (one_comment):
    
    from textblob import TextBlob
    polarity_list = []
    numbers_list = []
    number = 1
    en_blob = TextBlob(one_comment)
    #Try para comprobar el idioma, si no sale..
    try: 
        idioma = en_blob.detect_language()
    except: 
        idioma = "not detected"

        
    try: 
        a = en_blob.translate(to='en')
        analysis = a
        analysis = analysis.sentiment
        #Guardar la polaridad
        polarity = analysis.polarity
        polarity_list.append(polarity)
        #Contar las veces que esa polaridad ha ocurrido
        numbers_list.append(number)
        number = number + 1
        if polarity > 0:
            sentiment =  ('POSITIVO')
        else: 
            sentiment =  ('NEGATIVO')
    except:
        sentiment = "Not defined"
        idioma = "Not defined"
        
    return idioma, sentiment


# In[9]:


def file_name():
    ahora = time.strftime("%c")
    name = ahora.replace(' ', '')
    name = name.replace(':', '')
    final_name = name + ".xlsx"
    return final_name


# In[10]:


def sentiment_data(sentimient):
    num_pos = 0
    num_neg = 0
    num_not = 0
    for word in sentimient: 
        if word == "POSITIVO":
            num_pos += 1
        elif word == "NEGATIVO":
            num_neg +=1
        else:
            num_not +=1
    total = len(sentimient)
    porcent_pos = round((num_pos * 100) / total,2)
    porcent_neg = round((num_neg * 100) / total,2)
    porcent_not = round((num_not * 100) / total,2)


    return porcent_pos, porcent_neg, porcent_not


# In[11]:


def linea_blanco (usuarios, comentarios, fecha_com, sentimient, idiomas):  
    usuarios.append('')
    comentarios.append('')
    fecha_com.append('')
    sentimient.append('')
    idiomas.append('')


# In[13]:


def resumen_final (usuarios, comentarios, fecha_com, sentimient, idiomas): 
    num_com = len(comentarios)
    linea_blanco (usuarios, comentarios, fecha_com, sentimient, idiomas)  
    linea_blanco (usuarios, comentarios, fecha_com, sentimient, idiomas)  
    linea_blanco (usuarios, comentarios, fecha_com, sentimient, idiomas)  

    usuarios.append('')
    comentarios.append('URL')
    fecha_com.append('')
    sentimient.append('')
    idiomas.append('')

    usuarios.append('')
    comentarios.append('Likes')
    fecha_com.append('')
    sentimient.append('')
    idiomas.append('')

    usuarios.append('')
    comentarios.append('Comments')
    fecha_com.append(num_com)
    sentimient.append('')
    idiomas.append('')

    linea_blanco (usuarios, comentarios, fecha_com, sentimient, idiomas)  

    usuarios.append('')
    comentarios.append('SENTIMENT')
    fecha_com.append('')
    sentimient.append('')
    idiomas.append('')

    usuarios.append('')
    comentarios.append('Positive')
    fecha_com.append('')
    sentimient.append('%')
    idiomas.append('')

    usuarios.append('')
    comentarios.append('Negative')
    fecha_com.append('')
    sentimient.append('%')
    idiomas.append('')

    usuarios.append('')
    comentarios.append('Not defined')
    fecha_com.append('')
    sentimient.append('%')
    idiomas.append('')
    
    return usuarios, comentarios, fecha_com, sentimient, idiomas


# In[42]:


def data_tabla (usuarios, comentarios, fecha_com, sentimient, idiomas):
    #Creamos la tabla y la guardamos en excel. Para el nombre del archivo se usa fecha_dia_hora
    data = pd.DataFrame({"user": usuarios, "comment": comentarios, "fecha comentario": fecha_com, "sentimiento": sentimient, "idioma": idiomas})

    save_name = file_name()
	#print("Ha llegado hasta aqui")
    #data.to_excel("testJavi.xlsx")#(save_name)
    return save_name


# In[19]:


def alla_vamos (API, url_post):

    #LOG IN
	
    #OBTIENE LA ID DEL POST POR LA FUNCIÓN GET_MEDIA_ID
    media_id = get_media_id(url_post)

    #Llenamnos la lista comments con el contenido del post. 
    comments = save_comments(API, media_id)
    print ('COMENTARIOS EXPORTADOS. COMENTARIOS TOTALES: ', len(comments))

    #saca un resumen, numero de comentarios y los imprime con autor y fecha.
    usuarios =[]
    comentarios = []
    fecha_com = []
    sentimient = []
    idiomas = []
    #print ('INICIO RUTINA CREAR TABLA CON INFO', time.strftime("%H:%M:%S"))

    for com in range(0, len(comments)):
        usuarios.append(comments[com]['user']['username'])
        comentarios.append(comments[com]['text'])
        fecha = date_conversor (comments[com]['created_at'])
        fecha_com.append(fecha)    
        #lang, sent = sentiment (comments[com]['text'])
        sentimient.append('')
        idiomas.append('')

    #print ('FIN RUTINA CREAR TABLA CON INFO', time.strftime("%H:%M:%S"))

    #Para saber cuantos likes tenemos.
    likers, counter = get_posts_like(API, media_id)

    #Para saber porcentajes de sentimientos

    num_pos, num_neg, num_not = sentiment_data(sentimient)

    #Añadir resumen final
    usuarios, comentarios, fecha_com, sentimient, idiomas = resumen_final (usuarios, comentarios, fecha_com, sentimient, idiomas)


    #Creamos tabla y nos devuelve file_name
    save_name = bucket_connect (usuarios, comentarios, fecha_com, sentimient, idiomas)

    return save_name

	
def bucket_connect(usuarios, comentarios, fecha_com, sentimient, idiomas):
	nombre = file_name()
	client = storage.Client()
	bucket = client.get_bucket('apiresults')
	data = pd.DataFrame({"user": usuarios, "comment": comentarios, "fecha comentario": fecha_com, "sentimiento": sentimient, "idioma": idiomas})
	
	data.to_excel("/tmp/"+nombre)
	
	#bucket.blob(nombre).upload_from_string(data.to_excel(), 'text/csv')
	blob = bucket.blob("/tmp/"+nombre)
	blob.upload_from_filename("/tmp/"+nombre)
	blob.make_public()
	url_str = "https://storage.cloud.google.com/apiresults//tmp/"+nombre
	#os.remove(nombre)
	return url_str


#url = "https://www.instagram.com/p/B3XUPeilKbx/"

from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])

def index():
    #greeting = "Hello World"
    if request.method == "POST":
        name = request.form['name']
        url_i = request.form['url']
        #greeting = f"{name}, {url_i}"
        greeting = alla_vamos (API, url_i)
        #greeting = bucket_connect
        return render_template("index.html", greeting=greeting)
    else:
        return render_template("hello_form.html")

if __name__ == "__main__":
    app.run()
