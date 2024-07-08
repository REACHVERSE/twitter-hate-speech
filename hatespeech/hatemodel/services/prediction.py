import pickle
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import pandas as pd
import os
project_root = os.getenv('PROJECT_ROOT')

stop_words = set(stopwords.words('english'))
import re

#model = pickle.load(open('/workspaces/codespaces-blank/hatespeech/hatemodel/services/savedmodel.pkl', 'rb'))
model = pickle.load(open(os.path.join(project_root, 'hatespeech','hatemodel','services','savedmodel.pkl'),'rb'))

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
#vect = pickle.load(open('/workspaces/codespaces-blank/hatespeech/hatemodel/services/vectoriser.pkl', 'rb'))
vect = pickle.load(open(os.path.join(project_root, 'hatespeech','hatemodel','services','vectorizer.pkl'),'rb'))


def predict(data):
    #defining a function to clean text
    #print(data)
    data = lemmatizing(clean(data))
    input_data = vect.transform(data.split(" "))
    prediction = model.predict(input_data)

    if 1 in prediction:
        output = "Hate speech detected"

    else:
         output = "No hate speech detected"
    #print(type(prediction))
    print(output)
    return output
    

