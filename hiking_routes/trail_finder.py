from lancedb import DBConnection
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

from hiking_routes.models import HikingDatabaseQuery, Trail
from pipelines import WordNormalizer


class TrailFinder:

    def __init__(self, db: DBConnection, word_normalizer: WordNormalizer) -> list[Trail]:
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

        return [Trail.model_validate(result) for result in q.limit(10).to_list()]

