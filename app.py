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
    return " ".join(text)

def get_keywords(docs, topN):
    combined_text = " ".join(docs)
    # Fit CountVectorizer on the entire corpus
    cv = CountVectorizer(max_df=1, min_df=0.2, max_features=5000, ngram_range=(1, 1))
    word_count_vector = cv.fit_transform([combined_text])
    
    # Fit TF-IDF transformer on the word count vector of the entire corpus
    tf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tf_transformer = tf_transformer.fit(word_count_vector)
    
    # Extract feature names (i.e., words)
    tf_idf_vector = tf_transformer.transform(word_count_vector)
    feature_names = cv.get_feature_names_out()    

    tf_idf_vector = tf_idf_vector.tocoo()  # Sparse COO format
        
    
    # Sort tuples based on TF-IDF score (highest to lowest)
    word_scores = [(feature_names[idx], score) for idx, score in zip(tf_idf_vector.col, tf_idf_vector.data)]
    sorted_items = sorted(word_scores, key=lambda x: x[1], reverse=True)

    
    # Prepare the result as a dictionary {word: score}
    result = {}
    for i in range(topN):
        word, score = sorted_items[i]
        result[word] = round(score, 3)  # Round to 3 decimal places

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
    text_list = text.split('.')
    n = len(text_list)
    docs=[]
    for i in range(n):
        curr_text = preprocess_text(text_list[i])
        if curr_text:
            docs.append(curr_text)

    # Get keywords for the first document as an example
    keywords = get_keywords(docs, num_keywords)

    return render_template('keywords.html', keywords=keywords.keys())


if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
