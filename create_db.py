import chromadb
import json

from chromadb.utils import embedding_functions

from pipelines import CommonWordRemover

with open('trails.json', 'r') as f:
    trails = json.load(f)

trails = [trail for trail in trails if trail['name'] is not None]

trails_description = [' '.join(trail['description']) for trail in trails]

trails_description = CommonWordRemover().run(trails_description)
for trail, trail_description in zip(trails, trails_description):
    trail['description'] = trail_description

client = chromadb.PersistentClient('./chroma_db')

# client.delete_collection('trail_collection')


ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="intfloat/multilingual-e5-base"  # or any of the above
)

collection = client.get_or_create_collection('trail_collection', embedding_function=ef)

# collection.add(
#     ids=[str(trail['id']) for trail in trails],
#     documents=[f"{trail['description']} {trail['name']}" for trail in trails],
#     metadatas=[{'name': trail['name']} for trail in trails]
# )
# print([trail['description'] for trail in trails if 'Πάρνηθα'.lower() in trail['description'].lower()])
results = collection.query(query_texts=['query: Πάρνηθα'], n_results=15)
print(results)