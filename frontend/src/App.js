import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('books');
  const [popularBooks, setPopularBooks] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [booksResponse, statsResponse] = await Promise.all([
        axios.get(`${API_BASE_URL}/books/popular`),
        axios.get(`${API_BASE_URL}/dashboard/stats`)
      ]);
      
      setPopularBooks(booksResponse.data);
      setDashboardStats(statsResponse.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch data. Make sure the backend server is running.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading">
          <div className="loading-spinner"></div>
          <p>Loading your reading data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <div className="error">
          <h2>⚠️ Connection Error</h2>
          <p>{error}</p>
          <button onClick={fetchData} className="retry-btn">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>📚 Book Reading Tracker</h1>
        <p>Discover, track, and explore your reading journey</p>
      </header>

      <nav className="tab-nav">
        <button 
          className={`tab ${activeTab === 'books' ? 'active' : ''}`}
          onClick={() => setActiveTab('books')}
        >
          📖 Popular Books
        </button>
        <button 
          className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Dashboard
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'books' && (
          <BooksSection books={popularBooks} />
        )}
        {activeTab === 'dashboard' && (
          <DashboardSection stats={dashboardStats} />
        )}
      </main>
    </div>
  );
}

function BooksSection({ books }) {
  return (
    <div className="books-section">
      <h2>Most Popular Books</h2>
      <p className="section-subtitle">Based on number of readers</p>
      
      <div className="books-grid">
        {books.map((book, index) => (
          <div key={book.id} className="book-card">
            <div className="book-rank">#{index + 1}</div>
            <div className="book-info">
              <h3 className="book-title">{book.title}</h3>
              <p className="book-author">by {book.author.name}</p>
              <p className="book-description">{book.description}</p>
              <div className="book-stats">
                <span className="reader-count">
                  👥 {book.reader_count} reader{book.reader_count !== 1 ? 's' : ''}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function DashboardSection({ stats }) {
  return (
    <div className="dashboard-section">
      <h2>Your Reading Dashboard</h2>
      <p className="section-subtitle">Personal reading statistics and insights</p>
      
      <div className="stats-grid">
        <div className="stat-card highlight">
          <div className="stat-icon">🏆</div>
          <div className="stat-info">
            <h3>Most Popular Author</h3>
            <p className="stat-value">{stats.most_popular_author.name}</p>
            <p className="stat-detail">
              {stats.most_popular_author.total_readers} total readers across all books
            </p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📚</div>
          <div className="stat-info">
            <h3>Books You've Read</h3>
            <p className="stat-value">{stats.user_books_read}</p>
            <p className="stat-detail">
              {stats.user_books_read === 0 
                ? "Start reading to see your progress!" 
                : "Keep up the great reading habit!"
              }
            </p>
          </div>
        </div>

        <div className="stat-card wide">
          <div className="stat-icon">⭐</div>
          <div className="stat-info">
            <h3>Your Top Authors</h3>
            {stats.user_top_authors.length > 0 ? (
              <div className="top-authors">
                {stats.user_top_authors.map((author, index) => (
                  <div key={author.id} className="author-item">
                    <span className="author-rank">#{index + 1}</span>
                    <div className="author-details">
                      <span className="author-name">{author.name}</span>
                      <span className="books-count">
                        {author.total_readers} book{author.total_readers !== 1 ? 's' : ''} read
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="stat-detail">No reading history yet. Start exploring books above!</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
