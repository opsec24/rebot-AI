# 🔒 Pentest Vulnerability Report Generator

A powerful AI-powered tool for penetration testers to create professional vulnerability reports with automatic content generation using LLaMA 3.2 3B and OLLAMA.

## ✨ Features

### 🤖 AI-Powered Content Generation
- **Intelligent vulnerability analysis** using LLaMA 3.2 3B model
- **Dynamic field population** - AI analyzes vulnerability titles and generates appropriate details
- **Accurate OWASP and CWE classification** based on vulnerability type
- **Realistic impact and likelihood assessment** 
- **Professional descriptions** with technical accuracy
- **Contextual remediation steps** tailored to the specific vulnerability

### 📝 Professional Rich Text Editor
- **WYSIWYG editor** for steps to reproduce
- **Smart image handling** - properly sized images with copy/paste support
- **Professional formatting** with headers, lists, and code blocks
- **Real-time preview** of formatted content

### 📊 Comprehensive Report Management
- **Interactive dashboard** with vulnerability summary
- **Visual severity indicators** (Critical, High, Medium, Low)
- **Individual vulnerability management** with delete functionality
- **Real-time statistics** and metrics

### 📤 Professional Export Options
- **Markdown Export** - Easy editing and version control
- **PDF Export** - Professional presentation-ready reports with:
  - Color-coded severity indicators
  - Professional table formatting
  - Clean typography and layout
  - Industry-standard structure

### 🎯 Pentester-Focused Design
- **No database required** - uses in-memory storage
- **Offline capable** - works without internet (except for AI features)
- **Industry-standard templates** following OWASP guidelines
- **Client-ready reports** for immediate delivery

## 🚀 Quick Start

### Prerequisites
1. **Python 3.8+**
2. **OLLAMA** installed and running
3. **LLaMA 3.2 3B model** (auto-installed)

### Installation & Setup

1. **Clone or download** this repository
2. **Run the setup script:**
   ```bash
   python run.py
   ```

The script will:
- ✅ Install Python dependencies
- ✅ Check and install OLLAMA if needed
- ✅ Download LLaMA 3.2 3B model
- ✅ Start the application

3. **Open your browser** and go to: `http://localhost:8000`

### Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start OLLAMA (in a separate terminal)
ollama serve

# Pull the LLaMA model
ollama pull llama3.2:3b

# Start the application
python backend.py
```

## 🎮 How to Use

### 1. Add New Vulnerability
1. **Enter vulnerability title** (e.g., "SQL Injection in Login Form")
2. **Click "Generate with AI"** to auto-fill details
3. **Review and modify** AI-generated content
4. **Add steps to reproduce** using the rich text editor
5. **Upload images** by dragging/dropping or copy/pasting
6. **Save the vulnerability**

### 2. View Reports
- **Dashboard view** with summary statistics
- **Individual reports** with full details
- **Visual severity indicators**
- **Image thumbnails** for reports with screenshots

### 3. Export Reports
- **Combined report** with all vulnerabilities
- **Markdown format** for easy sharing
- **Professional formatting** ready for client delivery

## 🛠️ Technical Details

### Architecture
- **Backend:** FastAPI with Python
- **Frontend:** HTML/CSS/JavaScript with Bootstrap
- **AI:** LLaMA 3.1 3B via OLLAMA
- **Text Editor:** Quill.js for rich text editing
- **Storage:** In-memory (no database required)

### AI Integration
- **LangChain** for structured output parsing
- **OLLAMA** for local LLM inference
- **Pydantic** for data validation
- **Custom prompts** optimized for pentest reports

### Image Handling
- **Base64 encoding** for embedded images
- **Multiple format support** (PNG, JPG, GIF, etc.)
- **Drag & drop** and copy/paste support
- **Thumbnail previews** in the editor

## 📋 API Endpoints

- `GET /` - Main application page
- `POST /api/generate-vulnerability-details` - AI content generation
- `POST /api/save-vulnerability` - Save vulnerability report
- `GET /api/vulnerabilities` - Get all vulnerabilities
- `DELETE /api/vulnerabilities/{id}` - Delete vulnerability
- `GET /api/export-report` - Export combined report

## 🔧 Configuration

### Environment Variables
Create a `.env` file for custom configuration:
```env
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.2:3b
```

### Customizing AI Prompts
Edit the `vulnerability_prompt` in `backend.py` to customize AI behavior.

## 🐛 Troubleshooting

### OLLAMA Issues
- **OLLAMA not running:** Run `ollama serve` in a separate terminal
- **Model not found:** Run `ollama pull llama3.2:3b`
- **Slow responses:** The 3B model may be slow on older hardware

### Image Upload Issues
- **Images not showing:** Check browser console for errors
- **Large images:** Consider compressing images before upload
- **Format issues:** Supported formats: PNG, JPG, JPEG, GIF, BMP, WebP

### Performance Issues
- **Slow AI generation:** Consider using a more powerful model or GPU
- **Memory usage:** The 3B model requires ~4GB RAM

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OLLAMA** for local LLM inference
- **LangChain** for AI integration
- **FastAPI** for the backend framework
- **Quill.js** for the rich text editor
- **Bootstrap** for the UI framework

---

**Made with ❤️ for the penetration testing community**
