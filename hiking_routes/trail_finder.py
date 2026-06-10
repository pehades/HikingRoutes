from lancedb import DBConnection
from sentence_transformers import SentenceTransformer

from hiking_routes.models import HikingDatabaseQuery
from pipelines import WordNormalizer


class TrailFinder:

    def __init__(self, db: DBConnection, word_normalizer: WordNormalizer):
        self.db = db
        self.word_normalizer = word_normalizer
        self.embedding = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def find_trail(self, user_query: HikingDatabaseQuery):

        table = self.db.open_table(name='trails')
        embedding = self.embedding.encode(user_query.trail_possible_areas)

        q = table.search(query=embedding)

        # filter if given more constraints
        if user_query.trail_length_min is not None:
            q = q.where(f'length > {user_query.trail_length_min}')
        if user_query.trail_length_max is not None:
            q = q.where(f'length < {user_query.trail_length_max}')

        return q.limit(10).to_list()

