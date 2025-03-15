import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client["library_db"]  
collection = db["books"]   

# Custom CSS for better UI
st.markdown("""
    <style>
        body, .stApp { background-color: white !important; }
        .stApp { background-color: #ffffff; border-radius: 10px; padding: 20px; }
        .stDataFrame { background-color: #f9f9f9; border-radius: 10px; padding: 10px; }
        .stButton>button { background-color: #FFDF00 !important; color: white !important; border-radius: 5px; }
        .sidebar .sidebar-content { background-color: rgba(255, 223, 0, 0.9); padding: 20px; border-radius: 10px; }
        
    </style>
""", unsafe_allow_html=True)

# Streamlit UI
st.title("📚 Personal Library Manager")

# Add an image below the title
st.image("https://images.pexels.com/photos/207607/pexels-photo-207607.jpeg?auto=compress&cs=tinysrgb&w=600", use_container_width=True)

st.markdown('<h3 style="color: #FFDF00;">Manage and track your books easily!</h3>', unsafe_allow_html=True)


# Sidebar for Adding Books
st.sidebar.header("📌 Add a New Book")
book_title = st.sidebar.text_input("Enter Book Title")
author_name = st.sidebar.text_input("Enter Author Name")
publication_year = st.sidebar.number_input("Publication Year", min_value=1800, max_value=2100, value=2024, step=1)
genre = st.sidebar.text_input("Enter Genre")
progress = st.sidebar.slider("Read Progress (%)", 0, 100, 0)

if st.sidebar.button("Add Book"):
    if book_title and author_name and genre:
        collection.insert_one({"title": book_title, "author": author_name, "publication_year": publication_year, "genre": genre, "progress": progress})
        st.sidebar.success(f"Added {book_title} by {author_name}")
    else:
        st.sidebar.warning("Please enter all details!")

# Search Books
st.subheader("🔍 Search for a Book")
search_query = st.text_input("Enter book title, author name, or genre")
if st.button("Search Book"):
    search_results = list(collection.find({
        "$or": [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"author": {"$regex": search_query, "$options": "i"}},
            {"genre": {"$regex": search_query, "$options": "i"}}
        ]
    }))
    if search_results:
        search_df = pd.DataFrame(search_results)[["title", "author", "publication_year", "genre", "progress"]]
        st.dataframe(search_df, use_container_width=True)
    else:
        st.warning("No matching books found.")

# Show Books
st.subheader("📖 Library Collection")
books = list(collection.find())

if books:
    df = pd.DataFrame(books)
    df = df[["title", "author", "publication_year", "genre", "progress"]]  
    st.dataframe(df, use_container_width=True)

    # Delete Book
    st.subheader("🗑️ Delete a Book")
    book_to_delete = st.selectbox("Select a book to delete", df["title"].tolist())
    if st.button("Delete Book"):
        collection.delete_one({"title": book_to_delete})
        st.success(f"Deleted {book_to_delete}")

    # Analytics
    st.subheader("📊 Reading Progress Analytics")
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.hist(df["progress"], bins=10, color='#FFDF00')
    ax.set_xlabel("Read Percentage")
    ax.set_ylabel("Number of Books")
    ax.set_title("Distribution of Reading Progress")
    st.pyplot(fig)
else:
    st.info("No books found. Add some books to start tracking!")
