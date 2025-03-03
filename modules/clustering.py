from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


class DocumentClustering:
    def __init__(self, num_clusters=3):
        self.num_clusters = num_clusters

    def get_clusters(self, file_names, documents):
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(documents)

        model = KMeans(n_clusters=self.num_clusters, random_state=42)
        model.fit(X)

        clusters = {i: [] for i in range(self.num_clusters)}
        for i, label in enumerate(model.labels_):
            clusters[label].append(file_names[i])

        return clusters
