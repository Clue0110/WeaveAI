import React, { useState } from 'react';
import './Dashboard.css'; 

function Dashboard() {
  const [searchQuery, setSearchQuery] = useState("");
  const courses = [
    {
      title: "User Experience Design Fundamentals",
      author: "Sarah Johnson",
      desc: "Learn the fundamentals of UX design, including research methods, wireframing, and prototyping...",
      rating: "4.8",
      students: "1,245",
      duration: "7h 5m",
      price: "$89.99",
      level: "beginner"
    },
    {
      title: "Interactive Web Animation with CSS and JS",
      author: "Michael Chen",
      desc: "Master the art of web animations using CSS and JavaScript...",
      rating: "4.7",
      students: "982",
      duration: "5h 25m",
      price: "$79.99",
      level: "intermediate"
    },
    {
      title: "Human-Computer Interaction Principles",
      author: "David Williams",
      desc: "Dive into the theory and practice of HCI. Understand how humans interact with technology...",
      rating: "4.9",
      students: "645",
      duration: "5h 45m",
      price: "$99.99",
      level: "advanced"
    }
  ];

  const filter = "all"; // Assuming filter is "all" as no filter state is defined
  const filteredCourses = courses.filter(course => {
    const levelMatch = filter === "all" || course.level === filter;
    const titleMatch = course.title.toLowerCase().includes(searchQuery.toLowerCase());
    return levelMatch && titleMatch;
  });

  return (
    <div className="dashboard">
      <header className="header">
        <div className="logo">📖 LearnHub</div>
        <nav className="nav-links">
          <a href="#">Home</a>
          <a href="#">Courses</a>
          <a href="#">About</a>
          <a href="#">Contact</a>
        </nav>
        <div className="header-actions">
          <button className="search-icon">🔍</button>
          <button className="user-icon">👤</button>
          <button className="signup-btn">Sign Up</button>
        </div>
      </header>

      <section className="hero">
        <h1>Unlock Your Potential with Expert-Led Online Courses</h1>
        <p>Discover courses designed to elevate your skills and advance your career</p>
        <div className="search-bar">
          <input
            type="text"
            placeholder="What do you want to learn?"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button>Search</button>
        </div>
      </section>

      <section className="popular-courses">
        <div className="popular-header">
          <div>
            <h2>Popular Courses</h2>
            <p>Explore our most sought-after courses</p>
          </div>
          <button className="all-categories-btn">All Categories</button>
        </div>

        <div className="courses-list">
          {filteredCourses.map((course, index) => (
            <div key={index} className="course-card">
              <div className={`course-image ${course.level}`}></div>
              <div className="course-info">
                <h3>{course.title}</h3>
                <p>by {course.author}</p>
                <p className="course-desc">{course.desc}</p>
                <div className="course-meta">
                  <span>⭐ {course.rating}</span>
                  <span>👥 {course.students}</span>
                  <span>⏱️ {course.duration}</span>
                </div>
                <div className="course-footer">
                  <span className="price">{course.price}</span>
                  <button
                    className="view-course-btn"
                    onClick={() => window.location.href = '/course_content'}
                  >
                    View Course
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
