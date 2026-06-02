import lancedb
import json

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

db = lancedb.connect('./lance_db')

if 'trails' in db.table_names():
    db.drop_table('trails')

table = db.create_table('trails', schema=TrailDb)
table.add(trails)

