import streamlit as st

# Initialize the chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
    
# Main layout
st.set_page_config(layout="wide")

col1, col2 = st.columns([4,6])

with col1:
    st.header("Ask")
    
    chat_container = st.container(height=750)    
    
    if prompt := st.chat_input("What is up?"):   
        st.session_state.messages.append({"role": "user", "content": prompt})

    with chat_container:
        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
with col2:
    st.header("Graph")

