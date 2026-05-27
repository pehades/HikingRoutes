import chromadb
import json

with open('trails.json', 'r') as f:
    trails = json.load(f)

trails = [trail for trail in trails if trail['name'] is not None]

client = chromadb.PersistentClient('./chroma_db')

client.delete_collection('trail_collection')
collection = client.get_or_create_collection('trail_collection')
collection.add(
    ids=[str(trail['id']) for trail in trails],
    documents=['|'.join(trail['names']) for trail in trails],
    metadatas=[trail['name'] for trail in trails]
)

results = collection.query(query_texts=['Parnitha'], n_results=5)