from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from modules.keyword_extraction import extract_keywords, preprocess_text, get_synonyms
from modules.file_processing import extract_text_from_pdf, extract_text_from_docx
from modules.clustering import DocumentClustering
from modules.utils import allowed_file, find_related_files
import os
import traceback
import logging

logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

file_keywords = {}  # Global dictionary for storing extracted keywords

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_text():
    global file_keywords  # Use the global dictionary
    
    text = request.form.get('text')  # Get the single text input
    files = request.files.getlist('files')  # Get uploaded files
    num_keywords = int(request.form.get('keyword_count', 10))

    all_keywords = {}  # Store keywords for both files and text

    # Process manually entered text
    if text and text.strip():  # Ensure text is not empty
        filename = "text_input"  # Use a fixed name for text input

        # Preprocess and extract keywords
        text_list = text.split('.')  # Split into sentences
        docs = [preprocess_text(sentence) for sentence in text_list if sentence]
        keywords = extract_keywords(docs, num_keywords)

        all_keywords[filename] = list(keywords.keys())  # Store keywords

    # Process uploaded files
    for file in files:
        if file and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Extract text based on file type
            if filename.endswith('.pdf'):
                file_text = extract_text_from_pdf(file_path)
            elif filename.endswith('.docx'):
                file_text = extract_text_from_docx(file_path)
            else:
                file_text = ""
            if file_text:
                text_list = file_text.split('.')
                docs = [preprocess_text(sentence) for sentence in text_list if sentence]
                keywords = extract_keywords(docs, num_keywords)

                all_keywords[filename] = list(keywords.keys())  # Store keywords
            # 🗑️ Delete file after parsing
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass

    # Store all extracted keywords
    file_keywords.update(all_keywords)

    # Find related files
    related_files = find_related_files(file_keywords)  # Pass file_keywords to the function

    return render_template('keywords.html', keywords=all_keywords, related_files=related_files)

@app.route('/clusters')
def cluster_documents():
    if not file_keywords:
        return "No documents available for clustering."

    clustering_model = DocumentClustering(num_clusters=3)
    if 'text_input'in file_keywords:
        del file_keywords['text_input']
    file_names = list(file_keywords.keys())
    document_texts = [" ".join(file_keywords[file]) for file in file_names]

    clusters = clustering_model.get_clusters(file_names, document_texts)
    return render_template('clusters.html', clusters=clusters)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    if not query:
        return render_template('search.html', results={})
    query = query.lower()
    query_synonyms = get_synonyms(query)
    search_terms = {query} | query_synonyms  # Combine query + synonyms
    matching_files = {
        file: keywords
        for file, keywords in file_keywords.items()
        if any(term in keywords for term in search_terms)
    }
    return render_template('search.html', results=matching_files)

@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", message="Page not found!"), 404

@app.errorhandler(500)
def internal_error(error):
    # Log traceback for internal server errors too
    traceback.print_exc()
    return render_template("error.html", message="Internal server error! Please try again."), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Print full traceback in console
    traceback.print_exc()
    return render_template("error.html", message=str(e)), 500

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)