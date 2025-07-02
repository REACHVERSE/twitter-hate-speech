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

def predict(text):
    """Make prediction using the ONNX model"""
    # Preprocess input text using the same function as training
    encoding = prepare_bert_input(text)
    
    # Run inference
    ort_inputs = {
        ort_session.get_inputs()[0].name: encoding['input_ids'],
        ort_session.get_inputs()[1].name: encoding['attention_mask']
    }
    logits = ort_session.run(None, ort_inputs)[0]
    
    # Get probabilities and prediction
    probabilities = torch.softmax(torch.tensor(logits), dim=1).numpy()[0]
    prediction = np.argmax(probabilities)
    
    # Return human-readable results
    label_map = {
        0: {'label': 'Normal', 'prob': probabilities[0]},
        1: {'label': 'Offensive', 'prob': probabilities[1]}, 
        2: {'label': 'Hate', 'prob': probabilities[2]}
    }
    
    return {
        'prediction': label_map[prediction]['label'],
        'confidence': float(label_map[prediction]['prob']),
        'details': label_map
    }

# Example usage
if __name__ == "__main__":
    test_texts = [
        "This is a normal tweet about sports.",
        "Some very offensive comments here! lol",
        "Women are weak and should not be leaders."
    ]
    
    for text in test_texts:
        result = predict(text)
        print(f"\nText: {text}")
        print(f"Prediction: {result['prediction']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print("Details:")
        for label, info in result['details'].items():
            print(f"  {info['label']}: {info['prob']:.4f}")