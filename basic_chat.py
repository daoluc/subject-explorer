import streamlit as st

col1, col2 = st.columns(2)

if "counter" not in st.session_state:
    st.session_state.counter = 0

st.session_state.counter += 1


# with col1:
st.title("Echo Bot")
st.markdown("The counter is at: %i" % st.session_state.counter)

# with col2:
    # Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
# React to user input
if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})