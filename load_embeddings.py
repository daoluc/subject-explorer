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
    types = []
    x = []
    y = []
    for item in data:
        ids.append(item['id'])
        titles.append(item['title'])
        x.append(item['x'])
        y.append(item['y'])
        if (item['core']):
            types.append('Core')
        elif (item['depth']):
            if(item['eng']):
                if(item['mgmt']):
                    types.append('Eng & Mgmt Depth')
                else:
                    types.append('Eng Depth')
            else:
                types.append('Mgmt Depth')
        elif (item['elective']):
            if(item['eng']):
                if(item['mgmt']):
                    types.append('Eng & Mgmt Elective')
                else:
                    types.append('Eng Elective')
            else:
                types.append('Mgmt Elective')
        else:
            types.append('Other')
    
    return pd.DataFrame.from_dict(data=dict(
        x=x,
        y=y,        
        id=ids,
        title=titles,
        type=types
    ))