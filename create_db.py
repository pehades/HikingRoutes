import os

import lancedb
import json

from hiking_routes import ROOT_DIR
from hiking_routes.models import TrailDb
from pipelines import CommonWordRemover, WordNormalizer

with open('trails.json', 'r') as f:
    trails = json.load(f)

trails = [trail for trail in trails if trail['name'] is not None]

trails_description = [trail['description'] for trail in trails]

trails_description = CommonWordRemover().run(trails_description)
word_normalizer = WordNormalizer()

for trail, trail_description in zip(trails, trails_description):
    trail_description = ' '.join([word_normalizer.run(word) for word in trail_description.split(' ')])
    trail['description'] = trail_description

db = lancedb.connect(os.path.join(ROOT_DIR, 'hiking_routes/lance_db'))

if 'trails' in db.list_tables():
    db.drop_table('trails')

table = db.create_table('trails', schema=TrailDb)
table.add(trails)

