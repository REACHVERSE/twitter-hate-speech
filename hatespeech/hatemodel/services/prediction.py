import pandas as pd
from rest_framework import status
import pickle
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))
import re


model = pickle.load(open("/workspaces/codespaces-blank/ml_model.pkl", 'rb'))

def clean(text):
        text = str(text).lower()
        text = re.sub(r"https?://\S+|www\.\S+", "", text, flags = re.MULTILINE)
        test = re.sub(r"\@w+|\#", "", text)
        text = re.sub(r"[^\w\s]", "", text)
        tweet_tokens = word_tokenize(text)
        text = [word for word in text.split(" ") if word not in stop_words]
        text = " ".join(text)
        return text

    #initialising lemmatiser
lemmatizer = WordNetLemmatizer()
#defining lemmatizing function
def lemmatizing(data):
    tweet = [lemmatizer.lemmatize(w) for w in data]
    return data

#declaring the saved vectorizer
vect = pickle.load(open("/workspaces/codespaces-blank/vectorizer.pkl", "rb"))


def predict(data):
    #defining a function to clean text
    print(data)
    data = lemmatizing(clean(data))
    input_data = vect.transform(data.split(" "))
    prediction = model.predict(input_data)
    print(prediction)

#predict("You're a stupid bitch!!")