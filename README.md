# Live Translation System

<a>
  <img src="/public/lt.jpeg" width="400" />
</a>

## About the System

The Live Translation System is a real-time speech-to-text and translation tool. It leverages advanced speech recognition and translation models to transcribe spoken language and translate it into the desired target language. The system is designed for ease of use, supporting both direct code execution and a standalone executable tool.

## Features
- Real-time speech transcription
- Language translation
- Voice Activity Detection (VAD)
- User-friendly GUI
- ONNX-based model inference

## System Includes
- Speech-to-text transcription service
- Translation service
- Voice Activity Detection (VAD) service
- GUI for user interaction
- Pre-trained ONNX models for speech processing
- Standalone executable for easy deployment

## How to Run the System Locally

### 1. Running from Source Code

1. Clone the repository and navigate to the project directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the main application:
   ```bash
   python main.py
   ```

### 2. Using the Standalone Executable (.exe)

1. Navigate to the `build/Live_Translator/` or `dist/Live_Translator/` directory.
2. Double-click `Live_Translator.exe` to launch the tool.

## How to Build the Executable (.exe)

1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
2. Use PyInstaller to build the executable:
   ```bash
   pyinstaller Live_Translator.spec
   ```
3. The generated `.exe` and related files will be available in the `build/Live_Translator/` and `dist/Live_Translator/` directories.

---

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

