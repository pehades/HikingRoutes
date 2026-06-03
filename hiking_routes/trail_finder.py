from lancedb import DBConnection

from hiking_routes.models import HikingDatabaseQuery
from pipelines import WordNormalizer


class TrailFinder:

    def __init__(self, db: DBConnection, word_normalizer: WordNormalizer):
        self.db = db
        self.word_normalizer = word_normalizer

    def find_trail(self, query: HikingDatabaseQuery):

        predicates = []
        if query.trail_length_min is not None:
            predicates.append(f'trail_length > {query.trail_length_min}')
        if query.trail_length_max is not None:
            predicates.append(f'trail_length < {query.trail_length_max}')

        name_predicates = []
        for possible_area in query.trail_possible_areas:
            name_predicates.append(f"description LIKE '%{self.word_normalizer.run(possible_area)}%'")
        predicates.append(
            f"({' OR '.join(name_predicates)})"
        )

        final_predicate = ' OR '.join(predicates)

        table = self.db.open_table(name='trails')
        return table.search(final_predicate).limit(10).to_list()

    # table.to_lance().scanner(filter=f'levenshtein(description, parnitha) <= 2')
