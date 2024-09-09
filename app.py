import streamlit as st
import sqlite3
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

st.set_page_config(page_title="Chat with websites", page_icon="🤖")

load_dotenv()

# Custom CSS with the new color palette
st.markdown(
    """
    <style>
    
        input {
            color: white !important;
        }
        /* Main app background color */
        .stApp {
            background-color: #2B2E4A;  /* Dark slate blue */
            font-family: 'Arial', sans-serif;
            color: #FFFFFF;  /* Apply the text color globally */
        }

         div[data-testid="stTextInput"] input {
        color: #FFFFFF; /* Set your desired text color here */
    }
        
        /* Button styling */
        .stButton>button {
            background-color: #E84545;  /* Bright red for button background */
            color: #FFFFFF;  /* Button text color */
            font-size: 16px;
            border-radius: 8px;
        }
        
        .centered-text {
        text-align: center;
        color: #E84545;
    }

        /* Input field styling */
        .stTextInput>div>div>input {
            width: 100%;
            border: 1px solid #903749;  /* Dark red-pink for input border */
            padding: 10px;
            border-radius: 5px;
            color: #E23E57;  /* Ensure input text color */
        }

        /* Input label styling */
        .stTextInput>div>div>label {
            color: #E23E57;  /* Updated text color */
            font-size: 16px;
        }

        /* Alert box styling */
        .stAlert {
            border-radius: 10px;
            background-color: #903749;  /* Dark red-pink for alert background */
            color: #FFFFFF;  /* Alert text color */
        }

        /* Customize alert message font */
        .stAlert > div {
            font-size: 16px;
        }

        .stAlert > div > p {
            margin: 0;
        }

        /* Title styling */
        .css-1y0tads {
            font-size: 3em;  /* Increased font size for title */
            color: #E23E57;  /* Updated text color */
            font-weight: bold;
            text-align: center;  /* Center align the title */
            margin-bottom: 0.5em;
        }

    </style>
    """,
    unsafe_allow_html=True
)


class WebsiteDatabase:
    def __init__(self, db_name="websites.db"):
        self.db_name = db_name
        self.create_website_table()
        self.create_user_table()

    def create_website_table(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            query = """
            CREATE TABLE IF NOT EXISTS websites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                url TEXT NOT NULL
            )
            """
            conn.execute(query)
            conn.commit()

    def create_user_table(self):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
            """
            conn.execute(query)
            conn.commit()

    def get_url(self, name):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            query = "SELECT url FROM websites WHERE name = ?"
            cursor = conn.execute(query, (name,))
            result = cursor.fetchone()
            return result[0] if result else None

    def add_user(self, name, email, password):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            query = "INSERT INTO users (name, email, password) VALUES (?, ?, ?)"
            conn.execute(query, (name, email, generate_password_hash(password)))
            conn.commit()

    def get_user(self, email):
        with sqlite3.connect(self.db_name, check_same_thread=False) as conn:
            query = "SELECT * FROM users WHERE email = ?"
            cursor = conn.execute(query, (email,))
            result = cursor.fetchone()
            return result


def signup():
    st.title("Sign Up")
    st.markdown("Please enter your details to create an account.")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        if not name or not email or not password:
            st.error("All fields are required.")
        elif "@" not in email:
            st.error("Please enter a valid email address.")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters long.")
        else:
            db = WebsiteDatabase()
            if db.get_user(email):
                st.error("Email is already registered. Please log in.")
            else:
                db.add_user(name, email, password)
                st.success("Signup successful! Please log in.")
                st.session_state.page = "login"

    if st.button("Already have an account? Log in"):
        st.session_state.page = "login"


def login():
    st.title("Login")
    st.markdown("Please enter your credentials to log in.")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        db = WebsiteDatabase()
        user = db.get_user(email)
        if user and check_password_hash(user[3], password):
            st.success("Login successful!")
            st.session_state.page = "main"
            st.session_state.user_name = user[1]
            st.experimental_rerun()  # Trigger a rerun to navigate to the main page
        else:
            st.error("Invalid email or password.")

    if st.button("Don't have an account? Sign Up"):
        st.session_state.page = "signup"
        st.experimental_rerun()


def get_vectorstore_from_url(url):
    loader = WebBaseLoader(url)
    document = loader.load()
    text_splitter = RecursiveCharacterTextSplitter()
    document_chunks = text_splitter.split_documents(document)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma.from_documents(document_chunks, embeddings)
    return vector_store


def get_context_retriever_chain(vector_store):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, max_output_tokens=500)
    retriever = vector_store.as_retriever()
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user",
         "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    return retriever_chain


def get_conversational_rag_chain(retriever_chain):
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, max_output_tokens=500)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a highly specialized assistant designed to provide information strictly based on the specified website context."
         "If a user asks for something that is not explicitly covered or available on the website, for example if the "
         "user asks code for anything or anything that's not related to the website of not mentioned in the website you must respond with: "
         "'This information is not mentioned on the website, and I cannot provide information outside of this context.' "
         "Avoid any speculation, generalization, or discussion on topics not found in the provided context: \n\n{context}"
         ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])
    stuff_documents_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)


def get_response(user_input):
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)
    response = conversation_rag_chain.invoke({
        "chat_history": st.session_state.chat_history,
        "input": user_input
    })

    # Enforce restriction on responses to ensure it stays within context
    if "outside of this context" not in response['answer']:
        return response['answer']
    else:
        return "This information is not mentioned on the website, and I cannot provide information outside of this context."


# App configuration
st.markdown('<h1 class="centered-text">Chat with T&C of any Websites ', unsafe_allow_html=True)

# Streamlit app control flow
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.page == "login":
    login()
elif st.session_state.page == "signup":
    signup()
elif st.session_state.page == "main":
    # Main page content (if logged in)
    st.markdown(f"<h2 class='stTitle'>Welcome, {st.session_state.user_name}!</h2>", unsafe_allow_html=True)

    # Sidebar for URL input using website name
    with st.sidebar:
        st.header("Settings")
        website_name = st.text_input("Website Name").lower()

    db = WebsiteDatabase()

    if website_name:
        website_url = db.get_url(website_name)
        if website_url:
            # Initialize session state
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = [
                    AIMessage(content="Hello, How can I help you?"),
                ]
            if "vector_store" not in st.session_state:
                st.session_state.vector_store = get_vectorstore_from_url(website_url)

            # User input for conversation
            user_query = st.chat_input("Type your message here...")
            if user_query:
                with st.spinner('Fetching response...'):
                    response = get_response(user_query)
                    st.session_state.chat_history.append(HumanMessage(content=user_query))
                    st.session_state.chat_history.append(AIMessage(content=response))

            # Display the conversation history
            for message in st.session_state.chat_history:
                if isinstance(message, AIMessage):
                    with st.chat_message("AI"):
                        st.write(message.content)
                elif isinstance(message, HumanMessage):
                    with st.chat_message("Human"):
                        st.write(message.content)
        else:
            st.error("Website information not found")
    else:
        st.info("Please enter a website name to get started.")
