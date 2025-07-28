import streamlit as st
import os
import glob
import time
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
from src.agent import create_csv_agent

load_dotenv()
st.set_page_config(page_title="CSV Analysis Agent")

if "agent_executor" not in st.session_state:
    st.session_state.agent_executor = create_csv_agent()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "loaded_files" not in st.session_state:
    st.session_state.loaded_files = []


def cleanup_temp_files():
    for file_path in glob.glob("temp_*.csv"):
        try:
            os.remove(file_path)
        except OSError:
            pass


def extract_plots_from_response(response_text):
    plots = []
    lines = response_text.split('\n')
    
    for line in lines:
        if '.png' in line:
            import re
            png_matches = re.findall(r'[`\'"]?([^`\'"]*\.png)[`\'"]?', line)
            for match in png_matches:
                if match and os.path.exists(match):
                    plots.append(match)
    
    return plots


def display_message_plots(message_plots):
    if message_plots:
        for plot_file in message_plots:
            if os.path.exists(plot_file):
                st.image(plot_file, caption=plot_file)


with st.sidebar:
    st.header("Upload CSV Files")
    uploaded_files = st.file_uploader(
        "Choose one or more CSV files",
        type=['csv'],
        accept_multiple_files=True
    )

    if uploaded_files and st.button("Load CSV(s)"):
        cleanup_temp_files()

        with st.spinner("Loading CSV files..."):
            temp_files = []
            loaded_count = 0

            try:
                for uploaded_file in uploaded_files:
                    temp_file_path = f"temp_{uploaded_file.name}"
                    with open(temp_file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    temp_files.append(temp_file_path)

                for temp_file_path, uploaded_file in zip(temp_files, uploaded_files):
                    try:
                        load_request = f"Please load the CSV file at {temp_file_path}, just load the file and do not do any analysis for now, later we will ask you to analyze the data"

                        response = st.session_state.agent_executor.invoke({
                            "input": load_request,
                            "chat_history": st.session_state.chat_history
                        })

                        new_plots = extract_plots_from_response(
                            response['output'])

                        user_msg = f"Loaded CSV file: {uploaded_file.name}"
                        st.session_state.messages.append({
                            "role": "user",
                            "content": user_msg,
                            "plots": []
                        })
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response['output'],
                            "plots": new_plots
                        })

                        st.session_state.chat_history.append(
                            HumanMessage(content=user_msg))
                        st.session_state.chat_history.append(
                            AIMessage(content=response['output']))

                        st.session_state.loaded_files.append(
                            uploaded_file.name)
                        loaded_count += 1

                    except Exception as e:
                        st.error(
                            f"Failed to load {uploaded_file.name}: {str(e)}")

                if loaded_count > 0:
                    st.success(f"Successfully loaded {loaded_count} file(s)")
                    st.rerun()

            finally:
                cleanup_temp_files()

    if st.session_state.loaded_files:
        st.markdown("**Loaded CSV files:**")
        for fname in st.session_state.loaded_files:
            st.markdown(f"- {fname}")

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.loaded_files = []
        cleanup_temp_files()
        st.rerun()

st.title("CSV Analysis Agent")
st.markdown("Upload CSV files and ask questions about your data.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "plots" in message:
            display_message_plots(message["plots"])

if prompt := st.chat_input("Ask about your data..."):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "plots": []
    })
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                response = st.session_state.agent_executor.invoke({
                    "input": prompt,
                    "chat_history": st.session_state.chat_history
                })

                agent_response = response['output']
                st.markdown(agent_response)

                new_plots = extract_plots_from_response(agent_response)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": agent_response,
                    "plots": new_plots
                })
                st.session_state.chat_history.append(
                    HumanMessage(content=prompt))
                st.session_state.chat_history.append(
                    AIMessage(content=agent_response))

                display_message_plots(new_plots)

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "plots": []
                })
