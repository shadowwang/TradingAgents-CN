# 安装依赖
# pip install transformers torch scikit-learn
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class EmotionAnalyzer:
    def __init__(self, model_path="uer/roberta-base-finetuned-dianping-chinese"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.labels = ["negative", "positive"]  # 这个模型只支持二分类：负面和正面

    def analyze(self, text: str) -> dict:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            logits = self.model(**inputs).logits

        probabilities = torch.softmax(logits, dim=1)[0]
        predicted_class = torch.argmax(probabilities).item()

        return {
            "emotion": self.labels[predicted_class],
            "confidence": probabilities[predicted_class].item(),
            "probabilities": {label: prob.item() for label, prob in zip(self.labels, probabilities)}
        }