from rich import print
from langchain.docstore.document import Document
from langchain_ollama import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

local_llm = ChatOllama(model="mistral")

# RAG
def rag(chunks,collection_name):
    vectorstore = Chroma.from_documents(
        documents=documents,
        collection_name=collection_name,
        embedding=OllamaEmbeddings(model='nomic-embed-text'),
    )
    retriever = vectorstore.as_retriever()
    prompt_template = """Answer the question based only on the following context:
    {context}
    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | local_llm
        | StrOutputParser()
    )
    result = chain.invoke("What is the use of Text Splitting?")
    print(result)

# # 1. Character Text Splitting
# print("#### Character Text Splitting ####")

# text = "Text splitting in LangChain is a critical feature that facilitates the division of large texts into smaller, manageable segments. "

# # Manual Splitting
# chunks = []
# chunk_size = 35 # Characters
# for i in range(0, len(text), chunk_size):
#     chunk = text[i:i + chunk_size]
#     chunks.append(chunk)
# documents = [Document(page_content=chunk, metadata={"source": "local"}) for chunk in chunks]
# print(documents)

# # Automatic Text Splitting
# from langchain.text_splitter import CharacterTextSplitter
# text_splitter = CharacterTextSplitter(chunk_size = 35, chunk_overlap=0, separator='', strip_whitespace=False)
# documents = text_splitter.create_documents([text])
# print(documents)

# # 2. Recursive Character Text Splitting
# print("#### Recursive Character Text Splitting ####")
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# with open('content.txt', 'r', encoding='utf-8') as file:
#     text = file.read()
# text_splitter = RecursiveCharacterTextSplitter(chunk_size = 450, chunk_overlap=0) # ["\n\n", "\n", " ", ""] 65,450
# print(text_splitter.create_documents([text])) 

# # 3 Document Specific Splitting - Markdown
# from langchain.text_splitter import MarkdownTextSplitter
# splitter = MarkdownTextSplitter(chunk_size = 40, chunk_overlap=0)
# markdown_text = """
# # Fun in California

# ## Driving

# Try driving on the 1 down to San Diego

# ### Food

# Make sure to eat a burrito while you're there

# ## Hiking

# Go to Yosemite
# """
# print(splitter.create_documents([markdown_text]))

# # Document Specific Splitting - Python
# from langchain.text_splitter import PythonCodeTextSplitter
# python_text = """
# class Person:
#   def __init__(self, name, age):
#     self.name = name
#     self.age = age

# p1 = Person("John", 36)

# for i in range(10):
#     print (i)
# """
# python_splitter = PythonCodeTextSplitter(chunk_size=100, chunk_overlap=0)
# print(python_splitter.create_documents([python_text]))

# # Document Specific Splitting - Javascript
# from langchain.text_splitter import RecursiveCharacterTextSplitter, Language
# javascript_text = """
# // Function is called, the return value will end up in x
# let x = myFunction(4, 3);

# function myFunction(a, b) {
# // Function returns the product of a and b
#   return a * b;
# }
# """
# js_splitter = RecursiveCharacterTextSplitter.from_language(
#     language=Language.JS, chunk_size=65, chunk_overlap=0
# )
# print(js_splitter.create_documents([javascript_text]))

# # 4. Semantic Chunking
# print("#### Semantic Chunking ####")

# from langchain_experimental.text_splitter import SemanticChunker

# # Percentile - all differences between sentences are calculated, and then any difference greater than the X percentile is split
# text_splitter = SemanticChunker(
#     OllamaEmbeddings(model='nomic-embed-text'), breakpoint_threshold_type="percentile" # "standard_deviation", "interquartile"
# )
# documents = text_splitter.create_documents([text])
# print(documents)


# # 5. Agentic Chunking
# print("#### Proposition-Based Chunking ####")

# # https://arxiv.org/pdf/2312.06648.pdf

# from langchain.output_parsers.openai_tools import JsonOutputToolsParser
# #from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnableLambda
# from langchain.chains import create_extraction_chain
# from typing import Optional, List
# from langchain.chains import create_extraction_chain_pydantic
# from pydantic import BaseModel
# from langchain import hub

# from langchain_community.document_loaders import PyPDFLoader

# # Load text from PDF
# loader = PyPDFLoader("burns.pdf")
# pdf_documents = loader.load()
# text = "\n\n".join(doc.page_content for doc in pdf_documents)

# obj = hub.pull("wfh/proposal-indexing")
# # llm = ChatOpenAI(model='gpt-3.5-turbo') # Use local_llm instead
# runnable = obj | local_llm

# class Sentences(BaseModel):
#     sentences: List[str]
#  # Extraction
# structured_llm = local_llm.with_structured_output(Sentences)

# def get_propositions(text):
#     runnable_output = runnable.invoke({
#         "input": text
#     }).content
#     propositions = structured_llm.invoke(runnable_output).sentences
#     return propositions
    
# paragraphs = text.split("\n\n")
# text_propositions = []
# for i, para in enumerate(paragraphs[:5]):
#     if not para.strip(): # Skip empty paragraphs
#         continue
#     propositions = get_propositions(para)
#     text_propositions.extend(propositions)
#     print (f"Done with paragraph {i}")

# print (f"You have {len(text_propositions)} propositions")
# print(text_propositions[:10])

# Agentic Chunking with openrouter mistral 
print("#### Proposition-Based Chunking with OpenRouter ####")

from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.chains import create_extraction_chain
from typing import Optional, List
from langchain.chains import create_extraction_chain_pydantic
from pydantic import BaseModel
from langchain import hub
from os import getenv
from dotenv import load_dotenv
import json

from langchain_community.document_loaders import PyPDFLoader

# Load environment variables for OpenRouter
load_dotenv()

# Load text from PDF
loader = PyPDFLoader("burns.pdf")
pdf_documents = loader.load()
text = "\n\n".join(doc.page_content for doc in pdf_documents)

# Configure LLM for OpenRouter
openrouter_llm = ChatOpenAI(
  openai_api_key=getenv("OPENROUTER_API_KEY"),
  openai_api_base=getenv("OPENROUTER_BASE_URL"),
  model_name="mistralai/mistral-7b-instruct",
  model_kwargs={
    "default_headers": {
      "HTTP-Referer": getenv("YOUR_SITE_URL"),
      "X-Title": getenv("YOUR_SITE_NAME"),
    }
  },
)


obj = hub.pull("wfh/proposal-indexing")
runnable = obj | openrouter_llm

class Sentences(BaseModel):
    sentences: List[str]
 # Extraction
structured_llm = openrouter_llm.with_structured_output(Sentences)

def get_propositions(text):
    runnable_output = runnable.invoke({
        "input": text
    }).content
    propositions = structured_llm.invoke(runnable_output).sentences
    return propositions
    
paragraphs = text.split("\n\n")
text_propositions = []
for i, para in enumerate(paragraphs[:5]):
    if not para.strip(): # Skip empty paragraphs
        continue
    propositions = get_propositions(para)
    text_propositions.extend(propositions)
    print (f"Done with paragraph {i}")

# Save paragraphs and propositions to a JSON file
with open('propositions.json', 'w', encoding='utf-8') as f:
    json.dump({'paragraphs': paragraphs, 'propositions': text_propositions}, f, indent=4, ensure_ascii=False)

print (f"You have {len(text_propositions)} propositions")