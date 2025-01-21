from flask import Flask, request, render_template, redirect, url_for
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import docx

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Load stopwords
stopwords_set = set(stopwords.words('english'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = re.sub(r'[^a-zA-Z]', ' ', text)  # Remove punctuation and special characters
    text = nltk.word_tokenize(text)  # Tokenize the text
    text = [word for word in text if word not in stopwords_set and len(word) > 3]  # Remove stop words and short words
    stemming = PorterStemmer()
    text = [stemming.stem(word) for word in text]  # Stem the words
    text = list(set(text))  # Keep unique words
    return " ".join(text)

# def get_keywords(idx, docs, topN):
#     print(topN)
#     cv = CountVectorizer(max_df=0.95, max_features=5000, ngram_range=(1, 1))
#     word_count_vector = cv.fit_transform(docs)
#     tf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
#     tf_transformer = tf_transformer.fit(word_count_vector)
#     feature_names = cv.get_feature_names_out()
#     docs_word_count = tf_transformer.transform(cv.transform([docs[idx]]))
#     docs_word_count = docs_word_count.tocoo()

#     tuples = zip(docs_word_count.col, docs_word_count.data)
#     sorted_all_items = sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)

#     sorted_items = []
#     for i in range(len(sorted_all_items)):
#         sorted_items.append(sorted_all_items[i])
#         if i == topN - 1:
#             break

#     score_vals = []
#     feature_vals = []
#     for idx, score in sorted_items:
#         score_vals.append(round(score, 3))
#         feature_vals.append(feature_names[idx])

#     result = {}
#     for idx in range(len(feature_vals)):
#         result[feature_vals[idx]] = score_vals[idx]

#     return result

def get_keywords(idx, docs, topN):
    # Fit CountVectorizer on the entire corpus
    cv = CountVectorizer(max_df=0.95, max_features=5000, ngram_range=(1, 1))
    word_count_vector = cv.fit_transform(docs)
    
    # Fit TF-IDF transformer on the word count vector of the entire corpus
    tf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tf_transformer = tf_transformer.fit(word_count_vector)
    
    # Extract feature names (i.e., words)
    feature_names = cv.get_feature_names_out()
    
    # Transform only the specified document (docs[idx])
    single_doc_vector = tf_transformer.transform(cv.transform([docs[idx]]))
    
    # Convert to a sparse matrix representation
    single_doc_vector = single_doc_vector.tocoo()
    
    # Get non-zero TF-IDF values and corresponding words
    tuples = zip(single_doc_vector.col, single_doc_vector.data)
    
    # Sort tuples based on TF-IDF score (highest to lowest)
    sorted_items = sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)
    
    # Select the top N items based on sorted scores
    top_keywords = sorted_items[:topN]
    
    # Prepare the result as a dictionary {word: score}
    result = {}
    for idx, score in top_keywords:
        result[feature_names[idx]] = round(score, 3)
    
    return result

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_text():
    text = request.form.get('text')

    file = request.files.get('file')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract text based on file type
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file_path)

    if not text:
        return redirect(url_for('index'))

    # Get the number of keywords from the form
    num_keywords = request.form.get('keyword_count', 10)  # Default to 10 if not provided
    try:
        num_keywords = int(num_keywords)
    except ValueError:
        num_keywords = 10  # Fallback to 10 if conversion fails

    # Split text into smaller documents
    text_list = text.split(' ')
    n = len(text_list)
    docs = []
    for i in range(0, n, 20):
        docs.append(preprocess_text(' '.join(text_list[i:i+20])))

    # Get keywords for the first document as an example
    idx = 0
    keywords = get_keywords(idx, docs, num_keywords)

    return render_template('keywords.html', keywords=keywords.keys())


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
