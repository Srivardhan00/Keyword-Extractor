from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class DocumentClustering:
    def __init__(self, num_clusters=3):
        self.num_clusters = num_clusters
        self.vectorizer = TfidfVectorizer()
        self.model = KMeans(n_clusters=self.num_clusters, random_state=42)

    def fit(self, documents):
        """Fits the clustering model on the given documents"""
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        self.model.fit(tfidf_matrix)
        return self.model.labels_

    def get_clusters(self, file_names, documents):
        """Groups files into clusters and returns a dictionary {cluster_id: [file_names]}"""
        labels = self.fit(documents)
        clusters = {}

        for idx, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(file_names[idx])
        
        return clusters
