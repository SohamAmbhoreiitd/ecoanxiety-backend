import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from app.config import GROQ_API_KEY

# --- Constants ---
KNOWLEDGE_BASE_DIR = "knowledge_base"
CHROMA_PERSIST_DIR = "chroma_db"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# --- UPDATED: Fallback Constants ---
# Increased the threshold to be more lenient. We'll now only fallback if the
# distance is very high (greater than 1.0).
DISTANCE_THRESHOLD = 1.7 
FALLBACK_RESPONSE = "I'm sorry, but my knowledge is focused on providing support for eco-anxiety and related topics. I can't answer questions outside of that scope. How are you feeling today?"


def create_vector_db():
    # This function remains unchanged
    print("--- Starting Vector DB creation ---")
    loader = DirectoryLoader(KNOWLEDGE_BASE_DIR, glob="**/*.md", loader_cls=TextLoader)
    documents = loader.load()
    if not documents:
        print("No documents found in the knowledge base. Aborting.")
        return
    print(f"Loaded {len(documents)} document(s).")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    print(f"Split documents into {len(texts)} chunks.")
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    print(f"Creating and persisting vector store to '{CHROMA_PERSIST_DIR}'...")
    vectordb = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=CHROMA_PERSIST_DIR
    )
    print("--- Vector DB creation complete! ---")


# --- THIS IS THE UPDATED FUNCTION ---
def get_chat_response(query: str, chat_history: list):
    """
    Generates a response using the RAG pipeline with a corrected fallback mechanism.
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectordb = Chroma(
        persist_directory=CHROMA_PERSIST_DIR,
        embedding_function=embeddings
    )

    # 1. Use similarity_search_with_score to get distance scores (lower is better)
    retrieved_docs_with_scores = vectordb.similarity_search_with_score(query, k=1)
    
    # --- NEW: Add a print statement for debugging ---
    if retrieved_docs_with_scores:
        top_doc_score = retrieved_docs_with_scores[0][1]
        print(f"Top document score: {top_doc_score:.4f}")
    
    # 2. If no docs are found OR the distance is too high, use the fallback
    if not retrieved_docs_with_scores or retrieved_docs_with_scores[0][1] > DISTANCE_THRESHOLD:
        print("--- Fallback triggered: Score is above threshold. ---")
        return FALLBACK_RESPONSE

    # 3. If relevance is high enough (distance is low), proceed with the conversational chain
    print("--- Fallback not triggered: Proceeding with LLM. ---")
    retriever = vectordb.as_retriever(search_kwargs={"k": 2})
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=ChatGroq(
            groq_api_key=GROQ_API_KEY,
            model_name="llama-3.1-8b-instant",
            temperature=0.7
        ),
        retriever=retriever,
        memory=memory
    )
    result = qa_chain({"question": query, "chat_history": chat_history})
    return result['answer']


# ... (The if __name__ == '__main__' block remains the same for testing)
if __name__ == '__main__':
    print("--- Running Comprehensive Test Suite ---")

    # --- Test Suite 1: In-Depth Conversation (Memory & Relevance) ---
    print("\n\n--- Test Suite 1: In-Depth Conversation ---")
    chat_history_1 = []
    
    # Start with an emotional, relevant query
    query1 = "I've been feeling a lot of guilt about climate change."
    print(f"\n[User]: {query1}")
    response1 = get_chat_response(query1, chat_history_1)
    print(f"[AI]: {response1}")
    chat_history_1.append((query1, response1))
    
    # Follow-up that relies on the context of "guilt"
    query2 = "What can I do about it?"
    print(f"\n[User]: {query2}")
    response2 = get_chat_response(query2, chat_history_1)
    print(f"[AI]: {response2}")
    chat_history_1.append((query2, response2))
    
    # Specific follow-up that relies on the context of the AI's last response (Sphere of Control)
    query3 = "Tell me more about the inner circle of that exercise."
    print(f"\n[User]: {query3}")
    response3 = get_chat_response(query3, chat_history_1)
    print(f"[AI]: {response3}")

    # --- Test Suite 2: Fallback System Robustness ---
    print("\n\n--- Test Suite 2: Fallback System ---")
    
    # Irrelevant factual question
    query4 = "What is the capital of Mongolia?"
    print(f"\n[User]: {query4}")
    response4 = get_chat_response(query4, [])
    print(f"[AI]: {response4}")
    
    # Thematically related but out-of-scope (financial advice)
    query5 = "Should I invest my money in solar panel stocks?"
    print(f"\n[User]: {query5}")
    response5 = get_chat_response(query5, [])
    print(f"[AI]: {response5}")
    
    # Gibberish input
    query6 = "asdfghjkl"
    print(f"\n[User]: {query6}")
    response6 = get_chat_response(query6, [])
    print(f"[AI]: {response6}")

    # --- Test Suite 3: Vague & Emotional Input ---
    print("\n\n--- Test Suite 3: Vague & Emotional Input ---")
    
    # Short, emotional query
    query7 = "I'm feeling overwhelmed."
    print(f"\n[User]: {query7}")
    response7 = get_chat_response(query7, [])
    print(f"[AI]: {response7}")
