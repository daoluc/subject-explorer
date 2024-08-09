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
            't': data['SUBJECT_TITLE'].iloc[i],
            'd': data['SUBJECT_DESCRIPTION'].iloc[i],                         
            'core': 1 if data['SUBJECT_ID'].iloc[i] in ('EM.411', 'EM.412', 'EM.413') else 0,                        
            'depth': 1 if data['isDepth'].iloc[i] == 'Y' else 0,
            'elect': 1 if data['isElective'].iloc[i] == 'Y' else 0,
            'eng': 1 if (data['engUnits'].iloc[i] is not None and pd.notna(data['engUnits'].iloc[i]) and data['engUnits'].iloc[i] > 0) else 0,
            'mgmt': 1 if (data['mgmtUnits'].iloc[i] is not None and pd.notna(data['mgmtUnits'].iloc[i]) and data['mgmtUnits'].iloc[i] > 0) else 0,
            'c': int(data['SDMCount'].iloc[i]),
            'x': round(float(final_2d_embeddings[i][0]), 4),
            'y': round(float(final_2d_embeddings[i][1]), 4),
            'e': embeddings[i].tolist(),
        })
    
    with open(output_file, 'w') as file:
        json.dump(result, file)

def create_embedding_file(file_name):
    # Call read_xls_file given the file name as input
    data = read_xls_file(file_name)
    
    # Check if data is not None
    if data is not None:
        # Create a priority column based on isDepth, isElective, engUnits, and mgmtUnits
        data['priority'] = (
            (data['isDepth'] == 'Y').astype(int) * 8 +
            (data['isElective'] == 'Y').astype(int) * 4 +
            (data['engUnits'].notna() & (data['engUnits'] > 0)).astype(int) +
            (data['mgmtUnits'].notna() & (data['mgmtUnits'] > 0)).astype(int) +
            (data['SDMCount'].notna() & (data['SDMCount'] > 0)).astype(int)
        )
        
        # Sort by priority (descending) and remove duplicates based on SUBJECT_TITLE
        data = data.sort_values('priority', ascending=False)
        data = data.drop_duplicates(subset='SUBJECT_TITLE', keep='first')
        
        # Drop the temporary priority column
        data = data.drop('priority', axis=1)
        
        # Create texts from attribute subject_title and subject_description
        texts = ['Title: ' + str(title) + '. Description: ' + str(description) for title, description in zip(data['SUBJECT_TITLE'], data['SUBJECT_DESCRIPTION'])]
        
        # Create embeddings for the texts
        embeddings = create_embeddings(texts)
        
        # Create 2d embeddings
        umap_reducer = umap.UMAP(n_components=2, random_state=42)
        final_2d_embeddings = umap_reducer.fit_transform(embeddings)
        
        save_embeddings(data, embeddings, final_2d_embeddings, 'full_embeddings.json')
                
        print("Embeddings file created successfully.")
    else:
        print("Failed to create embeddings file.")



# create_embedding_file("MIT-Catalog-2025-SDM V2.xlsx")

