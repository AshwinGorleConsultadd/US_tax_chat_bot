# US Tax Chatbot - Frontend Interface

This directory contains the web-based frontend interface for the US Tax Chatbot. The frontend provides a modern, responsive chat interface that communicates with the Python backend to deliver AI-powered tax assistance.

## Files

- **`index.html`** - Main HTML file with the chat interface structure
- **`styles.css`** - Modern CSS styling with responsive design and animations
- **`script.js`** - JavaScript functionality for chat interactions and API communication
- **`README.md`** - This documentation file

## Features

### 🎨 Modern UI Design
- Clean, professional interface with a tax-focused theme
- Responsive design that works on desktop, tablet, and mobile
- Smooth animations and transitions
- Dark/light theme support (via CSS variables)

### 💬 Chat Interface
- Real-time chat with typing indicators
- Message history with timestamps
- User and assistant message differentiation
- Auto-resizing text input
- Character count and input validation

### 🔧 Functionality
- Send messages to the AI tax assistant
- Reset chat context
- Chat session management
- Error handling with user-friendly messages
- Loading states and status indicators

### 📱 Responsive Design
- Mobile-first approach
- Collapsible sidebar for chat history
- Touch-friendly interface
- Optimized for various screen sizes

## Usage

### Starting the Web Interface

1. **Using the startup script (recommended):**
   ```bash
   python start_web_interface.py
   ```

2. **Direct server start:**
   ```bash
   python web_server.py
   ```

3. **Access the interface:**
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - Start chatting with the tax assistant!

### API Endpoints

The frontend communicates with the backend through these API endpoints:

- **`POST /api/send_message`** - Send a message to the chatbot
- **`POST /api/reset_chat`** - Reset the chat context
- **`GET /api/health`** - Health check endpoint
- **`GET /api/status`** - Get chatbot status and document count

### Example API Usage

```javascript
// Send a message
const response = await fetch('/api/send_message', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        message: 'What are the standard deduction amounts for 2024?'
    })
});

const data = await response.json();
console.log(data.data.response);
```

## Customization

### Styling
The interface uses CSS custom properties (variables) for easy theming:

```css
:root {
    --primary-color: #2563eb;      /* Main brand color */
    --background-color: #f8fafc;   /* Background color */
    --text-primary: #1e293b;       /* Primary text color */
    --border-color: #e2e8f0;       /* Border color */
    /* ... more variables */
}
```

### Adding New Features
The JavaScript is modular and easy to extend:

```javascript
class TaxChatbot {
    // Add new methods here
    async newFeature() {
        // Implementation
    }
}
```

## Browser Support

- **Chrome** 90+
- **Firefox** 88+
- **Safari** 14+
- **Edge** 90+

## Development

### Local Development
1. Start the Flask server: `python web_server.py`
2. Open `http://localhost:5000` in your browser
3. Make changes to HTML, CSS, or JS files
4. Refresh the browser to see changes

### Debugging
- Open browser developer tools (F12)
- Check the Console tab for JavaScript errors
- Check the Network tab for API request/response details
- Server logs are displayed in the terminal

## Troubleshooting

### Common Issues

1. **"Failed to send message" error:**
   - Check if the Flask server is running
   - Verify OpenAI API key is set in `.env` file
   - Check server logs for detailed error messages

2. **Interface not loading:**
   - Ensure Flask server is running on port 5000
   - Check browser console for JavaScript errors
   - Verify all files are in the correct locations

3. **Styling issues:**
   - Clear browser cache (Ctrl+F5 or Cmd+Shift+R)
   - Check if CSS file is loading correctly
   - Verify CSS syntax in browser developer tools

### Getting Help
- Check the main project README.md for setup instructions
- Review server logs for error details
- Ensure all dependencies are installed correctly

## License

This frontend interface is part of the US Tax Chatbot project and follows the same licensing terms.
