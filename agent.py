import json
import time
import numpy as np
import streamlit as st
from bokeh.plotting import ColumnDataSource
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored
from sklearn.metrics.pairwise import cosine_similarity

from create_embeddings import create_embeddings
from load_embeddings import get_raw_embeddings_from_file  

GPT_MODEL = "gpt-4o"
client = OpenAI(
    
)

subject_ids, subject_embeddings, subject_titles, subject_description, x, y = get_raw_embeddings_from_file("full_embeddings.json")
threshold = 0.42

def highlight_subjects(subject_ids):
    print("highlighting subjects: ",subject_ids)
    print("labels: ",st.session_state.labels)
    new_data = dict(x=[], y=[], t=[], ind=[])
    for id in subject_ids:
        new_data['x'].append(x[id])
        new_data['y'].append(y[id])
        new_data['t'].append(id + ' ' + subject_titles[id])
        new_data['ind'].append(id)
    st.session_state.labels.data = new_data
    return "Subjects are highlighted in the graph"

def get_subject_info(subject_ids):
    print("getting subject info: ",subject_ids)
    subject_info = []
    for id in subject_ids:
        subject_info.append(f"Title: {id} {subject_titles[id]}. Description: {subject_description[id]}")
    return "\n".join(subject_info)

def find_related_subjects(query, top_n = 10):
    
    # create embeddings for the query
    print("creating embeddings for query: ",query)
    start_time = time.time()
    query_embedding = create_embeddings([query])[0]
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Embedding creation completed in {elapsed_time} seconds")
    
    # Calculate cosine similarity between the query and each subject
    similarities = cosine_similarity(subject_embeddings, query_embedding.reshape(1, -1))

    # Flatten the similarities array for easier handling
    similarities = similarities.flatten()

    # Filter subjects based on the threshold
    related_subjects = [(subject_ids[idx], similarities[idx]) for idx in range(len(similarities)) if similarities[idx] >= threshold]

    # Sort the results by similarity score in descending order
    related_subjects.sort(key=lambda x: x[1], reverse=True)

    subject_info = []
    for subject_id, similarity in related_subjects[:top_n]:
        subject_title = subject_titles[subject_id]
        subject_desc = subject_description[subject_id]
        subject_info.append(f"Title: {subject_id} {subject_title}. Description: {subject_desc}")

    result = "\n".join(subject_info)

    return result

@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }
    
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "function":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))

tools = [
    {
        "type": "function",
        "function": {
            "name": "find_related_subjects",
            "description": "Get the list of subjects related to the user query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "user query related to subject title or description or content",
                    },
                },
                "required": ["query"],
            },
        }        
    },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "get_subject_info",
    #         "description": "Get subject info based on subject ids. Call for multiple subjects",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "subject_ids": {
    #                     "type": "array",
    #                     "items": {
    #                         "type": "string",
    #                         "description": "subject id",
    #                     },
    #                     "description": "array of subject ids to highlight in the graph",
    #                 },
    #             },
    #             "required": ["subject_ids"],
    #         },
    #     }        
    # },
    {
        "type": "function",
        "function": {
            "name": "highlight_subjects",
            "description": "Highlight subjects in the graph. Call once at a time for multiple subjects",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject_ids": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "description": "subject id",
                        },
                        "description": "array of subject ids to highlight in the graph",
                    },
                },
                "required": ["subject_ids"],
            },
        }        
    },
]

def add_assistant_response(messages):        
    chat_response = chat_completion_request(
        messages, tools=tools, model=GPT_MODEL
    )    

    assistant_message = chat_response.choices[0].message
    print("assistant_message: ",assistant_message)

    tool_calls = assistant_message.tool_calls
    if tool_calls:
        messages.append(assistant_message)
        for tool_call in tool_calls:                        
            # If true the model will return the name of the tool / function to call and the argument(s)  
            tool_call_id = tool_call.id
            tool_function_name = tool_call.function.name        
            
            # Step 3: Call the function and retrieve results. Append the results to the messages list.      
            if tool_function_name == 'find_related_subjects':
                tool_query_string = eval(tool_call.function.arguments)['query']
                results = find_related_subjects(tool_query_string)
                
                messages.append({
                    "role":"tool", 
                    "tool_call_id":tool_call_id, 
                    "name": tool_function_name, 
                    "content":results
                })                
            elif tool_function_name == 'get_subject_info':
                subject_ids = eval(tool_call.function.arguments)['subject_ids']
                results = get_subject_info(subject_ids)
                messages.append({
                    "role":"tool", 
                    "tool_call_id":tool_call_id, 
                    "name": tool_function_name, 
                    "content":results
                })
            elif tool_function_name == 'highlight_subjects':
                subject_ids = eval(tool_call.function.arguments)['subject_ids']
                results = highlight_subjects(subject_ids)
                messages.append({
                    "role":"tool", 
                    "tool_call_id":tool_call_id, 
                    "name": tool_function_name, 
                    "content":results
                })
            else:
                messages.append({
                    "role":"tool", 
                    "tool_call_id":tool_call_id, 
                    "name": tool_function_name, 
                    "content": "Error: function does not exist"
                })            
            
        # Step 4: Invoke the chat completions API with the function response appended to the messages list
        # Note that messages with role 'tool' must be a response to a preceding message with 'tool_calls'
        add_assistant_response(messages)
    else:
        messages.append({"role": "assistant", "content": assistant_message.content})

# print(find_related_subjects("system architecture"))