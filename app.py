import os
import re
import pickle
from flask import Flask, render_template, request,session, redirect, url_for
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import keras
import tensorflow 
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import nltk
import config

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Initialize Flask app
app = Flask(__name__) 
app.secret_key = config.SECRET_KEY
# Load pre-trained model and tokenizer
loaded_model = load_model("LSTM.h5")

with open('tokenizer.pickle', 'rb') as f:
    tokenizer = pickle.load(f)

# Define preprocessing functions
def preprocess_text(text):
    text = re.sub(r'(www\.\S+|http\S+)', '', text)
    text = re.sub(r'[^\w\s\']', '', text) 
    text = re.sub(r'\d+', '', text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"_+", '', text)
    text = re.sub(r'[\$€£₹]', '', text)
    return text

# Define removing stopwords function
def remove_stopwords(text):
    stopwords_list = stopwords.words('english')
    words = word_tokenize(text)
    output = [word for word in words if word not in stopwords_list]
    return ' '.join(output)


# Define routes
@app.route("/")
def home():
    session['logged_in'] = False
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == "warptec" and password == "warptec_2023":
            session["logged_in"] = True
            print(session) 
            return redirect(url_for('index'))
        else:
            return render_template("login.html", error="username or password is incorrect")

    return render_template('login.html')

@app.route("/index")
def index():
    print(session)
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    if request.method == 'POST':
        text = request.form.get('text')
        text = text.lower()
        preprocessed_text = preprocess_text(text)
        preprocessed_text = remove_stopwords(preprocessed_text)
        X = [preprocessed_text]
        sequences = tokenizer.texts_to_sequences(X)
        padded_data = pad_sequences(sequences, maxlen=300,padding="post",truncating="post")
        predicted_val = loaded_model.predict(padded_data)

        if predicted_val >= 0.5:
            prediction = "Beware! News is fake...!"
        else:
            prediction = "Great! News is real...!"       
        
        return render_template('index.html', prediction=prediction, news=text) 
        
    return render_template('index.html')

# Run the app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)