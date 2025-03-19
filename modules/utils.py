from collections import defaultdict

def allowed_file(filename, allowed_extensions):
    """Check if file has a valid extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def find_related_files(file_keywords):
    related_files = defaultdict(set)
    for file1, keywords1 in file_keywords.items():
        for file2, keywords2 in file_keywords.items():
            if file1 != file2 and len(set(keywords1) & set(keywords2))>1:
                related_files[file1].add(file2)
    return related_files
