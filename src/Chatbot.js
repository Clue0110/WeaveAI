import React, { useState } from 'react';
import axios from 'axios';
import './Chatbot.css'; // create this file if it doesn't exist

function Chatbot() {
  const [recording, setRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioChunks, setAudioChunks] = useState([]);
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

  const handleStartRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      setMediaRecorder(recorder);
      const chunks = [];

      recorder.ondataavailable = event => chunks.push(event.data);
      recorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/mp3' });
        const formData = new FormData();
        formData.append('file', audioBlob, 'voice_input.mp3');

        try {
          const response = await axios.post('/voice_chat', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            responseType: 'blob'
          });

          const responseAudioUrl = URL.createObjectURL(response.data);
          const audio = new Audio(responseAudioUrl);
          audio.play();
        } catch (err) {
          console.error('Error sending voice input:', err);
        }
      };

      recorder.start();
      setAudioChunks(chunks);
      setRecording(true);

      setTimeout(() => {
        recorder.stop();
        setRecording(false);
      }, 5000); // 5 seconds recording

    } catch (err) {
      console.error('Microphone access error:', err);
    }
  };

  const handleTextQuery = async () => {
    if (!query.trim()) return;
    try {
      const res = await axios.get('/text_chat', {
        params: { q: query }
      });
      setChatHistory(prev => [...prev, { query, response: res.data.response }]);
      setQuery('');
    } catch (err) {
      console.error('Text query failed:', err);
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-card">
        <h2 className="chatbot-title">🤖 Weave AI</h2>
        <p className="chatbot-instruction">Click the mic to ask your question.</p>
        <button onClick={handleStartRecording} className="chatbot-mic-btn">🎤</button>
        {recording && <p className="chatbot-recording">Recording...</p>}

        <div className="chatbot-input-area">
          <input
            type="text"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Type your question"
            className="chatbot-input"
          />
          <button onClick={handleTextQuery} className="chatbot-send-btn">Send</button>
        </div>

        {chatHistory.length > 0 && (
          <div className="chatbot-response">
            {chatHistory.map((chat, index) => (
              <div key={index} style={{ marginBottom: '1.5em' }}>
                <p><strong>You:</strong> {chat.query}</p>
                <p><strong>AI:</strong> {chat.response}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Chatbot;