# 📚 AI Learning Interface

An interactive desktop application that combines computer vision, speech synthesis, and AI-powered conversations to provide a dynamic learning experience. It uses Google Vision API for object and text recognition, OpenAI for intelligent question generation, and pyttsx3 for speech output — all wrapped in a modern GUI with `CustomTkinter`.

---

## 🧠 Features

- 📷 **Live Camera Feed** – Detect objects and text in real time using your webcam.
- 🧾 **Google Vision API Integration** – Automatically extracts objects and OCR data from images.
- 🤖 **AI-Powered Q&A** – Uses OpenAI's GPT to generate follow-up questions and respond to user queries.
- 🗣️ **Speech Synthesis** – Reads AI responses aloud using `pyttsx3`.
- 🎯 **Learning Progress Bar** – Tracks user interaction with dynamic questions.
- 🖱️ **Dynamic Button Generation** – Creates question buttons that adapt to detected content.
- 🌙 **Dark Mode UI** – Built with `CustomTkinter` for a modern, themed interface.

---

## 🛠️ Technologies Used

- `Python`
- `OpenCV`
- `Google Cloud Vision`
- `OpenAI API`
- `pyttsx3`
- `CustomTkinter`
- `Pillow`

---

## 📦 Installation

### 1. Clone the repository

```
git clone https://github.com/yourusername/ai-learning-interface.git
cd ai-learning-interface
```

### 2. Set up a virtual environment (optional but recommended)

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Configure API keys

-Place your Google Cloud Vision API JSON key file as vision_api_key.json in the project root.

-Replace "OPENAPIKEY" in the code with your actual OpenAI API key or set it as an environment variable.

## 🚀 Usage

Run the application with:

```
python main.py
```

## Usage

- Click **Start Camera** to begin live object and text detection.
- Detected objects and texts appear as clickable buttons on the left.
- Clicking these buttons generates follow-up questions.
- Type your own questions or select generated ones to interact with the AI.
- Use **Send** to submit queries and **Stop** to halt speech output.
- The progress bar tracks your learning progress based on question interactions.

## 📝 Notes

- Requires a working webcam for live detection.
- Ensure you have an active internet connection for OpenAI and Google Vision API calls.
- The speech engine uses your system’s default voice.

