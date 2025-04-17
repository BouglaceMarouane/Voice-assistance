import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
from PIL import Image, ImageTk


class VoiceAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Assistant")
        self.root.geometry("650x600")
        self.root.configure(bg="#121212")

        # Initialize text-to-speech engine with error handling
        try:
            self.engine = pyttsx3.init()
            self.voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', self.voices[2].id if len(self.voices) > 1 else self.voices[0].id)
            self.engine.setProperty('rate', 150)  # Speed of speech
            self.engine.setProperty('volume', 1.0)  # Maximum volume

            # Test audio output
            self.test_audio()
        except Exception as e:
            print(f"TTS Engine Error: {e}")
            messagebox.showerror("TTS Error",
                                 f"Could not initialize text-to-speech engine: {e}\nThe assistant will run without voice output.")
            self.engine = None

        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.setup_ui()

    def test_audio(self):
        """Test audio output and report any issues"""
        try:
            # Get current volume and save it
            current_volume = self.engine.getProperty('volume')

            # Set test volume and say a short phrase
            self.engine.setProperty('volume', 1.0)
            self.engine.say("Audio test")
            self.engine.runAndWait()

            # Restore original volume
            self.engine.setProperty('volume', current_volume)

            print("Audio test completed successfully")
        except Exception as e:
            print(f"Audio test failed: {e}")
            raise

    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg="#121212")
        title_frame.pack(fill=tk.X, pady=(10, 20))

        title_label = tk.Label(
            title_frame,
            text="Voice Assistant",
            font=("Arial", 16, "bold"),
            bg="#121212",
            fg="white",
            anchor="center"
        )
        title_label.pack(side=tk.TOP, padx=20)

        # Main content frame
        content_frame = tk.Frame(self.root, bg="#121212")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Button frame
        button_frame = tk.Frame(content_frame, bg="#121212")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 10))

        # Load the exit icon (supports .png, .jpg, etc.)
        exit_image = Image.open("exit.png")
        exit_image = exit_image.resize((30, 30))  # Resize the image if needed
        self.exit_icon = ImageTk.PhotoImage(exit_image)

        # Exit button (red)
        self.exit_button = tk.Button(
            button_frame,
            text="Exit",
            image=self.exit_icon,
            compound="left",  # Image on the left of the text
            command=self.exit_app,
            bg="#FF0000",
            fg="white",
            font=("Arial", 12, "bold"),
            width=170,
            height=45,
            relief=tk.FLAT,
            cursor="hand2",
            padx=5  # Space between image and text
        )
        self.exit_button.pack(side=tk.LEFT, padx=10, pady=10)


        # Load the help icon (supports .png, .jpg, etc.)
        help_image = Image.open("Help.png")
        help_image = help_image.resize((30, 30))  # Resize the image if needed
        self.help_icon = ImageTk.PhotoImage(help_image)

        # Help button (green)
        self.help_button = tk.Button(
            button_frame,
            text="Help",
            image=self.help_icon,
            compound="left",  # Image on the left of the text
            command=self.show_help,
            bg="#00FF00",
            fg="black",
            font=("Arial", 12, "bold"),
            width=170,
            height=45,
            relief=tk.FLAT,
            cursor="hand2",
            padx=5  # Space between image and text
        )
        self.help_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Load the mic icon
        mic_image = Image.open("microphone.png")
        mic_image = mic_image.resize((30, 30))
        self.mic_icon = ImageTk.PhotoImage(mic_image)

        # Start Listening button (blue)
        self.listen_button = tk.Button(
            button_frame,
            text="Start Listening",
            image=self.mic_icon,
            compound="left",  # Image on the left of the text
            command=self.toggle_listening,
            bg="#0078D7",
            fg="white",
            font=("Arial", 12, "bold"),
            width=170,
            height=45,
            relief=tk.FLAT,
            cursor="hand2",
            padx = 5  # Space between image and text
        )
        self.listen_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Text area for displaying conversation
        self.conversation = scrolledtext.ScrolledText(
            content_frame,
            wrap=tk.WORD,
            width=50,
            height=10,
            font=("Arial", 10),
            bg="#1E1E1E",
            fg="#FFFFFF",
            insertbackground="white"
        )
        self.conversation.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        self.conversation.config(state=tk.DISABLED)

        # Audio control frame
        audio_frame = tk.Frame(content_frame, bg="#121212")
        audio_frame.pack(fill=tk.X, pady=(0, 10))

        # Test audio button
        self.test_audio_button = tk.Button(
            audio_frame,
            text="Test Audio",
            command=self.test_audio_output,
            bg="#9B59B6",
            fg="white",
            font=("Arial", 10),
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.test_audio_button.pack(side=tk.LEFT, padx=5)

        # Volume control
        volume_label = tk.Label(audio_frame, text="Volume:", bg="#121212", fg="white")
        volume_label.pack(side=tk.LEFT, padx=(10, 5))

        self.volume_scale = tk.Scale(
            audio_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            bg="#121212",
            fg="white",
            highlightbackground="#121212",
            troughcolor="#333333",
            activebackground="#0078D7",
            command=self.set_volume
        )
        self.volume_scale.set(50)  # Default to 50%
        self.volume_scale.pack(side=tk.LEFT, padx=5)

        # Status label
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 10),
            bg="#121212",
            fg="#AAAAAA"
        )
        self.status_label.pack(side=tk.BOTTOM, pady=5)

        # Add initial message
        self.update_conversation("Assistant: Hello! How can I help you today?")
        self.speak("Hello! How can I help you today?")

    def show_help(self):
        help_text = """
Voice Commands:
- Say "hello" or "hi" for a greeting
- Ask for the "time" or "date"
- Say "search [term]" to search Google
- Say "open browser", "open youtube", or "open email"
- Ask about the "weather"
- Say "thank you" or "thanks"
- Say "bye", "goodbye", or "exit" to end the conversation
        """
        self.update_conversation("Assistant: " + help_text)
        self.speak("Here are some commands you can use.")

    def test_audio_output(self):
        """Test button for audio output"""
        self.speak(
            "This is a test of the voice assistant audio. If you can hear this message, audio is working correctly.")
        messagebox.showinfo("Audio Test", "If you didn't hear anything, check your system volume and speakers.")

    def set_volume(self, val):
        """Set the volume of the text-to-speech engine"""
        if self.engine:
            volume = float(val) / 100.0
            self.engine.setProperty('volume', volume)
            print(f"Volume set to {volume}")

    def update_conversation(self, message):
        self.conversation.config(state=tk.NORMAL)
        self.conversation.insert(tk.END, message + "\n")
        self.conversation.see(tk.END)
        self.conversation.config(state=tk.DISABLED)

    def speak(self, text):
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Speech error: {e}")
                self.update_conversation(f"[Speech Error: {e}]")
        else:
            # If TTS engine is not available, just print the message
            print(f"TTS not available: {text}")

    def toggle_listening(self):
        if self.is_listening:
            self.is_listening = False
            self.listen_button.config(text="Start Listening", bg="#0078D7")
            self.status_label.config(text="Ready")
        else:
            self.is_listening = True
            self.listen_button.config(text="Stop Listening", bg="#E81123")
            self.status_label.config(text="Listening...")
            threading.Thread(target=self.listen_for_command).start()

    def exit_app(self):
        self.update_conversation("Assistant: Goodbye! Have a great day!")
        self.speak("Goodbye! Have a great day!")
        self.root.after(1000, self.root.destroy)

    def listen_for_command(self):
        while self.is_listening:
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.status_label.config(text="Listening...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    self.status_label.config(text="Processing...")

                command = self.recognizer.recognize_google(audio).lower()
                self.update_conversation(f"You: {command}")

                # Process the command
                response = self.process_command(command)
                self.update_conversation(f"Assistant: {response}")
                self.speak(response)

            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                self.status_label.config(text="Could not understand audio")
            except sr.RequestError:
                self.status_label.config(text="Could not request results; check your network connection")
            except Exception as e:
                print(f"Error: {e}")
                self.status_label.config(text="Error occurred")

            self.status_label.config(text="Listening..." if self.is_listening else "Ready")

    def process_command(self, command):
        # Simple command processing
        if "hello" in command or "hi" in command:
            return "Hello! How can I help you today?"

        elif "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}"

        elif "date" in command:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            return f"Today is {current_date}"

        elif "search" in command:
            search_term = command.replace("search", "").strip()
            if search_term:
                url = f"https://www.google.com/search?q={search_term}"
                webbrowser.open(url)
                return f"Searching for {search_term}"
            else:
                return "What would you like me to search for?"

        elif "open" in command:
            if "browser" in command or "chrome" in command:
                webbrowser.open("https://www.google.com")
                return "Opening web browser"
            elif "youtube" in command:
                webbrowser.open("https://www.youtube.com")
                return "Opening YouTube"
            elif "email" in command or "gmail" in command:
                webbrowser.open("https://mail.google.com")
                return "Opening Gmail"
            else:
                app = command.replace("open", "").strip()
                return f"I don't know how to open {app}"

        elif "weather" in command:
            return "I'm sorry, I don't have access to weather information at the moment."

        elif "thank you" in command or "thanks" in command:
            return "You're welcome! Is there anything else I can help you with?"

        elif "bye" in command or "goodbye" in command or "exit" in command:
            self.toggle_listening()
            return "Goodbye! Have a great day!"

        elif "help" in command:
            self.show_help()
            return "I've displayed some commands you can use."

        else:
            return "I'm not sure how to help with that. Try asking something else or say 'help' for available commands."


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = VoiceAssistant(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")