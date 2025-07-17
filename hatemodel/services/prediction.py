import re
import emoji
import onnxruntime
import numpy as np
import torch
from transformers import AutoTokenizer
import pickle

tokenizer = None
ort_session = None
model_accuracy = None

def initialize_model():
    """
    Loads the tokenizer, ONNX session, and accuracy value into global variables.
    This function is called once when the application starts.
    """
    global tokenizer, ort_session, model_accuracy
    
    tokenizer = AutoTokenizer.from_pretrained('huawei-noah/TinyBERT_General_4L_312D')
    ort_session = onnxruntime.InferenceSession("hatemodel/services/hate_speech_quantized.onnx")
    model_accuracy = pickle.load(open("hatemodel/services/accuracy.pkl", "rb"))

def preprocess_tweet(text):
    """The exact same cleaning function used during training"""
    text = emoji.demojize(text, delimiters=(" ", " "))
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#(\w+)', r'\1', text)
    text = re.sub(r"won't", "will not", text)
    text = re.sub(r"can't", "cannot", text)
    text = re.sub(r"n't", " not", text)
    text = re.sub(r"'re", " are", text)
    text = re.sub(r"'s", " is", text)
    text = re.sub(r"'d", " would", text)
    text = re.sub(r"'ll", " will", text)
    text = re.sub(r"'ve", " have", text)
    text = re.sub(r"'m", " am", text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

def prepare_bert_input(text, max_length=128):
    """Tokenize and prepare input for BERT model"""
    if tokenizer is None:
        raise RuntimeError("Model is not initialized. Please call initialize_model() first.")
    text = preprocess_tweet(text)
    encoding = tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=max_length,
        return_token_type_ids=False,
        padding='max_length',
        truncation=True,
        return_attention_mask=True,
        return_tensors='np'
    )
    return encoding

def predict(text, confidence_threshold=0.7):
    """
    Make prediction using the ONNX model.
    Returns a tuple: (prediction_label, confidence_score)
    """
    if ort_session is None:
        raise RuntimeError("Model is not initialized. Please call initialize_model() first.")
        
    encoding = prepare_bert_input(text)
    
    ort_inputs = {
        ort_session.get_inputs()[0].name: encoding['input_ids'],
        ort_session.get_inputs()[1].name: encoding['attention_mask']
    }
    logits = ort_session.run(None, ort_inputs)[0]
    
    probabilities = torch.softmax(torch.tensor(logits), dim=1).numpy()[0]
    
    predicted_class = np.argmax(probabilities)
    confidence = probabilities[predicted_class]
    
    # Format the confidence score as a percentage rounded to two decimal places
    confidence_score = round(confidence * 100, 2)
    
    if confidence >= confidence_threshold:
        if predicted_class == 0:
            return "Normal speech", confidence_score
        elif predicted_class == 1:
            return "Offensive speech detected", confidence_score
        else: 
            return "Hate speech detected", confidence_score
    else:
        # For low confidence, determine the most likely non-normal class
        if probabilities[2] > probabilities[1]: # Leaning towards Hate Speech
            low_confidence_score = round(probabilities[2] * 100, 2)
            return "Possible hate speech detected (low confidence)", low_confidence_score
        elif probabilities[1] > 0.4: # Leaning towards Offensive Speech
            low_confidence_score = round(probabilities[1] * 100, 2)
            return "Possible offensive speech detected (low confidence)", low_confidence_score
        else: # Default to Normal Speech
            normal_confidence_score = round(probabilities[0] * 100, 2)
            return "Normal speech", normal_confidence_score
        