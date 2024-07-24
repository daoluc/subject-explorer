import streamlit as st
st.set_page_config(layout="wide")

import pandas as pd
from bokeh.plotting import ColumnDataSource, figure
from agent import add_assistant_response
from load_embeddings import get_2d_embeddings_from_file
from bokeh.models import TapTool, CustomJS, HoverTool, LabelSet
from streamlit_js_eval import streamlit_js_eval



st.markdown(
    """
<style>
    h1 {
        padding: 0;
    }
    div[data-testid="stAppViewBlockContainer"] {
        padding: 50px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

if 'labels' not in st.session_state:
    st.session_state['labels'] = ColumnDataSource(data=dict(x=[], y=[], t=[], ind=[]))

# Initialize the chat history
if 'messages' not in st.session_state:
    learning_objectives = {
        "lo.SA01": "Structure and lead the early conceptual phases of the system development process.",
        "lo.SA02": "Define system architecture, explain what a system is, and how behavior emerges.",
        "lo.SA03": "Effectively describe the architecture of systems and critique descriptions of system architecture.",
        "lo.SA04": "Define the role of a system architect, describe the organizational issues likely to arise for the architect, shape where the architecting process fits within a PDP, and manage the architecture through operation and evolution.",
        "lo.SA05": "Identify and prioritize the stakeholders of the system quantitatively and qualitatively, and elicit and prioritize their needs.",
        "lo.SA06": "Articulate how a product creates value and competitive advantage from its system architecture, and articulate how corporate strategy, marketing, regulation, and platform strategies influence architecture and vice versa.",
        "lo.SA07": "Generate several architectures for new or improved systems using both structured and unstructured approaches.",
        "lo.SA08": "Select preferred system architectures from a set of architectures, a list of architectural decisions, or a tradespace of architectures.",
        "lo.SA09": "Define and produce the deliverables of the architect needed to define the architecture of a system, including actively choosing abstractions, hierarchy, and a decomposition for the system.",
        "lo.SA10": "Develop a personal set of guiding principles for successful architecting.",
        "lo.SE01": "Understand fundamental principles and methods of engineering complex systems and how they may evolve in practice due to changes in enabling technological and organizational systems and context.",
        "lo.SE02": "Elicit, define and formally articulate system value to help guide system priorities and structure value-generating activities across the system lifecycle.",
        "lo.SE03": "Analyze, understand, and represent system behavior by defining and analyzing system missions, operations, modes, and use cases.",
        "lo.SE04": "Define and manage requirements over the system’s lifecycle, tailoring the process to accommodate the system, its context, and emerging technologies and methods.",
        "lo.SE05": "Define and systematically explore the system’s tradespace in order to optimally select amongst competing alternatives and objectives.",
        "lo.SE06": "Define and manage the internal and external interfaces of a system given a particular choice of system boundary, architecture and decomposition.",
        "lo.SE07": "Analyze and manage changes to the system over its lifecycle.",
        "lo.SE08": "Understand the role of rigorous models of cyber-physical systems, formal modeling languages, and related approaches in the use of simulation and modeling in the system development process.",
        "lo.SE09": "Plan and execute a system verification and validation program, including the design, analysis, and sequencing of appropriate experiments and test campaigns.",
        "lo.SE10": "Understand the role of the system engineer in tailoring the system engineering approach to ensure maximum value delivery over the lifecycle of the system, including development, manufacturing, and operations.",
        "lo.PM01": "Explore and define linkages between a project and the portfolio of an organization.",
        "lo.PM02": "Define a project’s strategic purpose with estimates of systemic value, including metrics for verification.",
        "lo.PM03": "Define a project charter in response to strategy and stakeholder views, including targets and priorities across cost, schedule, scope and risk.",
        "lo.PM04": "Generate a project plan that is feasible given scope, resources, roles, dependencies, and risks.",
        "lo.PM05": "Model a project as integrated product, process, and organizational systems. Leverage dynamic modeling to forecast emergent outcomes including rework.",
        "lo.PM06": "Recommend a plan to stakeholders with a trade-space of alternatives across cost, schedule, scope, and risk.",
        "lo.PM07": "Credibly challenge unrealistic expectations related to project cost, schedule, scope, and risk. Lead others to shift attention, analyze, learn, and adapt.",
        "lo.PM08": "Establish a monitor and ongoing adaptive control approach including measures of value, scope progress, change, risk, cost, and other metrics.",
        "lo.PM09": "Identify key skills and attitudes required for effective leadership and team readiness in systems development programs.",
        "lo.PM10": "Design, select, and prepare project architecture and teamwork for diverse and geographically distributed projects."
    }

    context_str = "EM.411, EM.412, and EM.413 are System Design and Management (SDM) Core subjects. The learning objectives (lo) of SDM are " + "\n".join([f"{key}: {value}" for key, value in learning_objectives.items()]) + ''' 
    You are an academic advisor, helping SDM students explore subjects provided by MIT. Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous. Always include both subject id and subject title such as 'EM.411 Foundations of System Design and Management' when referring to a subject. Highlight the related subjects in the graph.
    Be concise and straight to the point when you response.
    '''        

    initial_messages = []
    initial_messages.append({"role": "system", "content": context_str})
    initial_messages.append({"role": "assistant", "content": "how can I help you today?"})
    st.session_state['messages'] = initial_messages

st.title('MIT Subject Explorer')
page_height = int(streamlit_js_eval(js_expressions='screen.height', key = 'SCR1'))
col1, col2 = st.columns([4,6], gap='large')

# chat bar
with col1:
    chat_container = st.container( height=max(page_height-400, 500) )    
    
    if prompt := st.chat_input("What is up?"):   
        st.session_state.messages.append({"role": "user", "content": prompt})
        add_assistant_response(st.session_state.messages)

    with chat_container:
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            if "role" in message and (message["role"] == "user" or message["role"] == "assistant"):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
# graph
with col2:
    TOOLTIPS = """
    <div style="width:300px;">
    @id @title <br> <br>
    </div>
    """

    data = get_2d_embeddings_from_file('full_embeddings.json')

    p = figure(width=700, height=500, x_range=(-5, 20), y_range=(0,25), tooltips=TOOLTIPS,
            title="UMAP projection of the embeddings of MIT subjects")
    
    # labels = st.session_state.labels 
    labels = ColumnDataSource(data=dict(x=[], y=[], t=[], ind=[]))
    labels.data = dict(st.session_state.labels.data)
    p.add_layout(LabelSet(x='x', y='y', text='t', y_offset=5, x_offset=5, source=labels, text_font_size='8pt'))

    code = """
    const data = labels.data
    for (const key in points) {
        if (points[key].selected.indices.length > 0) {
            const ind = points[key].selected.indices[0];
            
            const text = points[key].data.id[ind] + ' ' + points[key].data.title[ind];
            if (!data.t.includes(text)) {
                data.x.push(points[key].data.x[ind]);
                data.y.push(points[key].data.y[ind]);
                data.t.push(text);
                data.ind.push(ind);                
            }
            window.open('https://student.mit.edu/catalog/search.cgi?search=' + points[key].data.id[ind], '_blank');
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