import axios from 'axios';
import { saveAs } from 'file-saver';
import './Course_content.css'
import { Clock, ChevronUp, ChevronDown, Play } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function CourseContent() {
  const [expandedModules, setExpandedModules] = useState([]);
  const [coursePlanData, setCoursePlanData] = useState({});
  const navigate = useNavigate();

  const toggleModule = (id) => {
    setExpandedModules(prev =>
      prev.includes(id) ? prev.filter(mid => mid !== id) : [...prev, id]
    );
  };

  useEffect(() => {
    const fetchCoursePlan = async () => {
      try {
        const response = await axios.get('/courseplan');
        setCoursePlanData(response.data.data);
      } catch (error) {
        console.error('Failed to fetch course plan:', error);
      }
    };
    fetchCoursePlan();
  }, []);

  return (
    <>
      <div className="navbar">
        <div className="navbar-container">
          <div className="navbar-logo">
            <span>📘</span> <strong>WeaveAI</strong>
          </div>
          <div className="navbar-links">
            <a href="#">Home</a>
            <a href="#">Courses</a>
            <a href="#">About</a>
            <a href="#">Contact</a>
            <button className="signup-btn">Sign Up</button>
          </div>
        </div>
      </div>
      <div className="course-hero">
        <div className="course-main-section">
          <div className="course-header">
            <a className="back-link" href="#">← Back to Courses</a>
            <div className="course-meta-top">
              <span className="level-badge">Beginner</span>
              <span className="star-rating">⭐ 4.8</span>
            </div>
            <h1 className="course-title">Depth-First Search (DFS)</h1>
            <p className="course-description">
              Learn the fundamentals of DFS, a graph algorithm, which is widely used for solving many Graph related problems. It also forms a base for advanced data structures like Tree.
            </p>
            <div className="course-stats">
              <span>📚 3 modules</span>
              <span>⏱ 7h 5m</span>
              <span>👥 1,245 students</span>
            </div>
          </div>

          <div className="course-side-card">
            <button className="enroll-btn">Start now</button>
            <button className="preview-btn">Scroll to the bottom to begin your learning</button>
            <div className="course-includes">
              <h4>This course includes:</h4>
              <ul>
                <li>✅ 9 on-demand lessons</li>
                <li>✅ 7h 5m of video content</li>
                <li>✅ Access on mobile and desktop</li>
                <li>✅ Lifetime access</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <div className="course-details-section">
        <div className="course-info-layout">
          <div className="about-this-course">
            <h3>About This Course</h3>
            <p>
              Learn the fundamentals of Graphs, building Graphs, using graphs to solve real world problems and algorithms like DFS. This comprehensive course is
              designed to take you from beginner to proficient, with real-world applications.
            </p>
            <div className="info-boxes">
              <div className="what-you-learn">
                <h4>What you'll learn</h4>
                <ul>
                  <li>✅ Master fundamental concepts and principles</li>
                  <li>✅ Apply theoretical knowledge to practical scenarios</li>
                  <li>✅ Understand industry best practices</li>
                </ul>
              </div>
              <div className="requirements">
                <h4>Requirements</h4>
                <ul>
                  <li>• Basic understanding of the subject area</li>
                  <li>• Computer with internet connection</li>
                  <li>• Eagerness to learn and apply concepts</li>
                </ul>
              </div>
            </div>
          </div>

        </div>

        
      </div>
      <div className="course-content-section">
        <h2>Course Content</h2>
        <p className="course-summary">3 modules • 9 lessons • 7h 5m total length</p>
        {Object.entries(coursePlanData).map(([moduleId, module]) => (
          <div key={moduleId} className={`module ${expandedModules.includes(moduleId) ? 'expanded' : ''}`}>
            <div className="module-header" onClick={() => toggleModule(moduleId)}>
              <div className="module-index">{module.module_number}</div>
              <div className="module-title">{module.module_title}</div>
              <div className="module-duration">
                {expandedModules.includes(moduleId) ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </div>
            </div>
            {expandedModules.includes(moduleId) && (
              <div className="module-lessons">
                {Object.entries(module.submodules).map(([subId, lesson]) => (
                  <div key={subId} className="lesson">
                    <Play size={16} />
                    <span className="lesson-title">{lesson.module_title}</span>
                    <div className="lesson-actions">
                      <button
                        className="quiz-btn"
                        onClick={async () => {
                            navigate('/quiz', {
                              state: {
                                module: module.module_number,
                                submodule: lesson.module_number
                              }
                            });
                        }}
                      >
                        Quiz
                      </button>
                      <button
                        className="podcast-btn"
                        onClick={async () => {
                          try {
                            console.log("Fine0")
                            const response = await axios.post('/podcast', {
                                module: module.module_number,
                                submodule: lesson.module_number},{
                              responseType: 'blob'}
                            );
                            console.log("Fine1")
                            const filename = `podcast_module${module.module_number}_submodule${lesson.module_number}.mp3`;
                            console.log("Fine2")
                            console.log(response.data)
                            saveAs(response.data, filename);
                          } catch (error) {
                            console.error('Podcast download failed:', error);
                          }
                        }}
                      >
                        Podcast
                      </button>
                      <button
                        className="view-content-btn"
                        onClick={() => navigate('/content', {
                          state: {
                            module: module.module_number,
                            submodule: lesson.module_number
                          }
                        })}
                      >
                        View Content
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    <div style={{ position: 'fixed', bottom: '90px', right: '30px' }}>
      <button
        className="chatbot-page-btn"
        onClick={() => navigate('/chatbot')}
      >
        Click here for Chatbot
      </button>
    </div>
    </>
  );
}

export default CourseContent;