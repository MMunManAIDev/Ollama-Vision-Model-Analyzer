# Ollama Vision Model Analyzer

A modern, user-friendly GUI application for analyzing images with any Ollama vision model. No more command line interfaces from the stone age!

## 🚀 Features

- **Model Agnostic**: Works with any Ollama vision model (LLaVA, Qwen2.5-Vision, Moondream, BakLLaVA, etc.)
- **Intuitive GUI**: Clean, modern interface with easy file browsing and optional drag & drop
- **Smart Model Detection**: Automatically prioritizes vision models in the dropdown
- **Image Preview**: See your selected image before analysis (optimized size)
- **Drag & Drop Support**: Drop image files directly onto the preview area (optional - requires tkinterdnd2)
- **Flexible Prompting**: Enter custom questions about your images
- **Response Management**: Copy responses to clipboard with one click
- **Real-time Status**: Progress indicators and connection status
- **Error Handling**: Comprehensive error messages and troubleshooting
- **Persistent Connections**: Remembers successful connection settings for faster refresh
- **Compact Layout**: Optimized window size with scrollable content

## 📋 Prerequisites

- **Python 3.7+** installed on your system
- **Ollama** installed and running locally
- At least one vision model installed in Ollama

## 🛠️ Installation

### 1. Install Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai)

### 2. Install a Vision Model

Choose one or more vision models to install:

```bash
# Popular vision models
ollama pull llava:7b          # LLaVA 7B - General purpose vision
ollama pull llava:13b         # LLaVA 13B - Better accuracy
ollama pull qwen2.5-coder:7b  # Qwen2.5 Vision - Code analysis
ollama pull moondream         # Moondream - Lightweight vision model
ollama pull bakllava          # BakLLaVA - Alternative vision model
```

### 3. Start Ollama Server

```bash
ollama serve
```

### 4. Install Python Dependencies

```bash
# Required dependencies
pip install ollama pillow

# Optional: For drag and drop support
pip install tkinterdnd2
```

### 5. Download and Run the Application

```bash
# Clone this repository
git clone https://github.com/yourusername/ollama-vision-analyzer.git
cd ollama-vision-analyzer

# Run the application
python ollama_vision_analyzer.py
```

## 💻 Usage

### Basic Workflow

1. **Launch the application**
   ```bash
   python ollama_vision_analyzer.py
   ```

2. **Select a model**: Choose from the dropdown - vision models are sorted first

3. **Choose an image**: 
   - Click "Browse..." to select your image file from your computer, OR
   - Drag & drop an image file directly onto the preview area (if tkinterdnd2 is installed)

4. **Enter your prompt**: Type your question about the image in the prompt field

5. **Analyze**: Click "🔍 Analyze Image" and wait for the model's response

6. **Copy results**: Use "📋 Copy Response" to copy the analysis to your clipboard

### Tips

- **Model Selection**: Vision models appear first in the dropdown for convenience
- **File Selection**: Use Browse... button or drag & drop images directly (JPG, PNG, GIF, BMP, TIFF)
- **Model Refresh**: Click the 🔄 button if you install new models while the app is running
- **Scrollable Interface**: The interface scrolls if content is too tall for your screen
- **Custom Ports**: The app remembers successful connection settings for faster reconnection
- **Drag & Drop**: Install `tkinterdnd2` for drag & drop support: `pip install tkinterdnd2`

### Example Prompts

- `"Describe what you see in this image"`
- `"What text is visible in this screenshot?"`
- `"Count the number of people in this photo"`
- `"What colors are dominant in this image?"`
- `"Explain the code shown in this screenshot"`
- `"What emotions are expressed by the people in this image?"`

## 🎯 Supported Models

The application works with any Ollama model, but is optimized for vision models:

| Model | Size | Best For |
|-------|------|----------|
| **llava:7b** | ~4GB | General image analysis |
| **llava:13b** | ~7GB | High-accuracy analysis |
| **qwen2.5-coder:7b** | ~4GB | Code and technical images |
| **moondream** | ~2GB | Lightweight, fast analysis |
| **bakllava** | ~4GB | Alternative general vision |

## 🐛 Troubleshooting

### "Could not connect to Ollama server"
- Ensure Ollama is running: `ollama serve`
- Check if another application is using port 11434
- Try restarting Ollama

### "No models found"
- Install a vision model: `ollama pull llava:7b`
- Verify models are installed: `ollama list`
- Click the 🔄 refresh button in the app

### "Analysis failed" or 404 errors
- Ensure you selected a valid model from the dropdown
- Try a different model if available
- Check Ollama logs for detailed error messages

### Image not loading
- Supported formats: JPG, JPEG, PNG, GIF, BMP, TIFF
- Ensure the image file isn't corrupted
- Try a different image to test

## 🔧 Configuration

The application automatically tries multiple connection methods:
- `http://localhost:11434` (default)
- `http://127.0.0.1:11434`
- `http://localhost:8080` (alternative)

If you're running Ollama on a different port or host, modify the `initialize_ollama_client()` method in the source code.

## 🤝 Contributing

Contributions are welcome! Here are some ways you can help:

- 🐛 Report bugs or issues
- 💡 Suggest new features
- 📖 Improve documentation
- 🔧 Submit pull requests

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for providing the excellent local AI platform
- [Meta AI](https://ai.meta.com/) for the LLaVA model
- [Alibaba](https://qwenlm.github.io/) for the Qwen2.5-Vision model
- The open-source AI community for advancing vision model technology

## ⭐ Star History

If this project helped you, please consider giving it a star! It helps others discover this tool.

---

**Made with ❤️ for the AI community**

*No more command line headaches - just simple, powerful image analysis!*
