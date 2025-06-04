import re
import json
import math
import numpy as np
from hatemodel.services.model_code import score

# Load vectorizer data
with open("hatemodel/services/vectorizer_data.json", "r") as f:
    vec_data = json.load(f)
vocab = vec_data["vocab"]
idf = np.array(vec_data["idf"])

# stop_words = {
#     "i","me","my","we","our","you","your","he","she","it","they",
#     "them","this","that","is","are","was","were","a","an","the",
#     "and","but","or","if","in","on","for","to","with","as","at","by"
# }

stop_words = {
    "a", "an", "the", "and", "or", "but", "if", "while", "is", "am", "are", "was", "were", 
    "be", "been", "being", "have", "has", "had", "do", "does", "did", "so", "such", "too",
    "very", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", 
    "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when",
    "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", 
    "some", "no", "nor", "not", "only", "own", "same", "than", "can", "will", "just", "don", 
    "should", "now"
}

def clean(text):
    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"\@\w+|\#", "", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text

def preprocess(text):
    text = clean(text)
    tokens = [t for t in text.split() if t not in stop_words]
    return tokens

def vectorize(text_tokens):
    vec = np.zeros(len(vocab))
    for i, word in enumerate(vocab):
        count = text_tokens.count(word)
        if count > 0:
            vec[i] = count * idf[i]
    norm = np.linalg.norm(vec)
    return vec / norm if norm != 0 else vec

def predict(data):
    tokens = preprocess(data)
    input_vector = vectorize(tokens)
    result = score(input_vector.tolist())
    if isinstance(result, list):  # safety check
        result = result[0]
    return "Hate speech detected" if result > 0.5 else "No hate speech detected"