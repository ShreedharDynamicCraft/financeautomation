# PDF Data Extractor

A professional PDF extraction application that processes financial documents using Google Gemini AI and delivers structured Excel reports.

## 🚀 Features

- **Modern React Frontend** with Material-UI components
- **Drag & Drop File Upload** with real-time progress tracking
- **Two Extraction Templates** for different document types
- **Google Gemini 2.5 Flash** for intelligent data extraction
- **Background Processing** with FastAPI BackgroundTasks
- **Real-time Status Updates** and job monitoring
- **Professional Excel Export** with multiple sheets
- **Comprehensive Error Handling** and validation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │───▶│   FastAPI       │───▶│  Google Gemini  │
│   (Frontend)    │    │   (Backend)     │    │      API        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Material-UI (MUI)** for components
- **Framer Motion** for animations
- **React Dropzone** for file uploads
- **React Toastify** for notifications
- **Axios** for API communication

### Backend
- **Python 3.11+**
- **FastAPI** for REST API
- **Background Processing** with FastAPI BackgroundTasks
- **Google Gemini 2.5 Flash** for AI processing
- **PyMuPDF** and **pdfplumber** for PDF extraction
- **Pandas** and **OpenPyXL** for Excel generation

## 📋 Prerequisites

- **Node.js 18+** and npm
- **Python 3.11+** and pip
- **Google AI Studio API Key**

## ⚡ Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd pdf-extraction-project
```

### 2. Run Setup Script

```bash
./scripts/setup-dev.sh
```

### 3. Configure Environment

Edit `backend/.env` and add your Google API key:
```env
GOOGLE_API_KEY=your_api_key_here
```

### 4. Start the Application

```bash
./scripts/start-dev.sh
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📊 Extraction Templates

### Template 1: Comprehensive Fund Analysis
- Fund Data (name, currency, size, vintage year)
- Fund Manager details
- Company Investment Positions
- Financial Summary with IRR and multiples

### Template 2: Portfolio Summary Report
- Portfolio Summary metrics
- Schedule of Investments
- Performance Metrics and ratios

## 🔧 Manual Setup (Alternative)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.template .env
# Edit .env and add your Google API key

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 🔧 Configuration

### Environment Variables

```env
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Optional (with defaults)
DEBUG=False
LOG_LEVEL=INFO
MAX_FILE_SIZE=52428800  # 50MB
TASK_TIMEOUT=300  # 5 minutes
```

### Google AI Studio Setup

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create a new project or select existing
3. Generate an API key
4. Add the key to your `.env` file

## 📁 Project Structure

```
pdf-extraction-project/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   ├── types.ts         # TypeScript types
│   │   └── utils/           # Utility functions
│   ├── public/              # Static files
│   └── package.json         # Dependencies
├── backend/                 # Python FastAPI application
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── llm_logic.py     # AI processing logic
│   │   ├── config.py        # Configuration
│   │   └── models.py        # Pydantic models
│   └── requirements.txt     # Python dependencies
├── scripts/                 # Setup and run scripts
└── README.md               # This file
```

## 🧪 API Endpoints

### Upload File
```http
POST /api/upload
Content-Type: multipart/form-data

Form data:
- file: PDF file
- template: "Extraction Template 1" | "Extraction Template 2"
```

### Check Status
```http
GET /api/status/{task_id}
```

### Download Result
```http
GET /downloads/{filename}
```

### Health Check
```http
GET /health
```

## 🐛 Troubleshooting

### Common Issues

1. **"Google API key not configured"**
   - Ensure `GOOGLE_API_KEY` is set in `backend/.env`
   - Verify the key is valid and has Gemini API access

2. **"File upload fails"**
   - Check file size (max 50MB)
   - Ensure file is a valid PDF
   - Verify backend is running

3. **"Processing takes too long"**
   - Large PDF files may take several minutes
   - Check the status endpoint for progress
   - Ensure stable internet connection for API calls

### Logs

```bash
# Backend logs
tail -f backend/app.log

# Real-time logs
cd backend && python -m uvicorn app.main:app --reload --log-level debug
```

## 🚧 Development

### Adding New Templates

1. Add new template logic in `llm_logic.py`
2. Update frontend template selection
3. Test with sample documents

### Custom Prompts

Edit the `build_master_prompt()` function in `backend/app/llm_logic.py` to customize extraction logic.

### Styling Changes

Modify the Material-UI theme in `frontend/src/index.tsx`.

## 📈 Performance

### Optimization Tips
- Use smaller PDF files when possible
- Ensure stable internet connection
- Monitor Google API usage and quotas
- Consider upgrading to Gemini Pro for higher rate limits

## 🔒 Security

- File type validation (PDF only)
- File size limits (50MB default)
- CORS configuration
- Environment variable security
- Input sanitization

## 📜 License

This project is proprietary software. All rights reserved.

## 🤝 Support

For support, please contact the development team or create an issue in the project repository.

---

**Built with ❤️ using React, FastAPI, and Google Gemini AI**# financeautomation
# financeautomation
