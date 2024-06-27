import streamlit as st
import pandas as pd
from bokeh.plotting import ColumnDataSource, figure
from load_embeddings import get_2d_embeddings_from_file
from bokeh.models import TapTool, CustomJS, HoverTool, LabelSet

st.title('MIT Subject Explorer')

TOOLTIPS = """
<div style="width:300px;">
@id @title <br> <br>
</div>
"""

data = get_2d_embeddings_from_file('embeddings.json')

p = figure(width=700, height=583, x_range=(-5, 20), y_range=(0,25), tooltips=TOOLTIPS,
           title="UMAP projection of embeddings for MIT subjects")

labels = ColumnDataSource(data=dict(x=[], y=[], t=[], ind=[]))
p.add_layout(LabelSet(x='x', y='y', text='t', y_offset=5, x_offset=5, source=labels, text_font_size='8pt'))

code = """
const data = labels.data
for (const key in points) {
    if (points[key].selected.indices.length > 0) {
        const ind = points[key].selected.indices[0];
        
        const text = points[key].data.id[ind] + ' ' + points[key].data.title[ind];
        if (data.t.includes(text)) {
            const index = data.t.indexOf(text);
            data.x.splice(index, 1);
            data.y.splice(index, 1);
            data.t.splice(index, 1);
            data.ind.splice(index, 1);
        }
        else {        
            data.x.push(points[key].data.x[ind]);
            data.y.push(points[key].data.y[ind]);
            data.t.push(text);
            data.ind.push(ind);
            window.open('https://student.mit.edu/catalog/search.cgi?search=' + points[key].data.id[ind], '_blank');
        }
        break;
    }
}
labels.change.emit();
"""

types =  ['Core',    'Eng & Mgmt Depth', 'Eng Depth', 'Mgmt Depth', 'Eng & Mgmt Elective', 'Eng Elective', 'Mgmt Elective', 'Other']
colors = ['#0460D9', '#F2A413',          '#750014',   '#358C6C',    '#F2A413',             '#750014',      '#358C6C',       'gray']
points = dict()

for t in types:
    source = ColumnDataSource(data[data["type"] == t])
    points[t] = source
    if(t=='Core'):
        p.square('x', 'y', size=8, source=source, alpha=0.8, legend_label=t, color=colors[types.index(t)])
    elif 'Depth' in t:
        p.square('x', 'y', size=8, source=source, alpha=0.5, legend_label=t, color=colors[types.index(t)])
    elif 'Elective' in t:
        p.triangle('x', 'y', size=8, source=source, alpha=0.5, legend_label=t, color=colors[types.index(t)])
    else:
        p.circle('x', 'y', size=4, source=source, alpha=0.3, legend_label=t, color=colors[types.index(t)])
    p.legend.title = 'Subject Type'
    p.legend.location = "top_left"
    p.legend.click_policy="hide"
    
callback=CustomJS(args=dict(points=points, labels=labels), code=code)
p.add_tools(TapTool(callback=callback))

st.bokeh_chart(p)