import json
import pandas as pd
import umap.umap_ as umap
from sentence_transformers import SentenceTransformer

def read_xls_file(file_path):
    try:
        data = pd.read_excel(file_path)
        return data
    except FileNotFoundError:
        print("File not found.")
        return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None
    
def create_embeddings(texts):
    # Load pre-trained model
    model = SentenceTransformer('all-mpnet-base-v2')
    
    # Generate embedding for the given text
    embedding = model.encode(texts)
    
    return embedding

def save_embeddings(data, embeddings, final_2d_embeddings, output_file):
    result = []
    for i in range(len(embeddings)):
        result.append({
            'id' :data['SUBJECT_ID'].iloc[i],
            'title': data['SUBJECT_TITLE'].iloc[i],
            # 'embedding': embeddings[i].tolist(),
            'x': float(final_2d_embeddings[i][0]),
            'y': float(final_2d_embeddings[i][1]),
        })
    
    with open(output_file, 'w') as file:
        json.dump(result, file)

def create_embedding_file(file_name):
    # Call read_xls_file given the file name as input
    data = read_xls_file(file_name)
    
    # Check if data is not None
    if data is not None:
        # Create texts from attribute subject_title and subject_description
        texts = ['Title: ' + str(title) + '. Description: ' + str(description) for title, description in zip(data['SUBJECT_TITLE'], data['SUBJECT_DESCRIPTION'])]
        
        # Create embeddings for the texts
        embeddings = create_embeddings(texts)
        
        # Create 2d embeddings
        umap_reducer = umap.UMAP(n_components=2, random_state=42)
        final_2d_embeddings = umap_reducer.fit_transform(embeddings)
        
        save_embeddings(data, embeddings, final_2d_embeddings, 'embeddings.json')
                
        print("Embeddings file created successfully.")
    else:
        print("Failed to create embeddings file.")

create_embedding_file("MIT-Catalog-2025-SDM V2.xlsx")

