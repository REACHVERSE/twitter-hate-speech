import re
import emoji
import onnxruntime
import numpy as np
import torch
from transformers import AutoTokenizer

# Initialize ONNX runtime session and tokenizer
tokenizer = AutoTokenizer.from_pretrained('huawei-noah/TinyBERT_General_4L_312D')
ort_session = onnxruntime.InferenceSession("hatemodel/services/hate_speech_quantized.onnx")

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
    Make prediction using the ONNX model
    Returns: "Offensive speech detected", "Hate speech detected", or "Normal speech"
    """
    # Preprocess input text using the same function as training
    encoding = prepare_bert_input(text)
    
    # Run inference
    ort_inputs = {
        ort_session.get_inputs()[0].name: encoding['input_ids'],
        ort_session.get_inputs()[1].name: encoding['attention_mask']
    }
    logits = ort_session.run(None, ort_inputs)[0]
    
    # Get probabilities
    probabilities = torch.softmax(torch.tensor(logits), dim=1).numpy()[0]
    
    # Get the predicted class and its confidence
    predicted_class = np.argmax(probabilities)
    confidence = probabilities[predicted_class]
    
    # Return simplified result based on confidence threshold
    if confidence >= confidence_threshold:
        if predicted_class == 0:
            return "Normal speech"
        elif predicted_class == 1:
            return "Offensive speech detected"
        else: 
            return "Hate speech detected"
    else:
        # If confidence is below threshold, return the most likely non-normal class
        if probabilities[2] > probabilities[1]: 
            return "Possible hate speech detected (low confidence)"
        elif probabilities[1] > 0.4: 
            return "Possible offensive speech detected (low confidence)"
        else:
            return "Normal speech"

# Example usage
if __name__ == "__main__":
    test_texts = [
        "This is a normal tweet about sports.",
        "Some very offensive comments here! lol",
        "Women are weak and should not be leaders.",
        "This might be borderline offensive",
        "I kind of dislike those people"
    ]
    
    for text in test_texts:
        result = predict(text)
        print(f"\nText: {text}")
        print(f"Result: {result}")