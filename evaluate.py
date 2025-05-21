
import pandas as pd
from modules.keyword_extraction import extract_keywords, preprocess_text
from modules.evaluation import evaluate_keywords

# Load dataset (Hugging Face direct read)
df = pd.read_csv("https://huggingface.co/datasets/zino36/Tags-Generation-dataset/resolve/main/keyword-extraction-dataset.csv")

df.to_csv("./dataset/Dataset_Original.csv", index=False)

# Clean and process gold keywords
df['GoldKeywords'] = df['Keywords'].apply(
    lambda x: [preprocess_text(word.lower()) for phrase in x.split(',') for word in phrase.strip().split()]
)

df.to_csv(r"./dataset/Dataset_Keywords_Updated.csv", index=False)

def safe_extract_keywords(text, top_n=10):
    cleaned_sentences = [preprocess_text(sent) for sent in text.split('.') if sent.strip()]
    try:
        return extract_keywords(cleaned_sentences, topN=top_n)
    except Exception as e:
        print(f"Error in extract_keywords: {e}")
        return []

# Apply safely
df['PredictedKeywords'] = df.apply(
    lambda row: safe_extract_keywords(row['Articles'], top_n=int(0.5*len(row['GoldKeywords']))),
    axis=1
)

df.to_csv(r"./dataset/Dataset_with_Predictions.csv", index=False)

# Evaluate per row
evaluations = df.apply(lambda row: evaluate_keywords(row['PredictedKeywords'].keys(), row['GoldKeywords']), axis=1)

# Convert evaluation results to DataFrame
eval_df = pd.DataFrame(evaluations.tolist())

# Calculate mean metrics
metrics = {
    'precision': eval_df['precision'].mean(),
    'recall': eval_df['recall'].mean(),
    'f1_score': eval_df['f1_score'].mean()
}

print("Average Evaluation Metrics:")
print(f"Precision: {metrics['precision']:.4f}")
print(f"Recall:    {metrics['recall']:.4f}")
print(f"F1 Score:  {metrics['f1_score']:.4f}")

eval_df.to_csv(r"./dataset/Evaluation_Results.csv", index=False)