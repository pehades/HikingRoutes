import os

import json

import numpy as np
import pyarrow as pa
from sentence_transformers import SentenceTransformer
import lancedb

from hiking_routes import ROOT_DIR

from pipelines import CommonWordRemover, WordNormalizer

with open('trails.json', 'r') as f:
    trails = json.load(f)

trails = [trail for trail in trails if trail['name'] is not None]

trails_description = [trail['description'] for trail in trails]

trails_description = CommonWordRemover().run(trails_description)
word_normalizer = WordNormalizer()
embedding = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')


for trail, trail_description in zip(trails, trails_description):
    descriptions = [word_normalizer.run(word) for word in trail_description.split(' ')]
    trail_description = ' '.join(descriptions)
    trail['description'] = trail_description
    trail['vector'] = embedding.encode(descriptions).tolist()

db = lancedb.connect(os.path.join(ROOT_DIR, 'lance_db'))

if 'trails' in db.list_tables().tables:
    db.drop_table('trails')



coord = pa.struct([("lon", pa.float64()), ("lat", pa.float64())])

schema = pa.schema([
    pa.field("id", pa.int64()),
    pa.field("name", pa.string()),
    pa.field("start_point", coord),
    pa.field("end_point", coord),
    pa.field("coordinates", pa.list_(coord)),
    pa.field("length", pa.float64()),
    pa.field("elevation_profile", pa.list_(pa.int64())),
    pa.field("ascend", pa.int64()),
    pa.field("descend", pa.int64()),
    pa.field("description", pa.string()),
    pa.field("vector", pa.list_(pa.list_(pa.float32(), 384))),
])

tbl = db.create_table("trails", data=trails, schema=schema)
tbl.create_index(metric="cosine", vector_column_name='vector')

# table = db.create_table('trails', schema=TrailDb)
# table.create_index(metric='cosine')
# table.add(trails)

