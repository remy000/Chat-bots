import os
import asyncio
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

from app.models import UserProfile, HealthRecommendation

load_dotenv()

class RAGSystem:
    def __init__(self):
        self.llm = None
        self.embeddings = None
        self.vectorstore = None
        self.qa_chain = None
        self.knowledge_base_path = "../knowledge_base"
        self.persist_directory = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
        
    async def initialize(self):
        """Initialize the RAG system components"""
        try:
            # Initialize LLM
            self.llm = ChatOpenAI(
                model="gpt-4o-mini-2024-07-18",
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL", "https://ai-gateway.andrew.cmu.edu/"),
                temperature=0.7
            )
            
            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(
                model="azure/text-embedding-3-small",
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL", "https://ai-gateway.andrew.cmu.edu/")
            )
            
            # Load or create vector store
            await self._setup_vectorstore()
            
            # Create QA chain
            self._setup_qa_chain()
            
            print("RAG System initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing RAG system: {e}")
            raise e
    
    async def _setup_vectorstore(self):
        """Setup the vector store with fitness and nutrition documents"""
        try:
            # Check if vector store already exists
            if os.path.exists(self.persist_directory):
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                print("Loaded existing vector store")
            else:
                # Create new vector store from documents
                await self._create_vectorstore()
                
        except Exception as e:
            print(f"Error setting up vector store: {e}")
            # Fallback: create empty vector store
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
    
    async def _create_vectorstore(self):
        """Create vector store from knowledge base documents"""
        print("Creating new vector store from documents...")
        
        # Load documents from knowledge base
        if os.path.exists(self.knowledge_base_path):
            loader = DirectoryLoader(
                self.knowledge_base_path,
                glob="**/*.txt",
                loader_cls=TextLoader
            )
            documents = loader.load()
            
            if documents:
                # Split documents into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )
                texts = text_splitter.split_documents(documents)
                
                # Create vector store
                self.vectorstore = Chroma.from_documents(
                    documents=texts,
                    embedding=self.embeddings,
                    persist_directory=self.persist_directory
                )
                self.vectorstore.persist()
                print(f"Created vector store with {len(texts)} document chunks")
            else:
                print("No documents found in knowledge base")
        else:
            print("Knowledge base directory not found")
            
        # Create empty vector store if no documents
        if not self.vectorstore:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
    
    def _setup_qa_chain(self):
        """Setup the question-answering chain"""
        
        # Create a custom prompt template for better formatting
        prompt_template = """You are a professional fitness and nutrition expert. Use the following context to provide a well-structured, helpful answer.

Context:
{context}

Question: {question}

Please provide a clear, well-organized answer that includes:
1. A direct response to the question
2. Key points organized with bullet points or numbers when appropriate
3. Practical advice or recommendations
4. Any important considerations or warnings if relevant

Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Use custom prompt with RetrievalQA
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    
    def _is_greeting_or_simple_message(self, query: str) -> bool:
        """Check if the message is a greeting or simple conversation"""
        query_lower = query.lower().strip()
        
        # Exact phrase matches (greetings, farewells, acknowledgments)
        exact_phrases = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
            'how are you', 'how\'s it going', 'how is it going', 'what\'s up', 'whats up', 'sup', 'yo', 'greetings',
            'how is your day', 'how\'s your day', 'how was your day', 'how is the day', 'how\'s the day',
            'how is today', 'how\'s today', 'how are things', 'how\'s everything',
            'thanks', 'thank you', 'thank u', 'thx', 'ty',
            'bye', 'goodbye', 'see you', 'see ya', 'later', 'cya', 'farewell',
            'ok', 'okay', 'alright', 'sure', 'yep', 'yeah', 'yes', 'no', 'nope',
            'cool', 'nice', 'great', 'awesome', 'amazing', 'wonderful', 'perfect',
            'wow', 'omg', 'lol', 'haha', 'lmao', 'hehe',
            'good', 'bad', 'fine', 'excellent', 'fantastic',
            'sorry', 'excuse me', 'pardon', 'my bad',
            'welcome', 'congrats', 'congratulations',
            'please', 'help', 'assist'
        ]
        
        # Casual expressions and small talk
        casual_expressions = [
            'i am satisfied', 'am satisfied', 'i\'m satisfied', 
            'i am done', 'am done', 'i\'m done', 'i am good', 'am good', 'i\'m good',
            'i am fine', 'am fine', 'i\'m fine', 'i am ok', 'am ok', 'i\'m ok',
            'how\'s it going', 'how is it going', 'what\'s new', 'whats new',
            'how is the day', 'how\'s the day', 'how was your day', 'how\'s your day',
            'how is today', 'how\'s today', 'how are things', 'how\'s everything',
            'nice to meet you', 'pleased to meet you', 'good to see you',
            'have a good day', 'have a nice day', 'take care', 'stay safe',
            'i understand', 'i see', 'i get it', 'makes sense', 'got it',
            'no problem', 'no worries', 'all good', 'sounds good',
            'i agree', 'exactly', 'absolutely', 'definitely', 'for sure',
            'maybe', 'perhaps', 'probably', 'possibly',
            'interesting', 'that\'s cool', 'thats cool', 'i like that',
            'whatever', 'nevermind', 'forget it', 'ignore that',
            'what are you doing', 'what\'s happening', 'whats happening'
        ]
        
        # Emotional expressions
        emotions = [
            'happy', 'sad', 'excited', 'tired', 'bored', 'stressed',
            'angry', 'frustrated', 'confused', 'surprised', 'shocked',
            'love it', 'hate it', 'like it', 'dislike it'
        ]
        
        # Weather and time expressions
        casual_topics = [
            'nice weather', 'hot today', 'cold today', 'raining', 'sunny',
            'good morning', 'good night', 'good evening', 'good afternoon',
            'what time', 'how late', 'early today', 'running late'
        ]
        
        # Check exact phrases first - with and without punctuation
        for phrase in exact_phrases:
            if query_lower == phrase or query_lower == phrase + '!' or query_lower == phrase + '?':
                return True
            # Also check if query starts with the phrase (for variations)
            if query_lower.startswith(phrase + ' ') or query_lower == phrase:
                return True
        
        # Check casual expressions
        for expression in casual_expressions:
            if expression in query_lower:
                return True
                
        # Check emotional expressions
        for emotion in emotions:
            if emotion in query_lower and len(query.split()) <= 4:
                return True
                
        # Check casual topics
        for topic in casual_topics:
            if topic in query_lower:
                return True
        
        # Check if the query is very short and matches common patterns
        if len(query.split()) <= 3:
            for phrase in exact_phrases:
                if phrase in query_lower and phrase != 'you' and phrase != 'help':
                    return True
        
        # Single word responses
        single_words = ['ok', 'okay', 'yes', 'no', 'sure', 'maybe', 'cool', 'nice', 'wow', 'great']
        if query_lower in single_words:
            return True
            
        return False
    
    def _get_greeting_response(self, query: str) -> str:
        """Generate an appropriate greeting response"""
        query_lower = query.lower().strip()
        
        # Greetings
        if any(word in query_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! It's great to connect with you. How can I assist you today?"
        elif 'good morning' in query_lower:
            return "Good morning! It's great to connect with you. How can I assist you today?"
        elif 'good afternoon' in query_lower:
            return "Good afternoon! It's great to connect with you. How can I assist you today?"
        elif 'good evening' in query_lower:
            return "Good evening! It's great to connect with you. How can I assist you today?"
        elif 'good night' in query_lower:
            return "Good night! Sleep well and remember to maintain healthy habits. Feel free to ask me about fitness and nutrition anytime!"
            
        # How are you variations
        elif any(phrase in query_lower for phrase in ['how are you', 'how\'s it going', 'how is it going', 'what\'s up', 'whats up']):
            return "I'm doing great, thank you for asking! I'm here to help you with fitness and nutrition advice. What would you like to know?"
            
        # Day-related questions
        elif any(phrase in query_lower for phrase in ['how is the day', 'how\'s the day', 'how was your day', 'how\'s your day', 'how is today', 'how\'s today']):
            return "The day is going well, thank you for asking! I hope you're having a good day too. Is there anything about fitness or nutrition I can help you with today?"
            
        # General how questions
        elif any(phrase in query_lower for phrase in ['how are things', 'how\'s everything', 'what\'s happening', 'whats happening', 'what are you doing']):
            return "Everything's going well! I'm here and ready to help with any fitness and nutrition questions you might have. What can I assist you with?"
            
        # Thanks and appreciation
        elif any(word in query_lower for word in ['thanks', 'thank you', 'thank u', 'thx']):
            return "You're very welcome! I'm always here to help with your fitness and nutrition questions. Is there anything else you'd like to know?"
            
        # Satisfaction and completion
        elif any(phrase in query_lower for phrase in ['satisfied', 'i am done', 'am done', 'i\'m done', 'enough', 'fine', 'perfect', 'complete', 'all good']):
            return "That's wonderful! I'm glad I could help you with your fitness and nutrition questions. Feel free to come back anytime you need more advice. Stay healthy!"
            
        # Farewells
        elif any(word in query_lower for word in ['bye', 'goodbye', 'see you', 'see ya', 'later', 'cya', 'farewell']):
            return "Goodbye! Take care, and remember to stay active and eat well. Feel free to come back anytime you need fitness or nutrition advice!"
            
        # Positive responses
        elif any(word in query_lower for word in ['cool', 'nice', 'great', 'awesome', 'amazing', 'wonderful', 'excellent', 'fantastic']):
            return "I'm glad you think so! Is there anything specific about fitness or nutrition you'd like to explore?"
            
        # Agreement/Understanding
        elif any(phrase in query_lower for phrase in ['ok', 'okay', 'alright', 'sure', 'i understand', 'i see', 'got it', 'makes sense']):
            return "Great! If you have any questions about fitness, nutrition, or healthy living, I'm here to help!"
            
        # Simple yes/no responses
        elif query_lower in ['yes', 'yep', 'yeah']:
            return "Perfect! What would you like to know about fitness and nutrition?"
        elif query_lower in ['no', 'nope']:
            return "Perfect! I'm glad I could help. If you have any more fitness or nutrition questions in the future, don't hesitate to ask. Take care!"
            
        # Emotional expressions
        elif any(word in query_lower for word in ['happy', 'excited']):
            return "That's wonderful to hear! A positive mindset is great for maintaining healthy habits. How can I help you with your fitness or nutrition goals?"
        elif any(word in query_lower for word in ['tired', 'stressed', 'frustrated']):
            return "I understand how that feels. Sometimes proper nutrition and exercise can help improve energy and mood. Would you like some tips on that?"
        elif any(word in query_lower for word in ['sad', 'bored']):
            return "I'm sorry to hear that. Physical activity and good nutrition can sometimes help improve mood. Would you like some suggestions?"
            
        # Weather and casual topics
        elif any(phrase in query_lower for phrase in ['nice weather', 'hot today', 'cold today', 'raining', 'sunny']):
            return "Weather can definitely affect our motivation to exercise! Would you like some tips for staying active regardless of weather conditions?"
            
        # Apologies
        elif any(word in query_lower for word in ['sorry', 'excuse me', 'pardon', 'my bad']):
            return "No worries at all! I'm here to help with any fitness and nutrition questions you might have."
            
        # Help requests
        elif any(word in query_lower for word in ['help', 'assist']):
            return "I'd be happy to help! I specialize in fitness and nutrition advice. What specific area would you like assistance with?"
            
        # Default friendly response
        else:
            return "Hello! It's great to connect with you. How can I assist you today?"

    async def get_response(self, query: str, user_profile: Optional[UserProfile] = None, 
                          conversation_history: List = None) -> Dict[str, Any]:
        """Get response from the RAG system"""
        try:
            # Check if this is a greeting or simple message
            if self._is_greeting_or_simple_message(query):
                greeting_response = self._get_greeting_response(query)
                return {
                    "answer": greeting_response,
                    "sources": [],
                    "recommendations": []
                }
            
            # Format user profile and add it to the query for context
            enhanced_query = query
            if user_profile:
                profile_info = f"""
