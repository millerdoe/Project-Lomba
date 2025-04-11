
from os import getenv
from dotenv import load_dotenv
import re
from datetime import datetime
from  requests import get
from bs4 import BeautifulSoup
from googlesearch import search
from openai import OpenAI
from hashlib import sha256
from sqlite3 import connect, Connection
from flask import Flask, render_template, request, session, redirect, url_for


def Ai(query:str):
    
    load_dotenv(dotenv_path=".env")

    
    client = OpenAI(
      base_url="https://openrouter.ai/api/v1",
      api_key=f"{getenv("API_KEY")}"

         )
         
    try:   
            completion = client.chat.completions.create(
            extra_headers={
             "HTTP-Referer": "https://openrouter.ai/deepseek/deepseek-r1-distill-qwen-32b:free/api", 
             "X-Title": "DeepSeek: R1 Distill Qwen 32B (free)  Run with an API | OpenRouter", 
           },
            extra_body={},
            model="deepseek/deepseek-r1-distill-qwen-32b:free",
            messages=[
             {
               "role": "user",
               "content": f"{query}"
             }
           ]
         )
            hasil_query = completion.choices[0].message.content
    except Exception as err:
            print(err)

            hasil_query = "maaf ada kesalahan silahkan coba lagi!"

    return hasil_query
    

def pencarian_web(query, num_results):  
    img_url = []    
    result_list = []

    for url in search(query, start_num=0, num_results=num_results):     
        try:      
            response = get(url)           
            response.raise_for_status()            
            soup = BeautifulSoup(response.text, 'html.parser')           
            title = soup.title.string if soup.title else f"article dengan topik {query}"            
            img_tag = soup.find('img')           
            img_url = img_tag['src']             
            if img_tag and "src" in img_tag.attrs:                
                if re.search("^http", img_url):                    
                  img_url = img_url               
                elif not re.search("^http", img_url):
                    img_url = f"{url}/{img_url}"
                else:                   
                  img_url = "static/img/not_found.jpeg"      


            result_list.append({"title": title, 
                                  "url": url,               
                                 "img_url": img_url 
                                 
                        })
                           
        except Exception as e:            
            print(f"Error fetching {url}: {e}")    
                
    return result_list

def hess_passwd(password):
        random = "ods0KSAjoau0w39-2-238ao" + password + "dsahjueauHOIAUSjsd54534"
        hess = sha256(random.encode("UTF-8"))
        lihat_hess = hess.hexdigest()
        return lihat_hess



buat_table = """
             CREATE TABLE IF NOT EXISTS users(
             username TEXT PRIMARY KEY NOT NULL,
             kelas TEXT NOT NULL,
             password TEXT NOT NULL,
             datetime TEXT NOT NULL
             )
"""


app = Flask(__name__)

load_dotenv(dotenv_path="key/.env", encoding="UTF-8")
sekret_key = getenv("FLASK_SECRET_KEY")
app.config["SECRET_KEY"] = sekret_key

@app.route("/")
def index():
    username = ""
    kelas = ""
    time = ""
    if "username" in session:
        if "password" in session:
            username = session.get("username")
            kelas = session.get("kelas")
            time =  session.get("datetime")
            return render_template("success.html", username=username, kelas=kelas, time=time)

    return  redirect(url_for("home"))

@app.route("/index", methods=["POST", "GET"])
def home():
    query = ""
    hasil = []
    if request.method == "POST":
        query = request.form.get("query")
        hasil = pencarian_web(query, 15)


    return render_template("index.html", hasil=hasil, query=query)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").lower()
        password =  request.form.get("password")
        
        with Connection("dbusers.db") as dbconn:
            ijin_exe_q = dbconn.cursor()
            ijin_exe_q.execute("SELECT username, kelas, password, datetime FROM users")
            data = ijin_exe_q.fetchall()
            for lihat_data  in data:
                if username in lihat_data:
                    if hess_passwd(password) in lihat_data:
                        session["kelas"] = lihat_data[1]
                        session["username"] = username
                        session["password"] = hess_passwd(password)
                        session["datetime"] = lihat_data[3]
                        return redirect(url_for("index"))
    if "username" in session:
        if "password" in session:
            return redirect(url_for("index"))
                    
                    
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username").lower()
        kelas =  request.form.get("kelas")
        password =  request.form.get("password")

        get_Time = datetime.now()
        timeR = get_Time.strftime("%c")

        if len(username) >= 5:
            username_valid = username

        if len(password) >= 8:
            password_valid = password

        try:
            with connect("dbusers.db") as dbconn:
                ijin_exe_q = dbconn.cursor()
                ijin_exe_q.execute(buat_table)
                ijin_exe_q.execute("INSERT INTO users(username, kelas, password, datetime) VALUES (?, ?, ?, ?)", (username_valid, kelas, hess_passwd(password_valid), timeR))
                if ijin_exe_q:
                    dbconn.commit()
                    return redirect(url_for("login"))
                
        except:
            pass


    return render_template("register.html")

@app.route("/ai", methods=["POST", "GET"])
def ai():
    query = ""
    hasil = ""
    if request.method == "POST":
        query = request.form.get("cari")

        hasil = Ai(query)


    return render_template("AI.html", query=query, hasil=hasil)


@app.route("/log_out")
def log_out():
   
    session.pop("username")
    session.pop("password")
    session.pop("kelas")
    session.pop("datetime")


    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

