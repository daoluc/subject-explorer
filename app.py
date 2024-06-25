import streamlit as st
import pandas as pd
from bokeh.plotting import ColumnDataSource, figure
from load_embeddings import get_2d_embeddings_from_file

st.title('MIT Subject Explorer')

TOOLTIPS = """
<div style="width:300px;">
@id @title <br> <br>
</div>
"""

ids, titles, x, y = get_2d_embeddings_from_file('embeddings.json')

source = ColumnDataSource(data=dict(
    x=x,
    y=y,
    title=titles,
    id=ids,
))

p = figure(width=700, height=583, tooltips=TOOLTIPS, x_range=(0, 15), y_range=(2.5,15),
           title="UMAP projection of embeddings for MIT subjects")

p.circle('x', 'y', size=3, source=source, alpha=0.3)
st.bokeh_chart(p)