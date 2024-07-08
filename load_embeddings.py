import streamlit as st
import numpy as np
import pandas as pd
import umap.umap_ as umap
import json


# Function to read the JSON file
@st.cache_data
def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        return json.loads(content)

@st.cache_data   
def get_raw_embeddings_from_file(file_name):
    raw_data = read_json(file_name)
    ids = []
    embeddings = []
    titles = {}
    descriptions = {}
    x = {}
    y = {}
    title_check = []
    for item in raw_data:
        if (item['t'] in title_check):
            continue
        else:
            title_check.append(item['t'])
        ids.append(item['id'])
        embeddings.append(item['e'])
        titles[item['id'].upper()] = item['t']
        descriptions[item['id'].upper()] = item['d']
        x[item['id'].upper()] = item['x']
        y[item['id'].upper()] = item['y']
    return ids, embeddings, titles, descriptions, x, y

@st.cache_data   
def get_2d_embeddings_from_file(file_name):            
    raw_data = read_json(file_name)
    ids = []
    titles = []
    types = []
    x = []
    y = []
    for item in raw_data:
        ids.append(item['id'])
        titles.append(item['t'])
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
        elif (item['elect']):
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