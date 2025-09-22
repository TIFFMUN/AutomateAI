# AutomateAI 🚀

A comprehensive AI-powered employee development platform featuring React frontend with Python backend, designed to streamline career growth, skill development, performance management, and onboarding processes.

## ✨ Key Features

### 🎯 **Performance Management**

- AI-powered feedback analysis and insights
- Manager-employee feedback system
- Performance tracking and goal setting
- Real-time progress monitoring
- AI assistant for feedback improvement suggestions

### 🛠️ **Skills Development**

- Personalized skill assessment
- AI-driven learning recommendations
- Skill gap analysis
- Progress tracking and certification paths
- Interactive skill development modules

### 🚀 **Career Planning**

- AI career path recommendations
- Job matching and opportunities
- Career goal setting and tracking
- Industry insights and trends
- Personalized career development plans

### 📋 **Employee Onboarding**

- Streamlined onboarding workflows
- Interactive checklists and tasks
- Progress tracking and completion status
- Integration with HR systems
- Automated welcome sequences

## 🏗️ Architecture

- **Frontend**: React 18 with modern UI components
- **Backend**: FastAPI with Python 3.11+
- **AI Integration**: LangChain, LangGraph, Google Gemini AI
- **Database**: PostgreSQL with dual database setup
- **Authentication**: JWT-based secure authentication
- **Deployment**: Docker containerization

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running
- Git for version control

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd AutomateAI
```

### 2. Environment Setup

Create a `.env` file in the backend directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start the Application

```bash
# Start all services
docker-compose up

# Or start in detached mode
docker-compose up -d
```

### 4. Access the Application

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database Admin**: http://localhost:5050 (pgAdmin)
- **Main Database**: localhost:5432
- **Performance Database**: localhost:5433

## 🛠️ Development Commands

```bash
# Start development environment
docker-compose up

# Stop all services
docker-compose down

# View logs for specific service
docker-compose logs -f frontend
docker-compose logs -f backend

# Rebuild services
docker-compose up --build

# Start production environment
docker-compose -f docker-compose.prod.yml up

# Database operations
docker-compose exec backend python migrate_database.py
docker-compose exec backend python clear_database.py
```

## 📁 Project Structure

```
AutomateAI/
├── frontend/                 # React frontend application
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── Career/      # Career planning features
│   │   │   ├── Performance/ # Performance management
│   │   │   ├── Skills/      # Skills development
│   │   │   ├── Onboarding/  # Employee onboarding
│   │   │   └── Login/       # Authentication
│   │   ├── contexts/        # React contexts
│   │   └── utils/           # Utility functions
│   └── Dockerfile
├── backend/                 # Python FastAPI backend
│   ├── routers/            # API route handlers
│   ├── models/             # Database models
│   ├── services/           # Business logic services
│   ├── auth/               # Authentication utilities
│   └── data/               # Sample data and configurations
├── docker-compose.yml      # Development environment
├── docker-compose.prod.yml  # Production environment
└── README.md
```

## 🔧 Technology Stack

### Frontend

- **React 18** - Modern UI framework
- **React Router** - Client-side routing
- **CSS3** - Custom styling with modern features
- **Responsive Design** - Mobile-first approach

### Backend

- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - Python SQL toolkit and ORM
- **Alembic** - Database migration tool
- **Pydantic** - Data validation and settings management

### AI & Machine Learning

- **LangChain** - Framework for developing LLM applications
- **LangGraph** - Stateful, multi-actor applications with LLMs
- **Google Gemini AI** - Advanced AI model integration
- **OpenAI** - GPT model integration

### Database & Storage

- **PostgreSQL 15** - Primary database
- **Dual Database Setup** - Separate databases for different modules
- **pgAdmin** - Database administration interface

### DevOps & Deployment

- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Environment Configuration** - Flexible deployment options

## 🔐 Authentication & Security

- JWT-based authentication system
- Secure password hashing with bcrypt
- Protected routes and API endpoints
- Role-based access control
- Environment variable configuration for sensitive data

## 📊 API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation powered by Swagger UI.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the API documentation at http://localhost:8000/docs
- Review the Docker logs for troubleshooting

---

**Built with ❤️ for modern employee development and AI-powered career growth.**