User Profile Context:
- Age: {user_profile.age or 'Not specified'}
- Fitness Level: {user_profile.fitness_level or 'Not specified'}
- Goals: {', '.join(user_profile.fitness_goals) if user_profile.fitness_goals else 'Not specified'}
- Dietary Preferences: {', '.join(user_profile.dietary_preferences) if user_profile.dietary_preferences else 'Not specified'}

Question: {query}"""
                enhanced_query = profile_info
            
            # Get response from QA chain using the custom prompt format
            response_dict = self.qa_chain.invoke({"query": enhanced_query})
            
            # Extract the result from the response dictionary
            response = response_dict.get("result", response_dict.get("answer", str(response_dict)))
            
            # Format the response for better readability
            formatted_response = self._format_response(response)
            
            # Get source documents
            docs = self.vectorstore.similarity_search(query, k=3)
            sources = [doc.metadata.get('source', 'Unknown') for doc in docs]
            
            # Generate recommendations based on query type
            recommendations = await self._generate_recommendations(query, user_profile)
            
            return {
                "answer": formatted_response,
                "sources": sources,
                "recommendations": recommendations
            }
            
        except Exception as e:
            print(f"Error getting response: {e}")
            return {
                "answer": "I'm sorry, I encountered an error processing your request. Please try again.",
                "sources": [],
                "recommendations": []
            }
    
    def _format_response(self, response: str) -> str:
        """Format the response for better readability"""
        if not response:
            return response
        
        # Clean up the response
        formatted = response.strip()
        
        # Remove markdown formatting characters
        import re
        
        # Remove "Answer:" at the beginning
        formatted = re.sub(r'^Answer:\s*', '', formatted, flags=re.IGNORECASE)
        
        # Remove all # symbols and extra spaces
        formatted = re.sub(r'#+\s*', '', formatted)  # Remove # headers
        formatted = re.sub(r'\*\*(.*?)\*\*', r'\1', formatted)  # Remove **bold** formatting
        formatted = re.sub(r'\*(.*?)\*', r'\1', formatted)  # Remove *italic* formatting
        
        # Clean up excessive whitespace and newlines
        formatted = re.sub(r'\n\s*\n\s*\n+', '\n\n', formatted)  # Replace 3+ newlines with 2
        formatted = re.sub(r'[ \t]+', ' ', formatted)  # Replace multiple spaces/tabs with single space
        
        # Fix numbered lists - ensure proper spacing
        formatted = re.sub(r'\n+(\d+\.)', r'\n\n\1', formatted)  # Add single line before numbers
        
        # Fix bullet points - ensure single line spacing after each bullet
        formatted = re.sub(r'\n+([•-])', r'\n\1', formatted)  # Single line before bullets
        formatted = formatted.replace('• ', '\n• ')
        formatted = formatted.replace('- ', '\n• ')
        
        # Ensure single line spacing after bullet points
        formatted = re.sub(r'(• .+?)(\n• |\n\d+\.|\n[A-Z])', r'\1\n\2', formatted)
        
        # Clean up colons and periods
        formatted = re.sub(r':\s*\n+', ':\n', formatted)  # Single line after colons
        formatted = re.sub(r'\.\s*\n+([A-Z•\d])', r'.\n\n\1', formatted)  # Double line after periods before new content
        
        # Final cleanup - remove excessive whitespace
        formatted = re.sub(r'\n{3,}', '\n\n', formatted)  # Max 2 consecutive newlines
        formatted = re.sub(r'^\s+|\s+$', '', formatted, flags=re.MULTILINE)  # Trim line whitespace
        formatted = formatted.strip()
        
        return formatted
    
    async def _generate_recommendations(self, query: str, user_profile: Optional[UserProfile]) -> List[HealthRecommendation]:
        """Generate contextual recommendations based on the query"""
        recommendations = []
        
        # Simple keyword-based recommendation logic
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['workout', 'exercise', 'fitness', 'training']):
            recommendations.append(HealthRecommendation(
                type="workout",
                title="Beginner Full Body Workout",
                description="A balanced workout routine for overall fitness",
                details={"duration": "30-45 minutes", "frequency": "3x per week"},
                difficulty="beginner"
            ))
        
        if any(word in query_lower for word in ['diet', 'nutrition', 'eat', 'food', 'meal']):
            recommendations.append(HealthRecommendation(
                type="nutrition",
                title="Balanced Meal Planning",
                description="Tips for creating nutritious, balanced meals",
                details={"focus": "macronutrient balance", "frequency": "daily"},
                difficulty="beginner"
            ))
        
        return recommendations
    
    async def get_category_recommendations(self, category: str, user_profile: Optional[UserProfile]) -> List[HealthRecommendation]:
        """Get recommendations for a specific category"""
        recommendations = []
        
        if category == "fitness":
            recommendations = [
                HealthRecommendation(
                    type="workout",
                    title="Morning Cardio Routine",
                    description="Start your day with energizing cardio exercises",
                    duration="20-30 minutes",
                    difficulty="beginner"
                ),
                HealthRecommendation(
                    type="workout", 
                    title="Strength Training Basics",
                    description="Build muscle with fundamental strength exercises",
                    duration="45 minutes",
                    difficulty="intermediate"
                )
            ]
        elif category == "nutrition":
            recommendations = [
                HealthRecommendation(
                    type="nutrition",
                    title="Hydration Guidelines",
                    description="Optimal water intake for your fitness goals",
                    details={"daily_goal": "8-10 glasses"},
                    difficulty="beginner"
                ),
                HealthRecommendation(
                    type="meal",
                    title="Post-Workout Nutrition",
                    description="What to eat after exercise for optimal recovery",
                    details={"timing": "within 30 minutes", "focus": "protein + carbs"},
                    difficulty="beginner"
                )
            ]
        
        return recommendations