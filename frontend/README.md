# Ask UNE Frontend

A modern React + Vite frontend for the University Multi-Agent Support System.

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Development

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Open browser**
   ```
   http://localhost:5173
   ```

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## 🛠️ Features

- **Modern React 18** with hooks and functional components
- **Vite** for fast development and building
- **Proxy configuration** for seamless API integration
- **Responsive design** that works on desktop and mobile
- **Real-time chat interface** with loading states
- **Error handling** with user-friendly messages
- **Session management** with localStorage persistence

## 🎨 UI/UX

- **Beautiful gradient design** with modern styling
- **Smooth animations** and transitions
- **Typing indicators** for better user experience
- **Mobile-responsive** layout
- **Accessible** keyboard navigation (Enter to send)

## 🔧 Configuration

### API Integration
The frontend uses Vite's proxy feature to forward API calls to the Django backend:
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api/*`

### Environment Variables
Create a `.env` file for custom configuration:
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

## 📁 Project Structure

```
src/
├── App.jsx          # Main chat component
├── App.css          # Styles for the chat interface
├── main.jsx         # React entry point
└── index.css        # Global styles
```

## 🤝 Contributing

1. Make changes to the source files
2. Test locally with `npm run dev`
3. Build and test with `npm run build && npm run preview`
4. Submit your changes

## 📦 Dependencies

- **react**: UI library
- **react-dom**: DOM rendering
- **vite**: Build tool and dev server
- **@vitejs/plugin-react**: React support for Vite
- **eslint**: Code linting
