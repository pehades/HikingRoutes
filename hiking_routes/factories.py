import os

import lancedb

from hiking_routes import ROOT_DIR
from hiking_routes.trail_finder import TrailFinder
from pipelines import WordNormalizer


class Factory:

    @classmethod
    def get_local_trail_finder(cls) -> TrailFinder:
        return TrailFinder(
            db=lancedb.connect(os.path.join(ROOT_DIR, 'lance_db')),
            word_normalizer=WordNormalizer()
        )