import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './index.css';

const App = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your fitness and nutrition assistant. I can help you with workout routines, meal planning, nutrition advice, and answer any health-related questions. How can I help you today?'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [userProfile, setUserProfile] = useState({
    age: '',
    weight: '',
    height: '',
    fitness_level: '',
    fitness_goals: [],
    dietary_preferences: [],
    activity_level: ''
  });
  const [showProfile, setShowProfile] = useState(false);
  
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = { role: 'user', content: inputMessage };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    
    try {
      const response = await axios.post('/chat', {
        message: inputMessage,
        user_profile: userProfile.age ? userProfile : null,
        conversation_history: messages.slice(-5) // Last 5 messages for context
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        recommendations: response.data.recommendations || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again later.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setInputMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const updateProfile = (field, value) => {
    setUserProfile(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleGoalChange = (goal, checked) => {
    setUserProfile(prev => ({
      ...prev,
      fitness_goals: checked 
        ? [...prev.fitness_goals, goal]
        : prev.fitness_goals.filter(g => g !== goal)
    }));
  };

  const handleDietChange = (diet, checked) => {
    setUserProfile(prev => ({
      ...prev,
      dietary_preferences: checked 
        ? [...prev.dietary_preferences, diet]
        : prev.dietary_preferences.filter(d => d !== diet)
    }));
  };

  return (
    <div className="container">
      <h1 className="main-title">
        🏋️‍♀️ Fitness & Nutrition Assistant 🥗
      </h1>
      
      {/* Profile Section */}
      <div className="profile-section">
        <div className="profile-header">
          <h3>Personal Profile (Optional - for better recommendations)</h3>
          <button 
            className="profile-toggle-btn"
            onClick={() => setShowProfile(!showProfile)}
          >
            {showProfile ? 'Hide Profile' : 'Setup Profile'}
          </button>
        </div>
        
        {showProfile && (
          <div className="profile-form">
            <div className="form-group">
              <label>Age</label>
              <input
                type="number"
                value={userProfile.age}
                onChange={(e) => updateProfile('age', e.target.value)}
                placeholder="Enter your age"
              />
            </div>
            
            <div className="form-group">
              <label>Weight (kg)</label>
              <input
                type="number"
                value={userProfile.weight}
                onChange={(e) => updateProfile('weight', e.target.value)}
                placeholder="Enter your weight"
              />
            </div>
            
            <div className="form-group">
              <label>Height (cm)</label>
              <input
                type="number"
                value={userProfile.height}
                onChange={(e) => updateProfile('height', e.target.value)}
                placeholder="Enter your height"
              />
            </div>
            
            <div className="form-group">
              <label>Fitness Level</label>
              <select
                value={userProfile.fitness_level}
                onChange={(e) => updateProfile('fitness_level', e.target.value)}
              >
                <option value="">Select fitness level</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Activity Level (1-5)</label>
              <select
                value={userProfile.activity_level}
                onChange={(e) => updateProfile('activity_level', e.target.value)}
              >
                <option value="">Select activity level</option>
                <option value="1">1 - Sedentary</option>
                <option value="2">2 - Lightly Active</option>
                <option value="3">3 - Moderately Active</option>
                <option value="4">4 - Very Active</option>
                <option value="5">5 - Extremely Active</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Fitness Goals</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
                {['weight_loss', 'muscle_gain', 'strength', 'endurance', 'general_fitness'].map(goal => (
                  <label key={goal} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'normal' }}>
                    <input
                      type="checkbox"
                      checked={userProfile.fitness_goals.includes(goal)}
                      onChange={(e) => handleGoalChange(goal, e.target.checked)}
                    />
                    {goal.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </label>
                ))}
              </div>
            </div>
            
            <div className="form-group">
              <label>Dietary Preferences</label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '8px' }}>
                {['omnivore', 'vegetarian', 'vegan', 'keto', 'paleo', 'mediterranean'].map(diet => (
                  <label key={diet} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'normal' }}>
                    <input
                      type="checkbox"
                      checked={userProfile.dietary_preferences.includes(diet)}
                      onChange={(e) => handleDietChange(diet, e.target.checked)}
                    />
                    {diet.charAt(0).toUpperCase() + diet.slice(1)}
                  </label>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Chat Interface */}
      <div className="chat-container">
        <div className="chat-header">
          <h2>💬 Chat with Your Fitness Assistant</h2>
          <p>Ask me about workouts, nutrition, meal planning, or any health questions!</p>
        </div>
        
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-content">
                <div style={{ whiteSpace: 'pre-wrap' }}>
                  {message.content}
                </div>
                
                {message.recommendations && message.recommendations.length > 0 && (
                  <div className="recommendations">
                    <h4>💡 Recommendations for you:</h4>
                    {message.recommendations.map((rec, recIndex) => (
                      <div key={recIndex} className="recommendation-item">
                        <div className="recommendation-title">{rec.title}</div>
                        <div className="recommendation-description">{rec.description}</div>
                        {rec.duration && <div style={{ fontSize: '12px', color: '#888', marginTop: '5px' }}>Duration: {rec.duration}</div>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="loading">
                  <span>Assistant is typing</span>
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        <div className="chat-input-container">
          <input
            type="text"
            className="chat-input"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about workouts, nutrition, meal plans..."
            disabled={isLoading}
          />
          <button
            className="send-button"
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;