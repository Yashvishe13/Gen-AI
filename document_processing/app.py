import vertexai
from langchain_google_vertexai import VertexAI, ChatVertexAI, VertexAIEmbeddings

from langchain.prompts import PromptTemplate
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import HumanMessage, SystemMessage

import base64
import os
import uuid
import io
import re
import streamlit as st

from langchain.retrievers.multi_vector import MultiVectorRetriever
from langchain.storage import InMemoryStore
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from PIL import Image

# Define project information
PROJECT_ID = "ai-research-agent-yash" 
REGION = "us-central1"  

vertexai.init(project=PROJECT_ID, location=REGION)

loader = PyPDFLoader("google_report.pdf")
docs = loader.load()
tables = []
texts = [d.page_content for d in docs]

print(len(texts))

def generate_text_summaries(texts, tables, summarize_texts=False):
  """

  Summarize text elements
  texts: List of str
  tables: List of str
  summarize_texts: Bool to summarize texts
  """

  # Prompt
  prompt_text = """You are an assistant tasked with summarizing tables and text for retrieval. \
  These summaries will be embedded and used to retrieve the raw text or table elements. \
  Give a concise summary of the table or text that is well optimized for retrieval. Table or text: {element} """

  prompt = PromptTemplate.from_template(prompt_text)
  empty_response = RunnableLambda(
      lambda x: AIMessage(content="Error processing document")
  )
  # Text summary chain
  model = VertexAI(
      temperature=0, model_name="gemini-1.5-pro-preview-0409", max_output_tokens=1024
  ).with_fallbacks([empty_response])
  summarize_chain = {"element": lambda x: x} | prompt | model | StrOutputParser()

  # Initialize empty summaries
  text_summaries = []
  table_summaries = []

  # Apply to text if texts are provided and summarization is requested
  if texts and summarize_texts:
    text_summaries = summarize_chain.batch(texts, {"max_concurrency": 1})
  elif texts:
    text_summaries = texts

  # Apply to tables if tables are provided
  if tables:
    table_summaries = summarize_chain.batch(tables, {"max_concurrency": 1})

  return text_summaries, table_summaries

# Get text, table summaries
text_summaries, table_summaries = generate_text_summaries(
    texts, tables, summarize_texts=True
)

print(len(text_summaries))

def encode_image(image_path):
  """Getting the base64 string"""
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode("utf-8")

