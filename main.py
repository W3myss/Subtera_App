from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
import os

from database import create_tables, get_db, SessionLocal
from database import Author as DBAuthor, Book as DBBook, Reader as DBReader, book_reader
from schemas import (
    Author, AuthorCreate, Book, BookCreate, Reader, ReaderCreate,
    BookWithAuthor, AuthorStats, DashboardStats
)

app = FastAPI(title="Book Reading App", description="A simple book reading tracking system")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()
    # Initialize sample data if database is empty
    init_sample_data()

def init_sample_data():
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(DBAuthor).first():
            return
            
        # Create sample authors
        authors_data = [
            {"name": "J.K. Rowling", "bio": "British author, best known for Harry Potter series"},
            {"name": "George R.R. Martin", "bio": "American novelist and short story writer"},
            {"name": "Stephen King", "bio": "American author of horror, supernatural fiction"},
            {"name": "Agatha Christie", "bio": "English writer known for detective novels"},
            {"name": "Isaac Asimov", "bio": "American writer and professor of biochemistry"}
        ]
        
        authors = []
        for author_data in authors_data:
            author = DBAuthor(**author_data)
            db.add(author)
            authors.append(author)
        
        db.commit()
        
        # Refresh authors to get IDs
        for author in authors:
            db.refresh(author)
        
        # Create sample books
        books_data = [
            {"title": "Harry Potter and the Philosopher's Stone", "description": "First book in the Harry Potter series", "author_id": authors[0].id},
            {"title": "Harry Potter and the Chamber of Secrets", "description": "Second book in the Harry Potter series", "author_id": authors[0].id},
            {"title": "A Game of Thrones", "description": "First book in A Song of Ice and Fire series", "author_id": authors[1].id},
            {"title": "A Clash of Kings", "description": "Second book in A Song of Ice and Fire series", "author_id": authors[1].id},
            {"title": "The Shining", "description": "Horror novel about the Overlook Hotel", "author_id": authors[2].id},
            {"title": "It", "description": "Horror novel about a shape-shifting entity", "author_id": authors[2].id},
            {"title": "Murder on the Orient Express", "description": "Classic detective novel featuring Hercule Poirot", "author_id": authors[3].id},
            {"title": "And Then There Were None", "description": "Mystery novel about ten strangers on an island", "author_id": authors[3].id},
            {"title": "Foundation", "description": "Science fiction novel about psychohistory", "author_id": authors[4].id},
            {"title": "I, Robot", "description": "Collection of science fiction short stories", "author_id": authors[4].id}
        ]
        
        books = []
        for book_data in books_data:
            book = DBBook(**book_data)
            db.add(book)
            books.append(book)
        
        db.commit()
        
        # Refresh books to get IDs
        for book in books:
            db.refresh(book)
        
        # Create sample readers
        readers_data = [
            {"name": "Alice Johnson", "email": "alice@example.com"},
            {"name": "Bob Smith", "email": "bob@example.com"},
            {"name": "Charlie Brown", "email": "charlie@example.com"},
            {"name": "Diana Prince", "email": "diana@example.com"},
            {"name": "Eve Wilson", "email": "eve@example.com"}
        ]
        
        readers = []
        for reader_data in readers_data:
            reader = DBReader(**reader_data)
            db.add(reader)
            readers.append(reader)
        
        db.commit()
        
        # Refresh readers to get IDs
        for reader in readers:
            db.refresh(reader)
        
        # Create sample reading relationships
        reading_relationships = [
            # Alice reads Harry Potter books and Agatha Christie
            (readers[0].id, books[0].id), (readers[0].id, books[1].id), (readers[0].id, books[6].id), (readers[0].id, books[7].id),
            # Bob reads Game of Thrones and Stephen King
            (readers[1].id, books[2].id), (readers[1].id, books[3].id), (readers[1].id, books[4].id), (readers[1].id, books[5].id),
            # Charlie reads Asimov and Harry Potter
            (readers[2].id, books[8].id), (readers[2].id, books[9].id), (readers[2].id, books[0].id),
            # Diana reads everything by J.K. Rowling and Agatha Christie
            (readers[3].id, books[0].id), (readers[3].id, books[1].id), (readers[3].id, books[6].id), (readers[3].id, books[7].id),
            # Eve reads Stephen King and Asimov
            (readers[4].id, books[4].id), (readers[4].id, books[5].id), (readers[4].id, books[8].id), (readers[4].id, books[9].id),
            # Additional reads to make Harry Potter most popular
            (readers[1].id, books[0].id), (readers[2].id, books[1].id), (readers[4].id, books[0].id)
        ]
        
        for reader_id, book_id in reading_relationships:
            # Check if relationship already exists
            existing = db.query(book_reader).filter_by(reader_id=reader_id, book_id=book_id).first()
            if not existing:
                db.execute(book_reader.insert().values(reader_id=reader_id, book_id=book_id))
        
        db.commit()
        
    finally:
        db.close()

