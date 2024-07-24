import speech_recognition as sr
import json
import os
import pyttsx3
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, ttk
import PyPDF2

# Initialize recognizer
recognizer = sr.Recognizer()

# Initialize text-to-speech engine
tts_engine = pyttsx3.init()

# File name
file_name = "recognized_texts.json"

# Supported languages
languages = {
    "English": "en-IN",
    "Hindi": "hi-IN"
}

# Default language
selected_language = "English"

# Function to read and play saved texts for a specific user
def read_and_play_saved_texts():
    user_name = simpledialog.askstring("Input", "Enter your name:")
    if not user_name:
        return
    
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict) and user_name in data:
                recognized_texts = data[user_name]
                for text in recognized_texts:
                    print(f"Playing: {text}")
                    tts_engine.say(text, languages[selected_language])
                    tts_engine.runAndWait()
            else:
                messagebox.showinfo("Information", f"No recognized texts found for {user_name}.")
    else:
        messagebox.showinfo("Information", "No recognized texts found.")

# Function to capture and recognize speech and save for a specific user
def recognize_speech():
    user_name = simpledialog.askstring("Input", "Enter your name:")
    if not user_name:
        return

    with sr.Microphone() as source:
        print("Please say something:")
        audio = recognizer.listen(source)

        try:
            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio, language=languages[selected_language])
            print(f"You said: {text}")

            # Check if file exists and load existing data
            if os.path.exists(file_name):
                with open(file_name, "r", encoding="utf-8") as file:
                    data = json.load(file)
            else:
                data = {}

            # Ensure data is a dictionary
            if not isinstance(data, dict):
                data = {}

            # Add recognized text to the user's list
            if user_name not in data:
                data[user_name] = []
            data[user_name].append(text)

            # Save recognized text to a JSON file
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            messagebox.showinfo("Information", f"Recognized text has been saved for {user_name}.")
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Google Web Speech could not understand audio.")
        except sr.RequestError as e:
            messagebox.showerror("Error", f"Could not request results from Google Web Speech; {e}")

# Function to capture and recognize speech for voice search
def voice_search():
    with sr.Microphone() as source:
        print("Please say something to search:")
        audio = recognizer.listen(source)

        try:
            # Recognize speech using Google Web Speech API
            search_text = recognizer.recognize_google(audio, language=languages[selected_language])
            print(f"You searched for: {search_text}")

            # Check if file exists and load existing data
            if os.path.exists(file_name):
                with open(file_name, "r", encoding="utf-8") as file:
                    data = json.load(file)
            else:
                data = {}

            results = []
            for user, texts in data.items():
                for text in texts:
                    if search_text.lower() in text.lower():
                        results.append((user, text))

            if results:
                result_str = "\n".join([f"User: {user}, Text: {text}" for user, text in results])
                messagebox.showinfo("Search Results", result_str)
            else:
                messagebox.showinfo("Search Results", "No matches found.")
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Google Web Speech could not understand audio.")
        except sr.RequestError as e:
            messagebox.showerror("Error", f"Could not request results from Google Web Speech; {e}")

# Function to read text from a PDF file and play it aloud
def read_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        return

    try:
        pdf_reader = PyPDF2.PdfFileReader(open(file_path, "rb"))
        text = ""
        for page_num in range(pdf_reader.getNumPages()):
            text += pdf_reader.getPage(page_num).extract_text()

        if text:
            tts_engine.say(text, languages[selected_language])
            tts_engine.runAndWait()
        else:
            messagebox.showinfo("Information", "No text found in the PDF file.")
    except Exception as e:
        messagebox.showerror("Error", f"Could not read PDF file: {e}")

# Function to quit the application
def quit_application():
    root.quit()

# Function to update the selected language
def update_language(event):
    global selected_language
    selected_language = language_combobox.get()

# Create GUI
root = tk.Tk()
root.title("Speech Recognition and Playback")
root.geometry("400x400")
root.configure(bg="#d4edda")  # Light green background

# Language selection
language_frame = tk.Frame(root, bg="#d4edda")
language_frame.pack(pady=10)

language_label = tk.Label(language_frame, text="Select Language:", bg="#d4edda", fg="black", font=("Helvetica", 12))
language_label.pack(side="left", padx=5)

language_combobox = ttk.Combobox(language_frame, values=list(languages.keys()), state="readonly", font=("Helvetica", 12))
language_combobox.set(selected_language)
language_combobox.pack(side="left", padx=5)
language_combobox.bind("<<ComboboxSelected>>", update_language)

# Create and place buttons with improved styling
button_style = {"font": ("Helvetica", 12), "bg": "#4CAF50", "fg": "black", "relief": "raised", "width": 20, "height": 2}

recognize_button = tk.Button(root, text="Recognize Speech", command=recognize_speech, **button_style)
recognize_button.pack(pady=10)

play_button = tk.Button(root, text="Play Saved Texts", command=read_and_play_saved_texts, **button_style)
play_button.pack(pady=10)

search_button = tk.Button(root, text="Voice Search", command=voice_search, **button_style)
search_button.pack(pady=10)

pdf_button = tk.Button(root, text="Upload & Read PDF", command=read_pdf, **button_style)
pdf_button.pack(pady=10)

quit_button = tk.Button(root, text="Quit", command=quit_application, **button_style)
quit_button.pack(pady=10)

# Run the application
root.mainloop()