def image_summarize(img_base64, prompt):
  """Make image summary"""
  model = ChatVertexAI(model_name="gemini-1.5-pro-preview-0409", max_output_tokens=1024)

  msg = model(
      [
          HumanMessage(
              content=[
                  {"type": "text", "text": prompt},
                  {
                      "type": "image_url",
                      "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                  },
              ]
          )
      ]
  )
  return msg.content

def generate_img_summaries(path):
  """
  Generate summaries and base64 encoded strings for images
  path: Path to list of .jpg files extracted by Unstructured
  """

  # Store base64 encoded images
  img_base64_list=[]

  # Store image summaries
  image_summaries = []

  # Prompt
  prompt = """You are an assistant tasked with summarizing images for retrieval. \
  These summaries will be embedded and used to retrieve the raw image. \
  Give a concise summary of the image that is well optimized for retrieval."""

  # Apply to images
  for img_file in sorted(os.listdir(path)):
    if img_file.endswith(".jpg"):
      img_path = os.path.join(path, img_file)
      base64_image = encode_image(img_path)
      img_base64_list.append(base64_image)
      image_summaries.append(image_summarize(base64_image, prompt))

  return img_base64_list, image_summaries


# Image summaries
img_base64_list, image_summaries = generate_img_summaries("images")
print("img base list:", len(img_base64_list))

def create_multi_vector_retriever(
    vectorstore, text_summaries, texts, table_summaries, tables, image_summaries, images
):
    """
    Create retriever that indexes summaries but returns raw images or texts
    """

    # Initialize the storage layer
    store = InMemoryStore()
    id_key = "doc_id"

    # Create the multi-vector retriever
    retriever = MultiVectorRetriever(
        vectorstore = vectorstore,
        docstore = store,
        id_key = id_key,
    )

    # Helper function to add documents to the vectorstore and docstore
    def add_documents(retriever, doc_summaries, doc_contents):
      doc_ids = [str(uuid.uuid4()) for _ in doc_contents]
      summary_docs = [
          Document(page_content=s, metadata={id_key: doc_ids[i]})
          for i,s, in enumerate(doc_summaries)
      ]
      retriever.vectorstore.add_documents(summary_docs)
      retriever.docstore.mset(list(zip(doc_ids, doc_contents)))

    # Add texts, tables, and images
    # Check that text_summaries is not empty before adding
    if text_summaries:
      add_documents(retriever, text_summaries, texts)
    # CHeck that table_summaries is not empty before adding
    if table_summaries:
      add_documents(retriever, table_summaries, tables)
    # Check that image_summaries is not empty before adding
    if image_summaries:
      add_documents(retriever, image_summaries, images)

    return retriever

# The vectorstore to use to index the summaries
vectorstore = Chroma(
    collection_name = "mm_rag_cj_blog",
    embedding_function=VertexAIEmbeddings(model_name="textembedding-gecko@latest"),
)

# Create Retriever
retriever_multi_vector_img = create_multi_vector_retriever(
    vectorstore,
    text_summaries,
    texts,
    table_summaries,
    tables,
    image_summaries,
    img_base64_list,
)

def plt_img_base64(img_base64):
  """Display base64 encoded string as image"""
  # Create an HTML img tag with the base64 string as source
  image_html = f'<img src="data"image/jpeg;base64,{img_base64}" />'
  # Display the image by rendering the HTML
  display(HTML(image_html))

def looks_like_base64(sb):
  """CHceck if the string looks like base64"""
  return re.match("^[A-Za-z0-9+/]+[=]{0,2}$", sb) is not None

def is_image_data(b64data):
  """
  CHeck if the base64 data is an image by looking at the start of the data
  """
  image_signatures = {
      b"\xFF\xD8\xFF": "jpg",
      b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A": "png",
      b"\x47\x49\x46\x38": "gif",
      b"\x52\x49\x46\x46": "webp",
  }
  try:
    header = base64.b64decode(b64data)[:8] # Decode and get the first 8 bytes
    for sig, format in image_signatures.items():
      if header.startswith(sig):
        return True
    return False
  except Exception:
    return False

def resize_base64_image(base64_string, size=(128,128)):
  img_data = base64.b64decode(base64_string)
  img = Image.open(io.BytesIO(img_data))

  # Resize the image
  resized_img = img.resize(size, Image.LANCZOS)

  # Save the resized image to a bytes buffer
  buffered = io.BytesIO()
  resized_img.save(buffered, format=img.format)

  # Encode the resized image to Base64
  return base64.b64encode(buffered.getvalue()).decode("utf-8")

def split_image_text_types(docs):
  b64_images=[]
  texts = []
  for doc in docs:
    if isinstance(doc, Document):
      doc = doc.page_content
    if looks_like_base64(doc) and is_image_data(doc):
      doc = resize_base64_image(doc, size=(1300,600))
      b64_images.append(doc)
    else:
      texts.append(doc)
  if len(b64_images) > 0:
    return {"images": b64_images[:1], "texts": []}
  return {"images":b64_images, "texts": texts}


def img_prompt_func(data_dict):

  formatted_texts = "\n".join(data_dict["context"]["texts"])
  messages = []

  text_message = {
      "type": "text",
      "text": (
          "You are Graph analyst tasked with providing insights in the Graph.\n"
          "You will be given a mixed of text, tables, and image(s) usually of charts or graphs. Try to extract numbers using x-axis and y-axies on the charts\n"
          "Use this information to provide information related to the user question. \n"
          f"Use-provided question: {data_dict['question']}\n\n"
          "Text and/or tables: \n"
          f"{formatted_texts}"
      ),
  }
  messages.append(text_message)
  # Adding image(s) to the messages if present
  if data_dict["context"]["images"]:
    for image in data_dict["context"]["images"]:
      image_message = {
          "type": "image_url",
          "image_url": {"url": f"data:image/jpeg;base64,{image}"},
      }
      messages.append(image_message)
  return [HumanMessage(content=messages)]


def multi_modal_rag_chain(retriever):
  """
  Multi-modal RAG chain
  """

  # Multi-modal LLM
  model = ChatVertexAI(
      temperature = 0, model_name = "gemini-1.5-pro-preview-0409", max_output_tokens=1024
  )

  # RAG Pipeline
  chain = (
      {
          "context": retriever | RunnableLambda(split_image_text_types),
          "question": RunnablePassthrough(),
      }
      | RunnableLambda(img_prompt_func)
      | model
      | StrOutputParser()
  )

  return chain


# Create RAG chain
chain_multimodal_rag = multi_modal_rag_chain(retriever_multi_vector_img)

st.title("Document Query App")

query = st.text_input("Ask your question here")
# query = "how is the performance of Alphabet Inc compared to S&P 500 in comparison of cummulative 5-Year total return"
if query:
    docs = retriever_multi_vector_img.invoke(query, limit=1)

    print("len of docs:", len(docs))
    result = chain_multimodal_rag.invoke(query)
    st.write(result)