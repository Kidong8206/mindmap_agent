# Mindmap Agent - Chat & Mindmap Builder

A web application that allows you to chat with an AI assistant and visualize your conversation as an interactive mindmap.

## Features

- **Interactive Chat Interface**: Chat with an AI assistant powered by Claude
- **Mindmap Visualization**: Convert your chat history into a beautiful, interactive mindmap
- **Session Persistence**: Your chat history is maintained during your session
- **Responsive Design**: Works on desktop and mobile devices
- **Radial Tree Layout**: Mindmaps are displayed in an elegant radial tree structure

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key (Optional)

If you want to use Claude AI for chat responses:

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Add your Anthropic API key to the `.env` file:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key_here
   ```

If you don't provide an API key, the app will use demo responses.

### 3. Run the Application

```bash
cd mindmap_agent/app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the Application

Open your browser and navigate to:
- Web Interface: http://localhost:8000/app
- API Documentation: http://localhost:8000/docs

## Usage

1. **Start Chatting**: Type a message in the chat input and press Enter or click Send
2. **View Responses**: The AI will respond to your messages
3. **Generate Mindmap**: Click the "Generate Mindmap" button to visualize your conversation
4. **Interact with Mindmap**:
   - Zoom in/out using mouse wheel
   - Drag to pan around the mindmap
   - Hover over nodes to see them highlighted
5. **Clear Chat**: Click "Clear Chat" to start a new conversation

## API Endpoints

- `POST /api/chat` - Send a chat message
- `GET /api/chat/{session_id}` - Get chat history
- `POST /api/mindmap` - Generate mindmap from chat history
- `DELETE /api/chat/{session_id}` - Clear chat history

## Technologies Used

- **Backend**: FastAPI, Python
- **Frontend**: HTML, CSS, JavaScript
- **Visualization**: D3.js (Data-Driven Documents)
- **AI**: Anthropic Claude API

## Project Structure

```
mindmap_agent/
├── mindmap_agent/
│   └── app/
│       ├── main.py           # FastAPI application
│       └── static/
│           ├── index.html    # Main HTML page
│           ├── styles.css    # Styling
│           └── app.js        # Frontend JavaScript
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## License

This is a research and development project.
