"""
utilities.py
General assistant features: time, date, greeting, websites, Wikipedia, jokes.
"""

import datetime
import random
import re
import webbrowser

WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "stackoverflow": "https://stackoverflow.com",
}

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "A SQL query walks into a bar, walks up to two tables and asks, can I join you?",
    "Why did the student eat his homework? Because the teacher said it was a piece of cake.",
    "There are 10 types of people in the world, those who understand binary and those who do not.",
]


def greet(name):
    hour = datetime.datetime.now().hour
    if hour < 12:
        part = "Good morning"
    elif hour < 17:
        part = "Good afternoon"
    else:
        part = "Good evening"
    return f"{part} {name}! I am your Smart Campus and Study Assistant. Type help to see what I can do."


def tell_time():
    return "The time is " + datetime.datetime.now().strftime("%I:%M %p")


def tell_date():
    return "Today is " + datetime.datetime.now().strftime("%A, %d %B %Y")


def open_website(command):
    for name, url in WEBSITES.items():
        if name in command:
            webbrowser.open(url)
            return f"Opening {name}."
    return "Which site? I can open: " + ", ".join(WEBSITES)


def search_google(command):
    query = command.replace("search", "").replace("google", "").strip()
    if not query:
        return "What should I search?"
    webbrowser.open("https://www.google.com/search?q=" + query.replace(" ", "+"))
    return f"Searching Google for {query}."


def search_wikipedia(command):
    topic = command
    for word in ("wikipedia", "what is", "what are", "who is", "tell me about",
                 "explain", "define", "meaning of"):
        topic = topic.replace(word, "")
    topic = topic.strip()
    if not topic:
        return "What topic should I look up?"
    try:
        import wikipedia
        try:
            # auto_suggest=True can mangle the title (e.g. "machine learnning")
            return wikipedia.summary(topic, sentences=2, auto_suggest=False)
        except wikipedia.exceptions.DisambiguationError as e:
            return wikipedia.summary(e.options[0], sentences=2, auto_suggest=False)
        except wikipedia.exceptions.PageError:
            results = wikipedia.search(topic)
            if not results:
                raise
            return wikipedia.summary(results[0], sentences=2, auto_suggest=False)
    except ImportError:
        return "Wikipedia library is not installed. Run pip install wikipedia."
    except Exception:
        return f"Sorry, I could not find {topic} on Wikipedia."


def tell_joke():
    try:
        import pyjokes
        return pyjokes.get_joke()
    except Exception:
        return random.choice(JOKES)


# ---------------------------------------------------------------- small talk
GREETING = re.compile(r"\b(hello|hi+|hey+|namaste|yo|good (morning|afternoon|evening|night))\b")
FILLER = {"there", "assistant", "bot", "buddy", "friend", "dear", "sir", "madam", "all",
          "everyone", "how", "are", "you", "doing", "is", "it", "going", "u", "r"}


def small_talk(command, name="Student"):
    """Reply to greetings and casual chat. Returns None if it is not small talk."""
    text = re.sub(r"[^a-z' ]", " ", command.lower())
    words = text.split()
    if not words or len(words) > 8:
        return None

    replies = []
    if GREETING.search(text):
        rest = [w for w in GREETING.sub("", text).split() if w not in FILLER]
        if not rest:
            replies.append(f"Hello {name}!")
    if re.search(r"\bhow are you\b|\bhow r u\b|\bhow is it going\b|\bhow's it going\b|\bwhat's up\b|\bwassup\b", text):
        replies.append("I am doing great, thanks for asking!")
    if re.search(r"\bwho are you\b|\byour name\b|\bwhat are you\b|\bintroduce yourself\b", text):
        replies.append("I am your Smart Campus and Study Assistant, an AI Lab project. "
                       "I use search, logic and probability algorithms to help you study.")
    if re.search(r"\bwho (made|created|built|developed) you\b", text):
        replies.append("I was built by Garvit Khicher as an AI Lab project.")
    if re.search(r"\b(thanks|thank you|thankyou|thx)\b", text):
        replies.append("You are welcome! All the best for your exams.")
    if re.search(r"\bbored\b", text):
        replies.append("Let us take a break! Try play 8 puzzle, play wumpus world or tell me a joke.")
    if re.fullmatch(r"(ok|okay|cool|nice|great|good|fine|awesome)", text.strip()):
        replies.append("Great! Tell me what you would like to do next.")

    if not replies:
        return None
    if GREETING.search(text) and not re.search(r"\bhow are you\b|\bwho\b|\bwhat\b", text):
        replies.append("Ask me for a route, a study timetable, or any topic like what is machine "
                       "learning (I look those up on Wikipedia). Type help to see everything.")
    return " ".join(replies)


def is_small_talk(command):
    return small_talk(command) is not None
