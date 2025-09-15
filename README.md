# Polyglot Media Analyzer

An AI-powered platform that ingests video/audio to deliver real-time multilingual transcription, translation, summarization, sentiment analysis, object/logo detection, and highlight reel generation.

## Features

- 🎵 **Audio & Video Processing**: Support for MP4, AVI, MOV, MP3, WAV, M4A files
- 🗣️ **Real-time Transcription**: Powered by Hugging Face Whisper models
- 🌍 **Multilingual Translation**: Support for 9+ languages
- 📄 **AI Summarization**: Automatic content summarization
- 😊 **Sentiment Analysis**: Real-time emotion detection
- 👁️ **Object Detection**: Video frame analysis and object recognition
- 🎬 **Highlight Reels**: Automated video segment creation
- 🔍 **Smart Search**: ElasticSearch-powered content discovery
- 📊 **Analytics Dashboard**: Comprehensive insights and reporting

## Technology Stack

- **Backend**: FastAPI, Python 3.11
- **Frontend**: React 18, Material-UI
- **Database**: PostgreSQL 15
- **Search**: ElasticSearch 8.11
- **Cache**: Redis 7
- **AI Models**: Hugging Face Transformers
- **Deployment**: Docker, Kubernetes
- **Media Processing**: FFmpeg, MoviePy, OpenCV

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/r3ximous/Polyglot-Media-Analyzer.git
   cd Polyglot-Media-Analyzer
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Installation

#### Backend Setup

1. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r ../requirements.txt
   ```

2. **Set up PostgreSQL**
   ```bash
   # Install and start PostgreSQL
   createdb polyglot_media
   ```

3. **Set up ElasticSearch**
   ```bash
   # Install and start ElasticSearch
   # Default: http://localhost:9200
   ```

4. **Set up Redis**
   ```bash
   # Install and start Redis
   # Default: redis://localhost:6379
   ```

5. **Run the backend**
   ```bash
   cd backend/app
   uvicorn main:app --reload --port 8000
   ```

#### Frontend Setup

1. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server**
   ```bash
   npm start
   ```

## Usage

### 1. Upload Media Files
- Drag and drop or click to select video/audio files
- Supported formats: MP4, AVI, MOV, MP3, WAV, M4A
- Maximum file size: 500MB

### 2. Monitor Processing
- Real-time status updates
- Progress tracking for each AI task
- Error handling and retry mechanisms

### 3. View Results
- **Transcription**: Full text with timestamps and confidence scores
- **Translation**: Translate to 9+ languages
- **Summary**: AI-generated content summaries
- **Sentiment**: Emotion analysis with confidence metrics
- **Objects**: Detected items in video frames
- **Highlights**: Create custom video segments

### 4. Search Content
- Natural language queries
- Filter by file type, language, sentiment
- Advanced search with highlighting
- Export results and analytics

## API Documentation

The API provides comprehensive endpoints for all functionality:

- `POST /api/v1/media/upload` - Upload media files
- `GET /api/v1/media/status/{file_id}` - Check processing status
- `GET /api/v1/media/transcription/{file_id}` - Get transcription results
- `POST /api/v1/media/translate/{file_id}` - Translate content
- `GET /api/v1/media/summary/{file_id}` - Get summary
- `GET /api/v1/media/sentiment/{file_id}` - Get sentiment analysis
- `GET /api/v1/media/objects/{file_id}` - Get object detection results
- `POST /api/v1/media/highlight/{file_id}` - Create highlight reel
- `GET /api/v1/search/search` - Search content
- `GET /api/v1/search/analytics/overview` - Get analytics

Full API documentation available at: `http://localhost:8000/docs`

## Deployment

### Docker Production Deployment

1. **Build images**
   ```bash
   docker build -f Dockerfile.backend -t polyglot-backend .
   docker build -f Dockerfile.frontend -t polyglot-frontend .
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Kubernetes Deployment

1. **Apply configurations**
   ```bash
   kubectl apply -f k8s/
   ```

2. **Monitor deployment**
   ```bash
   kubectl get pods -w
   ```

3. **Access services**
   ```bash
   kubectl get services
   ```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/polyglot_media

# ElasticSearch
ELASTICSEARCH_URL=http://localhost:9200

# Redis
REDIS_URL=redis://localhost:6379

# AI Models
ASR_MODEL=openai/whisper-base
TRANSLATION_MODEL=Helsinki-NLP/opus-mt-en-mul
SUMMARIZATION_MODEL=facebook/bart-large-cnn
SENTIMENT_MODEL=cardiffnlp/twitter-roberta-base-sentiment-latest
OBJECT_DETECTION_MODEL=facebook/detr-resnet-50

# Security
SECRET_KEY=your-super-secret-key
HF_TOKEN=your_hugging_face_token
```

### Model Configuration

The platform supports different Hugging Face models:

- **ASR**: openai/whisper-small, openai/whisper-medium, openai/whisper-large
- **Translation**: Various Helsinki-NLP models for different language pairs
- **Summarization**: facebook/bart-large-cnn, google/pegasus-xsum
- **Sentiment**: cardiffnlp/twitter-roberta-base-sentiment-latest
- **Object Detection**: facebook/detr-resnet-50, facebook/detr-resnet-101

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │  FastAPI Backend│    │   PostgreSQL    │
│                 │◄──►│                 │◄──►│                 │
│  - File Upload  │    │  - AI Processing│    │  - Metadata     │
│  - Results View │    │  - API Endpoints│    │  - Results      │
│  - Search UI    │    │  - Media Proc.  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  ElasticSearch  │    │  Hugging Face   │    │     Redis       │
│                 │    │                 │    │                 │
│  - Full-text    │    │  - ASR Models   │    │  - Caching      │
│  - Search Index │    │  - Translation  │    │  - Background   │
│  - Analytics    │    │  - Sentiment    │    │  - Tasks        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation at `/docs`
- Review the API documentation at `/api/docs`

## Roadmap

- [ ] Real-time streaming support
- [ ] Advanced video analytics
- [ ] Multi-user authentication
- [ ] API rate limiting
- [ ] Advanced caching strategies
- [ ] Mobile app support
- [ ] Integration with cloud storage
=======