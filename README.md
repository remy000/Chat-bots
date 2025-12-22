# 🏋️‍♀️ Fitness & Nutrition Chatbot 🥗

An AI-powered chatbot that provides personalized fitness and nutrition advice using FastAPI, React.js, and RAG (Retrieval-Augmented Generation) technology.

## ✨ Features

- 💬 **Smart Chat Interface**: Ask questions about fitness, nutrition, and health
- 🎯 **Personalized Recommendations**: Tailored advice based on your profile
- 📚 **Knowledge Base**: Powered by fitness and nutrition documents
- 🔍 **RAG System**: Retrieves relevant information for accurate responses
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 👤 **User Profiles**: Save your fitness goals and dietary preferences

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **LangChain**: RAG implementation and LLM integration
- **ChromaDB**: Vector database for document storage
- **OpenAI**: GPT-4o-mini for chat responses

### Frontend
- **React.js**: Interactive user interface
- **Axios**: API communication
- **CSS3**: Modern styling with gradients and animations

## 📁 Project Structure

```
fitness-nutrition-chatbot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py          # Pydantic models
│   │   └── rag_system.py      # RAG implementation
│   ├── main.py                # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── index.js          # React entry point
│   │   └── index.css         # Styling
│   ├── public/
│   │   └── index.html        # HTML template
│   └── package.json          # Node dependencies
├── knowledge_base/
│   ├── beginner_workouts.txt # Workout routines
│   ├── nutrition_basics.txt  # Nutrition information
│   └── meal_ideas.txt        # Meal planning and recipes
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
copy .env.example .env
# Edit .env file with your OpenAI API key

# Run the backend
python main.py
```

The backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will be available at `http://localhost:3000`

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://ai-gateway.andrew.cmu.edu/
CHROMA_PERSIST_DIRECTORY=./chroma_db
HOST=localhost
PORT=8000
DEBUG=True
```

### Knowledge Base

The system uses documents in the `knowledge_base/` directory:

- `beginner_workouts.txt`: Exercise routines and workout plans
- `nutrition_basics.txt`: Nutritional information and guidelines
- `meal_ideas.txt`: Healthy recipes and meal planning tips

You can add more `.txt` files to expand the knowledge base.

## 🎯 Usage Examples

### Sample Questions to Ask:

**Fitness:**
- "Can you create a beginner workout plan for me?"
- "What exercises can I do at home without equipment?"
- "How many calories should I burn during cardio?"

**Nutrition:**
- "What should I eat after a workout?"
- "Can you suggest a meal plan for weight loss?"
- "How much protein do I need daily?"

**Meal Planning:**
- "Give me healthy breakfast ideas"
- "What are some quick lunch recipes?"
- "How do I meal prep for the week?"

## 🏗️ API Endpoints

### POST /chat
Send a message to the chatbot
```json
{
  "message": "What's a good workout for beginners?",
  "user_profile": {
    "age": 25,
    "fitness_level": "beginner",
    "fitness_goals": ["weight_loss"]
  }
}
```

### POST /profile
Update user profile
```json
{
  "age": 25,
  "weight": 70,
  "height": 175,
  "fitness_level": "beginner"
}
```

### GET /recommendations/{category}
Get recommendations for fitness or nutrition

## 🔧 Development

### Adding New Knowledge

1. Create new `.txt` files in `knowledge_base/`
2. Restart the backend to rebuild the vector database
3. The RAG system will automatically index new content

### Customizing the UI

- Edit `frontend/src/App.js` for component logic
- Modify `frontend/src/index.css` for styling
- Update colors, fonts, and layout as needed

### Extending the Backend

- Add new endpoints in `main.py`
- Create new models in `app/models.py`
- Enhance RAG functionality in `app/rag_system.py`

## 🧪 Testing

### Backend Testing
```bash
cd backend
# Test the API endpoints
curl http://localhost:8000/
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"message": "Hello"}'
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📦 Deployment

### Backend Deployment
- Use Docker for containerization
- Deploy to cloud platforms (AWS, GCP, Azure)
- Set up environment variables in production

### Frontend Deployment
- Build the React app: `npm run build`
- Deploy to static hosting (Netlify, Vercel, AWS S3)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.8+)
- Verify OpenAI API key is set
- Ensure all dependencies are installed

**Frontend connection error:**
- Verify backend is running on port 8000
- Check CORS settings in FastAPI
- Confirm proxy setting in package.json

**RAG system not working:**
- Ensure knowledge base files exist
- Check ChromaDB permissions
- Verify OpenAI API key has embedding access

### Getting Help

- Check the API documentation at `http://localhost:8000/docs`
- Review the browser console for frontend errors
- Check backend logs for detailed error messages

## 🎉 Next Steps

- Add user authentication and data persistence
- Integrate with fitness tracking APIs
- Add image upload for food recognition
- Implement progress tracking and analytics
- Add voice chat capabilities
- Create mobile app version

Happy coding! 🚀