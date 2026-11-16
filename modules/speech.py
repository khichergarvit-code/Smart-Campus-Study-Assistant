"""
speech.py
Handles input and output for the assistant.
- Voice output uses pyttsx3 (offline text to speech).
- Voice input uses SpeechRecognition (needs a microphone + internet).
If these libraries are not installed, the assistant falls back to text mode.
"""

try:
    import pyttsx3
    _engine = pyttsx3.init()
    _engine.setProperty("rate", 175)
    TTS_AVAILABLE = True
except Exception:
    _engine = None
    TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except Exception:
    STT_AVAILABLE = False


def speak(text, voice_on=True):
    """Print the reply and also speak it if text to speech is available."""
    print(f"Assistant: {text}")
    if voice_on and TTS_AVAILABLE:
        try:
            _engine.say(text)
            _engine.runAndWait()
        except Exception:
            pass


def listen_voice():
    """Listen from the microphone and return the recognised text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, phrase_time_limit=6)
    try:
        text = recognizer.recognize_google(audio, language="en-IN")
        print(f"You said: {text}")
        return text.lower()
    except Exception:
        return ""


def take_input(voice_mode=False):
    """Get a command from the user, by voice or by typing."""
    if voice_mode and STT_AVAILABLE:
        try:
            text = listen_voice()
            if text:
                return text
            print("Could not understand, please type instead.")
        except Exception:
            print("Microphone not available, switching to typing.")
    return input("You: ").strip().lower()
