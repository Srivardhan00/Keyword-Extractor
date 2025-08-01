import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from nltk.corpus import wordnet as wn

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

stopwords_set = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
stopwords_set.add("nbsp")
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    words = nltk.word_tokenize(text)
    words = [lemmatizer.lemmatize(word) for word in words if word not in stopwords_set and len(word) > 3]
    return " ".join(words)

def extract_keywords(docs, topN=10):
    try:
        combined_text = " ".join(docs)
        vectorizer = CountVectorizer(max_df=1, min_df=0.2, max_features=5000, 
                                    # ngram_range=(1, 2), 
                                    stop_words='english')
        word_count_vector = vectorizer.fit_transform([combined_text])

        tfidf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
        tfidf_vector = tfidf_transformer.fit_transform(word_count_vector).tocoo()

        feature_names = vectorizer.get_feature_names_out()
        word_scores = [(feature_names[idx], score) for idx, score in zip(tfidf_vector.col, tfidf_vector.data)]
        sorted_items = sorted(word_scores, key=lambda x: x[1], reverse=True)

        return {word: round(score, 3) for word, score in sorted_items[:topN]}
    except Exception as e:
        print(f"Error in extract_keywords: {e}")
        return {["NO KEYWORDS FOUND"]}

def get_synonyms(word):
  synonyms = set()
  for syn in wn.synsets(word):
      for lemma in syn.lemmas():
          name = lemma.name().replace("_", " ").lower()
          if name != word.lower():
              synonyms.add(name)
  return synonyms