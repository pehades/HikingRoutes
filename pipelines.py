import re

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer


class CommonWordRemover:


    def run(self, descriptions: list[str]):

        # count word frequency
        cv = CountVectorizer(binary=True, lowercase=True, stop_words='english')
        X = cv.fit_transform(descriptions)

        df_ratio = np.asarray(X.sum(0)).ravel() / X.shape[0]
        terms = np.array(cv.get_feature_names_out())

        # 0.1 removes very common words (διοίκηση, Ελλάς, δήμος) in specific corpus.
        # lower than that may remove words like Άγγραφα which is a useful name for search
        stopwords = terms[df_ratio > 0.1].tolist()

        return [
            self.strip(description, stopwords) for description in descriptions
        ]

    @staticmethod
    def strip(text, stopwords):
        tokens = text.split(' ')
        return ' '.join(t for t in tokens if t.lower() not in stopwords)