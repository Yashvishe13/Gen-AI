
# IMPORTING LIBRARIES
import os
from langchain_google_vertexai import VertexAI
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from getpass import getpass

# SETTING KEYS
os.environ['GOOGLE_API_KEY'] = os.getenv('GOOGLE_API_KEY')
## Langmith tracking
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]="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"



# CREATING PROMPTS

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please response to user queries in 3-4 sentences"),
        ("user", "Question:{question}")
    ]
)

# STREAMLIT UI
st.title("CHATBOT")
input_text = st.text_input("Ask a query here")

# LLM
model = VertexAI(model_name="gemini-1.5-pro-preview-0409")
output_parser = StrOutputParser()
chain = prompt|model|output_parser

if input_text:
    st.write(chain.invoke({"question":input_text}))
