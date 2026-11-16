"""
main.py
Smart Campus & Study Assistant

Run:
    python main.py          -> typing mode
    python main.py --voice  -> voice mode (needs microphone)

How it works:
1. Take a command (voice or text)
2. Detect the intent using keywords
3. Call the matching module
4. Speak / print the reply
"""

import sys

from modules.speech import speak, take_input
from modules import utilities, campus_navigation, study_planner
from modules import pass_predictor, focus_tracker, brain_games
from modules import dstar, wumpus_world, em_clustering

USER_NAME = "Student"

HELP_TEXT = """
Things you can ask me:
  route from main gate to hostel        (A*, add 'bfs', 'dfs' or 'ids' to change algorithm)
  compare routes from library to hostel (runs all 4 search algorithms)
  reroute from main gate to hostel if library is blocked   (D* Lite re-planning)
  make my study timetable               (Simulated Annealing, say 'hill climbing' to change)
  will i pass                           (Bayesian Network)
  check my focus                        (Hidden Markov Model)
  play hanoi with 4 disks               (Towers of Hanoi)
  play 8 puzzle                         (A* search)
  play wumpus world                     (logical agent, model checking)
  which group am i                      (EM algorithm, clusters students)
  syllabus                              (which algorithm powers which feature)
  hello / how are you / who are you         (small talk)
  time / date / joke
  what is machine learning / who is alan turing / explain recursion  (looked up on Wikipedia)
  open youtube / search python tutorial
  exit
"""

# intent name -> keywords that trigger it (checked in this order)
INTENTS = [
    ("exit", ["exit", "bye", "quit", "stop"]),
    ("help", ["help", "what can you do"]),
    ("chat", utilities.is_small_talk),
    ("syllabus", ["syllabus", "algorithms used", "coverage"]),
    ("compare", ["compare"]),
    ("replan", ["d*", "dstar", "d star", "reroute", "re-route", "replan", "blocked", "closed"]),
    ("wumpus", ["wumpus"]),
    ("em", ["em algorithm", "cluster", "which group", "my group", "student type", "gaussian"]),
    ("route", ["route", "way to", "how to reach", "navigate", "path"]),
    ("timetable", ["timetable", "time table", "schedule", "study plan"]),
    ("pass", ["pass", "exam result", "will i clear"]),
    ("focus", ["focus", "concentration", "distracted"]),
    ("hanoi", ["hanoi", "tower"]),
    ("puzzle", ["8 puzzle", "eight puzzle", "puzzle"]),
    ("time", ["time"]),
    ("date", ["date", "day is it"]),
    ("joke", ["joke", "funny"]),
    ("open", ["open"]),
    ("google", ["search", "google"]),
    ("wiki", ["wikipedia", "what is", "what are", "who is", "tell me about",
              "explain", "define", "meaning of"]),
]


def detect_intent(command):
    for intent, keywords in INTENTS:
        if callable(keywords):
            hit = keywords(command)
        else:
            hit = any(k in command for k in keywords)
        if hit:
            return intent
    return "unknown"


COVERAGE = [
    ("DFS, BFS, Iterative Deepening", "Campus Navigation / Route Comparison", "route ... using dfs|bfs|ids"),
    ("A*", "Campus Navigation, 8 Puzzle", "route from main gate to hostel"),
    ("D* (D* Lite)", "Live route re-planning", "reroute from main gate to hostel if library is blocked"),
    ("Hill Climbing", "Study Timetable", "make my study timetable using hill climbing"),
    ("Simulated Annealing", "Study Timetable", "make my study timetable"),
    ("Wumpus World", "Campus Escape game", "play wumpus world"),
    ("8 Puzzle", "Brain Games", "play 8 puzzle"),
    ("Towers of Hanoi", "Brain Games", "play hanoi with 4 disks"),
    ("Bayesian Network", "Pass Predictor", "will i pass"),
    ("EM Algorithm", "Student group clustering", "which group am i"),
    ("Hidden Markov Model", "Focus Tracker", "check my focus"),
]


def show_coverage():
    print(f"{'Lab topic':30} | {'Feature in the assistant':36} | Try saying")
    for topic, feature, example in COVERAGE:
        print(f"{topic:30} | {feature:36} | {example}")
    return "All 13 lab topics are used: every algorithm powers a real feature of the assistant."


def handle(intent, command, ask):
    if intent == "help":
        print(HELP_TEXT)
        return "Here is the list of things I can do."
    if intent == "chat":
        return utilities.small_talk(command, USER_NAME)
    if intent == "syllabus":
        return show_coverage()
    if intent == "replan":
        return dstar.replan(command)
    if intent == "wumpus":
        return wumpus_world.play_wumpus(command)
    if intent == "em":
        return em_clustering.find_my_group(ask)
    if intent == "route":
        return campus_navigation.navigate(command)
    if intent == "compare":
        places = campus_navigation.find_places(command)
        if len(places) < 2:
            return "Tell me two places, like compare routes from library to hostel."
        print(f"{'Algo':5} | {'Cost':5} | {'Explored':8} | Path")
        for name, path, cost, explored in campus_navigation.compare_all(places[0], places[1]):
            print(f"{name:5} | {cost:5} | {explored:8} | {path}")
        return "A star gives the shortest distance. BFS and IDS give the fewest stops."
    if intent == "timetable":
        return study_planner.make_plan(command)
    if intent == "pass":
        return pass_predictor.predict_pass(ask)
    if intent == "focus":
        return focus_tracker.track_focus(ask)
    if intent == "hanoi":
        return brain_games.play_hanoi(command)
    if intent == "puzzle":
        return brain_games.play_8_puzzle(command)
    if intent == "time":
        return utilities.tell_time()
    if intent == "date":
        return utilities.tell_date()
    if intent == "joke":
        return utilities.tell_joke()
    if intent == "open":
        return utilities.open_website(command)
    if intent == "google":
        return utilities.search_google(command)
    if intent == "wiki":
        return utilities.search_wikipedia(command)
    return ("Sorry, I did not understand. Type help to see what I can do. For general "
            "knowledge, ask what is ... or who is ...")


def main():
    voice_mode = "--voice" in sys.argv
    ask = lambda: take_input(voice_mode)

    speak(utilities.greet(USER_NAME), voice_mode)
    while True:
        command = ask()
        if not command:
            continue
        intent = detect_intent(command)
        if intent == "exit":
            speak("Goodbye, all the best for your exams!", voice_mode)
            break
        speak(handle(intent, command, ask), voice_mode)


if __name__ == "__main__":
    main()
