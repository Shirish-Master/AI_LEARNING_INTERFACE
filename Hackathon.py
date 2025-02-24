import cv2  # OpenCV for camera functionality
import io
import os
import time
import threading
import openai
import pyttsx3
import customtkinter as ctk
import textwrap  # For manual text wrapping
from google.cloud import vision
from PIL import Image, ImageTk

# Set API Keys
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vision_api_key.json"  # Ensure this file exists
openai.api_key = "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"  # Replace with your OpenAI API key

# Initialize Google Vision API client
client = vision.ImageAnnotatorClient()

# Initialize Text-to-Speech engine
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)
tts_engine.setProperty("volume", 1)

# Global variables
detected_objects = []
detected_texts = []
capturing = False
clicked_questions = set()  # Track clicked questions
current_speech_thread = None  # Track the current speech thread
stop_speech_flag = threading.Event()  # Flag to signal stopping

# Initialize CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Create main window
root = ctk.CTk()
root.title("AI Learning Interface")
root.geometry("1100x650")

# Main Layout - Split into three frames
left_frame = ctk.CTkFrame(root, width=250, height=650, corner_radius=10)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

middle_frame = ctk.CTkFrame(root, width=600, height=650, corner_radius=10)
middle_frame.pack(side="left", padx=10, pady=10, expand=True, fill="both")

right_frame = ctk.CTkFrame(root, width=250, height=650, corner_radius=10)
right_frame.pack(side="right", fill="y", padx=10, pady=10)

# Title Label
title_label = ctk.CTkLabel(middle_frame, text="📚 AI Learning Interface", font=("Arial", 20, "bold"))
title_label.pack(pady=10)

# Left Frame - Detected Objects Section
objects_section_frame = ctk.CTkFrame(left_frame, corner_radius=10, fg_color="#2B2B2B")
objects_section_frame.pack(fill="both", expand=True, padx=5, pady=5)

objects_label = ctk.CTkLabel(objects_section_frame, text="📌 Detected Objects", font=("Arial", 14, "bold"))
objects_label.pack(pady=5)

objects_frame = ctk.CTkScrollableFrame(objects_section_frame, width=220, height=200, corner_radius=5)
objects_frame.pack(fill="both", expand=True, padx=5, pady=5)

# Left Frame - OCR Text Section
ocr_section_frame = ctk.CTkFrame(left_frame, corner_radius=10, fg_color="#2B2B2B")
ocr_section_frame.pack(fill="both", expand=True, padx=5, pady=5)

ocr_label = ctk.CTkLabel(ocr_section_frame, text="🔍 Detected Text (OCR)", font=("Arial", 14, "bold"))
ocr_label.pack(pady=5)

ocr_frame = ctk.CTkScrollableFrame(ocr_section_frame, width=220, height=150, corner_radius=5)
ocr_frame.pack(fill="both", expand=True, padx=5, pady=5)

# Camera Control Buttons
camera_button = ctk.CTkButton(left_frame, text="📷 Start Camera", command=lambda: start_camera())
camera_button.pack(pady=5)

capture_button = ctk.CTkButton(left_frame, text="🛑 Take Photo", command=lambda: stop_camera())
capture_button.pack(pady=5)

# Video Feed Label
video_label = ctk.CTkLabel(middle_frame, text="🎥 Live Video Feed", font=("Arial", 14, "bold"))
video_label.pack()

video_feed = ctk.CTkLabel(middle_frame, text="(Camera Feed Here)")
video_feed.pack(pady=10)

# Right Frame - AI Chat & Questions
conversation_text = ctk.CTkTextbox(right_frame, width=220, height=300, wrap="word")
conversation_text.pack(pady=10, padx=5)

entry = ctk.CTkEntry(right_frame, width=200, placeholder_text="Ask AI here...")
entry.pack(pady=5)

# Frame for Send and Stop buttons
button_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
button_frame.pack(pady=5)

send_button = ctk.CTkButton(button_frame, text="Send", command=lambda: handle_input(), fg_color="green")
send_button.pack(side="left", padx=2)

stop_button = ctk.CTkButton(button_frame, text="Stop", command=lambda: stop_speech(), fg_color="red")
stop_button.pack(side="left", padx=2)

# Progress Bar Section
progress_label = ctk.CTkLabel(right_frame, text="📈 Learning Progress:", font=("Arial", 12, "bold"))
progress_label.pack(pady=5)

progress_var = ctk.DoubleVar()
progress_bar = ctk.CTkProgressBar(right_frame, variable=progress_var, width=180)
progress_bar.set(0)
progress_bar.pack(pady=5)

# Scrollable Follow-Up Questions
button_scroll_frame = ctk.CTkScrollableFrame(right_frame, width=240, height=200, corner_radius=5)
button_scroll_frame.pack(pady=5, padx=5, fill="both", expand=True)

# Exit Button
exit_button = ctk.CTkButton(right_frame, text="Exit", command=root.quit, fg_color="red")
exit_button.pack(pady=5)

def update_progress(question):
    """Increase progress bar by 20% only if the question hasn’t been clicked before."""
    if question not in clicked_questions:
        current_value = progress_var.get()
        if current_value < 1.0:
            progress_var.set(current_value + 0.2)
            clicked_questions.add(question)
            print(f"Progress updated to {progress_var.get()*100}% for question: {question}")
        else:
            print("Progress bar is already full")
    else:
        print(f"Question '{question}' already clicked, no progress update")