# API Routes

@app.get("/")
def read_root():
    return {"message": "Book Reading App API", "status": "active"}

@app.get("/books/popular", response_model=List[BookWithAuthor])
def get_popular_books(limit: int = 10, db: Session = Depends(get_db)):
    """Get most popular books based on number of readers"""
    books = db.query(
        DBBook,
        func.count(book_reader.c.reader_id).label('reader_count')
    ).join(
        book_reader, DBBook.id == book_reader.c.book_id, isouter=True
    ).join(
        DBAuthor, DBBook.author_id == DBAuthor.id
    ).group_by(
        DBBook.id
    ).order_by(
        desc('reader_count')
    ).limit(limit).all()
    
    result = []
    for book, reader_count in books:
        book_dict = {
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "author": {
                "id": book.author.id,
                "name": book.author.name,
                "bio": book.author.bio
            },
            "reader_count": reader_count or 0
        }
        result.append(book_dict)
    
    return result

@app.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics for the logged-in user (first reader)"""
    # Get first reader (simulated logged-in user)
    current_user = db.query(DBReader).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="No users found")
    
    # Most popular author (based on total readers across all their books)
    most_popular_author = db.query(
        DBAuthor,
        func.count(book_reader.c.reader_id).label('total_readers')
    ).join(
        DBBook, DBAuthor.id == DBBook.author_id
    ).join(
        book_reader, DBBook.id == book_reader.c.book_id, isouter=True
    ).group_by(
        DBAuthor.id
    ).order_by(
        desc('total_readers')
    ).first()
    
    # User's total books read
    user_books_count = db.query(func.count(book_reader.c.book_id)).filter(
        book_reader.c.reader_id == current_user.id
    ).scalar()
    
    # User's top 3 authors (based on number of books read by this user)
    user_top_authors = db.query(
        DBAuthor,
        func.count(book_reader.c.book_id).label('books_read')
    ).join(
        DBBook, DBAuthor.id == DBBook.author_id
    ).join(
        book_reader, DBBook.id == book_reader.c.book_id
    ).filter(
        book_reader.c.reader_id == current_user.id
    ).group_by(
        DBAuthor.id
    ).order_by(
        desc('books_read')
    ).limit(3).all()
    
    return DashboardStats(
        most_popular_author=AuthorStats(
            id=most_popular_author[0].id,
            name=most_popular_author[0].name,
            total_readers=most_popular_author[1] or 0
        ) if most_popular_author else AuthorStats(id=0, name="No data", total_readers=0),
        user_books_read=user_books_count or 0,
        user_top_authors=[
            AuthorStats(
                id=author.id,
                name=author.name,
                total_readers=books_read
            ) for author, books_read in user_top_authors
        ]
    )

@app.get("/authors/", response_model=List[Author])
def get_authors(db: Session = Depends(get_db)):
    return db.query(DBAuthor).all()

@app.post("/authors/", response_model=Author)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    db_author = DBAuthor(**author.dict())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author

@app.get("/books/", response_model=List[Book])
def get_books(db: Session = Depends(get_db)):
    return db.query(DBBook).all()

@app.post("/books/", response_model=Book)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = DBBook(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/readers/", response_model=List[Reader])
def get_readers(db: Session = Depends(get_db)):
    return db.query(DBReader).all()

@app.post("/readers/", response_model=Reader)
def create_reader(reader: ReaderCreate, db: Session = Depends(get_db)):
    db_reader = DBReader(**reader.dict())
    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    return db_reader

# Serve React static files (for production)
if os.path.exists("frontend/build"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
    app.mount("/", StaticFiles(directory="frontend/build", html=True), name="frontend")