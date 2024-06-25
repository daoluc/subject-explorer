import pandas as pd
import umap.umap_ as umap
import json


# Function to read the JSON file
def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        return json.loads(content)
    
def get_2d_embeddings_from_file(file_name):
            
    data = read_json(file_name)
    ids = []
    titles = []
    x = []
    y = []
    for item in data:
        ids.append(item['id'])
        titles.append(item['title'])
        x.append(item['x'])
        y.append(item['y'])
    
    return ids, titles, x, y