def speak_in_chunks(text):
    """Speak text sentence by sentence with stop capability."""
    global current_speech_thread
    stop_speech_flag.clear()  # Reset the stop flag
    sentences = text.split(". ")
    for sentence in sentences:
        if stop_speech_flag.is_set():  # Check if stop is requested
            print("Speech stopped by user")
            break
        if sentence.strip():
            tts_engine.say(sentence)
            conversation_text.insert("end", f"{sentence}. ")
            conversation_text.see("end")
            tts_engine.runAndWait()

def stop_speech():
    """Stop the current speech and OpenAI response."""
    global current_speech_thread
    stop_speech_flag.set()  # Signal the speech thread to stop
    tts_engine.stop()  # Stop the text-to-speech engine immediately
    if current_speech_thread and current_speech_thread.is_alive():
        print("Stopping current speech thread")
    conversation_text.insert("end", "\n[Speech stopped]\n")
    conversation_text.see("end")

def get_object_analysis(user_input):
    """Generate follow-up questions based on a detected object or text."""
    analysis_prompt = f"""
Generate five follow-up questions about '{user_input}' that guide a person from a beginner to an advanced level of understanding. 
Ensure the questions follow a structured learning path, starting with the basics and moving to deeper concepts. 
Use the following levels:
1. Basic Introduction (What is it?)
2. Functionality and Components (How does it work?)
3. Applications and Use Cases (Where is it used?)
4. Advanced Techniques and Optimization (How to optimize or modify it?)
5. Expert-Level Knowledge (What are the latest innovations or challenges?)
Return the questions as a single string with each question on a new line.
"""
    response = ask_openai(analysis_prompt)
    print(f"Raw OpenAI response for '{user_input}': {response}")
    return response

def show_question_buttons(questions):
    """Display buttons with follow-up questions in a scrollable frame."""
    for widget in button_scroll_frame.winfo_children():
        widget.destroy()

    if isinstance(questions, str):
        question_list = questions.strip().split("\n")
    else:
        question_list = questions

    print(f"Questions to display: {question_list}")

    for question in question_list:
        if question.strip():
            wrapped_text = "\n".join(textwrap.wrap(question.strip(), width=30))
            btn = ctk.CTkButton(
                button_scroll_frame,
                text=wrapped_text,
                width=220,
                height=40,
                command=lambda q=question.strip(): [handle_input(q), update_progress(q)],
                corner_radius=5
            )
            btn.pack(pady=2, fill="x")
            print(f"Button created for: {wrapped_text}")
        else:
            print("Empty question skipped")

def handle_input(user_input=None):
    """Handle user input and generate response or follow-up questions."""
    global current_speech_thread
    if user_input is None:
        user_input = entry.get().strip()

    if not user_input:
        return

    conversation_text.insert("end", f"\nYou: {user_input}\n")

    if len(user_input.split()) <= 2:
        analysis = get_object_analysis(user_input)
        show_question_buttons(analysis)
    else:
        response = ask_openai(user_input)
        conversation_text.insert("end", "ChatGPT: ")
        conversation_text.see("end")
        stop_speech_flag.clear()  # Reset stop flag before starting new speech
        current_speech_thread = threading.Thread(target=speak_in_chunks, args=(response,), daemon=True)
        current_speech_thread.start()

    entry.delete(0, "end")

def start_camera():
    """Capture video and update GUI in real-time."""
    global capturing
    capturing = True
    cap = cv2.VideoCapture(0)

    while capturing:
        ret, frame = cap.read()
        if not ret:
            break

        detect_objects_and_text(frame)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        video_feed.imgtk = imgtk
        video_feed.configure(image=imgtk)

        root.update_idletasks()
        root.update()

    cap.release()

def stop_camera():
    """Stop webcam capture."""
    global capturing
    capturing = False

def detect_objects_and_text(frame):
    """Detect objects and extract text using Google Vision API."""
    global detected_objects, detected_texts

    is_success, buffer = cv2.imencode(".jpg", frame)
    image_bytes = buffer.tobytes()

    image = vision.Image(content=image_bytes)

    # Object Detection
    object_response = client.object_localization(image=image)
    objects = object_response.localized_object_annotations

    detected_objects = []
    for obj in objects:
        detected_objects.append(obj.name)

    # OCR (Text Detection)
    text_response = client.text_detection(image=image)
    texts = text_response.text_annotations

    detected_texts = [t.description for t in texts[1:]] if len(texts) > 1 else []

    update_object_buttons()
    update_ocr_buttons()

def update_object_buttons():
    """Display detected object names as buttons in the Objects frame."""
    for widget in objects_frame.winfo_children():
        widget.destroy()

    if not detected_objects:
        no_objects_label = ctk.CTkLabel(objects_frame, text="No objects detected", font=("Arial", 12))
        no_objects_label.pack(pady=5)
    else:
        for obj in detected_objects:
            btn = ctk.CTkButton(objects_frame, text=obj, command=lambda o=obj: handle_input(o))
            btn.pack(pady=2, fill="x")
            print(f"Object button created: {obj}")

def update_ocr_buttons():
    """Display detected OCR text as buttons in the OCR frame."""
    for widget in ocr_frame.winfo_children():
        widget.destroy()

    if not detected_texts:
        no_text_label = ctk.CTkLabel(ocr_frame, text="No text detected", font=("Arial", 12))
        no_text_label.pack(pady=5)
    else:
        for text in detected_texts:
            btn = ctk.CTkButton(ocr_frame, text=text, command=lambda t=text: handle_input(t))
            btn.pack(pady=2, fill="x")
            print(f"OCR button created: {text}")

def ask_openai(prompt):
    """Send a prompt to OpenAI API and return the response."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {e}"

root.mainloop()