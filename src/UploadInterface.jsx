import React, { useState } from 'react';
import axios from 'axios';
import './UploadInterface.css';
import { Youtube, FileArchive, PlusCircle, Trash2, UploadCloud } from 'lucide-react'; // Import Lucide icons
import { useNavigate } from 'react-router-dom';

const UploadInterface = () => {
  const [youtubeLinks, setYoutubeLinks] = useState(['']);
  const [zipFile, setZipFile] = useState(null);
  const navigate = useNavigate();

  const handleAddLink = () => {
    setYoutubeLinks([...youtubeLinks, '']);
  };

  const handleLinkChange = (index, value) => {
    const newLinks = [...youtubeLinks];
    newLinks[index] = value;
    setYoutubeLinks(newLinks);
  };

  const handleRemoveLink = (index) => {
    const newLinks = youtubeLinks.filter((_, i) => i !== index);
    // Ensure there's always at least one input field
    if (newLinks.length === 0) {
        setYoutubeLinks(['']);
    } else {
        setYoutubeLinks(newLinks);
    }
  };

  const handleZipChange = (event) => {
    if (event.target.files && event.target.files[0]) {
      setZipFile(event.target.files[0]);
    }
  };

  const handleRemoveZip = () => {
    setZipFile(null);
    // Reset the file input
    const fileInput = document.getElementById('zip-upload-input');
    if (fileInput) {
        fileInput.value = '';
    }
  };

  const handleSubmit = async () => {
    const payload = {
      resource_list: youtubeLinks.map((url) => ({ url }))
    };

    try {
      console.log(payload);
      await axios.post('/add_resource', payload);
      console.log('Added resource links:');

      await axios.post('/trigger_course_plan', {});
      console.log('CoursePlan triggered');

      await axios.post('/setup_course', {});
      console.log('setup_course triggered');

      await axios.post('/content', {});
      console.log('content triggered');

      
      // alert('All API calls completed successfully!');
      navigate('/');
    } catch (error) {
      if (error.response) {
        console.error('Server responded with an error:', error.response.data);
      } else if (error.request) {
        console.error('No response received:', error.request);
      } else {
        console.error('Axios config error:', error.message);
      }
      alert('There was an error submitting your content. Please try again.');
    }
  };

  return (
    <div className="upload-container">
      <h2>Upload Your Content</h2>

      {/* YouTube Links Section */}
      <div className="upload-section youtube-section">
        <div className="section-header">
          <Youtube size={24} className="icon" />
          <h3>YouTube Links</h3>
        </div>
        {youtubeLinks.map((link, index) => (
          <div key={index} className="input-group">
            <input
              type="url"
              placeholder="https://www.youtube.com/watch?v=..."
              value={link}
              onChange={(e) => handleLinkChange(index, e.target.value)}
            />
            {youtubeLinks.length > 1 && (
              <button onClick={() => handleRemoveLink(index)} className="remove-btn">
                <Trash2 size={16} /> {/* Use Lucide icon */}
              </button>
            )}
          </div>
        ))}
        <button onClick={handleAddLink} className="add-btn">
          <PlusCircle size={18} /> {/* Use Lucide icon */} Add More Links
        </button>
      </div>

      {/* Zip File Upload Section */}
      <div className="upload-section zip-section">
        <div className="section-header">
          <FileArchive size={24} className="icon" /> {/* Use Lucide icon */}
          <h3>Zip Contents</h3>
        </div>
        {!zipFile ? (
            <label htmlFor="zip-upload-input" className="zip-upload-label">
                <input
                id="zip-upload-input"
                type="file"
                accept=".zip"
                onChange={handleZipChange}
                style={{ display: 'none' }} // Hide default input
                />
                <UploadCloud size={32} className="upload-icon"/> 
                <span>Click or Drag to Upload .zip File</span>
            </label>
        ) : (
            <div className="file-info">
                <FileArchive size={20} className="icon file-icon"/> 
                <span>{zipFile.name}</span>
                <button onClick={handleRemoveZip} className="remove-btn">
                    <Trash2 size={16} /> 
                </button> 
            </div>
        )}
      </div>

      <button className="submit-btn" onClick={handleSubmit}>Submit</button>
    </div>
  );
};

export default UploadInterface;