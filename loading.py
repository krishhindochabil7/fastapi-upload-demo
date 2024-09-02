import fitz  # PyMuPDF
import csv
from typing import List
from langchain.docstore.document import Document
from langchain_community.graphs import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain.text_splitter import TokenTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
import os

# Directly assign secret key values here
GROQ_API_KEY = "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"
GOOGLE_API_KEY = "AIzaSyBuAuw3GZQ5xGxf651tgWi6mguatIdmc_4"
NEO4J_URI = "neo4j+s://66a5874d.databases.neo4j.io"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "bGu3bhlAksSx-KzXcbH5MgqxGLlxAIsz9px14ISGGEg"

# Initialize API clients
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
llm = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)  # Initialize ChatGroq with specified parameters

graph = None
final_documents = None
def loading_graph(input_path):
    global graph
    global final_documents
    final_documents = []

    def load_files(input_path_or_list):
        all_documents = []
        file_count = 0  # Initialize the file counter

        def process_pdf(file_path):
            nonlocal file_count
            try:
                with fitz.open(file_path) as pdf:
                    print(f"Processing PDF file: {file_path}")  # Use logger instead of print
                    successful_pages = 0
                    for page_number in range(len(pdf)):
                        page = pdf.load_page(page_number)
                        text = page.get_text()
                        if text.strip():
                            all_documents.append(Document(page_content=text, metadata={"source": file_path, "page_number": page_number}))
                            successful_pages += 1
                    if successful_pages > 0:
                        file_count += 1  # Increment if any pages had content
            except Exception as e:
                print(f"An error occurred while processing {file_path}: {e}")

        def process_csv(file_path):
            nonlocal file_count
            try:
                with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    content = ""
                    for row in reader:
                        content += " ".join(row) + "\n"
                    if content.strip():
                        all_documents.append(Document(page_content=content, metadata={"source": file_path}))
                        file_count += 1  # Increment for each successful CSV file
                    print(f"Processing CSV file: {file_path}")  # Use logger instead of print
            except Exception as e:
                print(f"An error occurred while processing {file_path}: {e}")

        # Determine if the input is a string (path) or list of paths
        if isinstance(input_path_or_list, str):
            # Check if the string is a file path or folder path
            if os.path.isfile(input_path_or_list):
                # Single file path
                if input_path_or_list.endswith(".pdf"):
                    process_pdf(input_path_or_list)
                elif input_path_or_list.endswith(".csv"):
                    process_csv(input_path_or_list)
                else:
                    print(f"The provided file is neither a PDF nor a CSV: {input_path_or_list}")
        
            elif os.path.isdir(input_path_or_list):
                # Folder path
                try:
                    files = [os.path.join(input_path_or_list, f) for f in os.listdir(input_path_or_list) if f.endswith((".pdf", ".csv"))]
                    for file_path in files:
                        if file_path.endswith(".pdf"):
                            process_pdf(file_path)
                        elif file_path.endswith(".csv"):
                            process_csv(file_path)
                except Exception as e:
                    print(f"An error occurred while processing files in {input_path_or_list}: {e}")

            else:
                print(f"The provided path is neither a valid file nor a folder: {input_path_or_list}")

        elif isinstance(input_path_or_list, list):
            # List of file paths
            for file_path in input_path_or_list:
                if os.path.isfile(file_path):
                    if file_path.endswith(".pdf"):
                        process_pdf(file_path)
                    elif file_path.endswith(".csv"):
                        process_csv(file_path)
                    else:
                        print(f"Invalid file type in list: {file_path}")
                else:
                    print(f"Invalid file path in list: {file_path}")

        else:
            print("Invalid input: Provide either a file path, folder path, or a list of PDF/CSV file paths.")

        print(f"{file_count} file(s) under process.")
        return all_documents

    documents = load_files(input_path)
    if documents  != None:
        answer = "File uploaded successfully!"
    else:
        answer = "Error processing file. Please check input path and try again. Thank you!"

    os.environ["NEO4J_URI"] = NEO4J_URI
    os.environ["NEO4J_USERNAME"] = NEO4J_USERNAME
    os.environ["NEO4J_PASSWORD"] = NEO4J_PASSWORD

    graph = Neo4jGraph()
    text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=24)
    final_documents = text_splitter.split_documents(documents)

    llm_transformer = LLMGraphTransformer(llm=llm)
    graph_documents = llm_transformer.convert_to_graph_documents(final_documents)

    graph.add_graph_documents(
        graph_documents,
        baseEntityLabel=True,
        include_source=True
    )
    
    print("Graph loading completed.")
    return answer
