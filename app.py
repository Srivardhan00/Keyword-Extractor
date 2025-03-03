from flask import Flask, request, render_template, redirect, url_for, jsonify
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import docx
from nltk.stem import WordNetLemmatizer
from collections import defaultdict

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Load stopwords
stopwords_set = set(stopwords.words('english'))

# Global dictionary to store extracted keywords for each file
file_keywords = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'<.*?>', '', text)  # Remove HTML tags
    text = re.sub(r'[^a-zA-Z]', ' ', text)  # Remove punctuation and special characters
    text = nltk.word_tokenize(text)  # Tokenize the text
    text = [word for word in text if word not in stopwords_set and len(word) > 3]  # Remove stop words and short words
    lemmatizer = WordNetLemmatizer()
    text = [lemmatizer.lemmatize(word) for word in text]
    return " ".join(text)

def get_keywords(docs, topN):
    combined_text = " ".join(docs)
    cv = CountVectorizer(max_df=1, min_df=0.2, max_features=5000, ngram_range=(1, 1))
    word_count_vector = cv.fit_transform([combined_text])
    
    tf_transformer = TfidfTransformer(smooth_idf=True, use_idf=True)
    tf_transformer = tf_transformer.fit(word_count_vector)
    
    tf_idf_vector = tf_transformer.transform(word_count_vector)
    feature_names = cv.get_feature_names_out()    

    tf_idf_vector = tf_idf_vector.tocoo()  # Sparse COO format
        
    word_scores = [(feature_names[idx], score) for idx, score in zip(tf_idf_vector.col, tf_idf_vector.data)]
    sorted_items = sorted(word_scores, key=lambda x: x[1], reverse=True)

    result = {}
    for i in range(min(topN, len(sorted_items))):
        word, score = sorted_items[i]
        result[word] = round(score, 3)

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
    full_text = [para.text for para in doc.paragraphs]
    return '\n'.join(full_text)

def find_related_files():
    """Find related files based on keyword similarity."""
    related_files = defaultdict(set)

    # Compare keywords between files
    for file1, keywords1 in file_keywords.items():
        for file2, keywords2 in file_keywords.items():
            if file1 != file2:
                common_keywords = set(keywords1) & set(keywords2)
                if common_keywords:
                    related_files[file1].add(file2)

    return related_files

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_text():
    print("Received Request")
    
    text = request.form.get('text')
    files = request.files.getlist('files')  # Get multiple files

    all_keywords = {}  # Store keywords from all files

    # Process uploaded files
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Extract text from files
            if filename.endswith('.pdf'):
                file_text = extract_text_from_pdf(file_path)
            elif filename.endswith('.docx'):
                file_text = extract_text_from_docx(file_path)
            else:
                file_text = ""

            if file_text:
                text += " " + file_text  # Append file text to input text

            # Process each file separately
            text_list = file_text.split('.')
            docs = [preprocess_text(sentence) for sentence in text_list if sentence]

            # Extract keywords for this file
            num_keywords = int(request.form.get('keyword_count', 10))
            keywords = get_keywords(docs, num_keywords)

            all_keywords[filename] = list(keywords.keys())  # Store keywords

    # If no text is available, redirect
    if not text.strip():
        return redirect(url_for('index'))

    # Store keywords globally
    global file_keywords
    file_keywords.update(all_keywords)

    # Find related files
    related_files = find_related_files()

    return render_template('keywords.html', keywords=all_keywords, related_files=related_files)

@app.route('/search', methods=['GET'])
def search():
    """Search for files based on user-inputted keywords."""
    query = request.args.get('q', '').lower()
    if not query:
        return render_template('search.html', results={})

    matching_files = {file: keywords for file, keywords in file_keywords.items() if query in keywords}
    return render_template('search.html', results=matching_files)

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
