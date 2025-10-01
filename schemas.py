from pydantic import BaseModel
from typing import List, Optional

class AuthorBase(BaseModel):
    name: str
    bio: Optional[str] = None

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    id: int
    
    class Config:
        from_attributes = True

class BookBase(BaseModel):
    title: str
    description: Optional[str] = None
    author_id: int

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    author: Author
    reader_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class ReaderBase(BaseModel):
    name: str
    email: str

class ReaderCreate(ReaderBase):
    pass

class Reader(ReaderBase):
    id: int
    books_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class BookWithAuthor(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    author: Author
    reader_count: int
    
    class Config:
        from_attributes = True

class AuthorStats(BaseModel):
    id: int
    name: str
    total_readers: int
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    most_popular_author: AuthorStats
    user_books_read: int
    user_top_authors: List[AuthorStats]
