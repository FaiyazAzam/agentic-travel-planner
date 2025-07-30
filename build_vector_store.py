from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pathlib import Path
import os

# Step 1: Load the documents
docs_path = Path("data/rag_docs")
# loaders = [TextLoader(str(file)) for file in docs_path.glob("*.txt")] # for txt files
loaders = [TextLoader(str(file), encoding="utf-8") for file in docs_path.glob("*.md")]
documents = []
for loader in loaders:
    documents.extend(loader.load())

# Step 2: Split documents into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs_split = splitter.split_documents(documents)

# Step 3: Use HuggingFace model to get embeddings
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Step 4: Create FAISS index
db = FAISS.from_documents(docs_split, embedding_model)

# Step 5: Save the FAISS index
db.save_local("data/faiss_index")

print("✅ FAISS vector store created and saved to 'data/faiss_index'")
