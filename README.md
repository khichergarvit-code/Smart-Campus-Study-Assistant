# Virtual Assistant — Smart Campus & Study Assistant

**Topic chosen:** Smart Campus & Study Assistant

**Submitted by:** Garvit Khicher | Roll No: 2025kuad3029 | Section: D1 (AIDE)
**Course:** Artificial Intelligence Lab
**GitHub:** _add your repository link here_

---

## About the Project

This is a voice and text based virtual assistant made for college students. It helps a student move around the campus, re-plan a route when a path is blocked, plan study time, check exam readiness, track focus while studying, find out what type of learner they are, and take short breaks with puzzles and games. It also chats, answers general questions from Wikipedia and opens websites.

It comes with a **web chat interface** (a browser page with buttons, voice input and spoken replies) and a **terminal version**.

Every main feature is powered by an algorithm from our AI Lab syllabus, so the assistant covers **all 13 lab topics** (see [Lab Syllabus Coverage](#lab-syllabus-coverage)).

---

## What the Assistant Can Do (at a glance)

| # | Capability | Say something like | Algorithm / technique |
|---|---|---|---|
| 1 | Find a route on campus | `route from main gate to hostel` | A* (default), BFS, DFS, Iterative Deepening |
| 2 | Compare all search algorithms | `compare routes from library to hostel` | A*, BFS, DFS, IDS side by side |
| 3 | Re-plan when a place is blocked | `reroute from main gate to hostel if library is blocked` | D* Lite |
| 4 | Make a weekly study timetable | `make my study timetable` | Simulated Annealing |
| 5 | Same timetable with another method | `make my study timetable using hill climbing` | Hill Climbing |
| 6 | Predict chance of passing | `will i pass` | Bayesian Network |
| 7 | Check study focus | `check my focus` | Hidden Markov Model (Viterbi + Forward) |
| 8 | Find your student type | `which group am i` | EM algorithm (Gaussian Mixture Model) |
| 9 | Play the Wumpus World game | `play wumpus world` | Knowledge-based logical agent, model checking |
| 10 | Solve Towers of Hanoi | `play hanoi with 4 disks` | Recursion |
| 11 | Solve an 8 puzzle | `play 8 puzzle` | A* with Manhattan distance |
| 12 | Show syllabus coverage | `syllabus` | — |
| 13 | Answer general questions | `what is machine learning` | Wikipedia lookup |
| 14 | Small talk | `hello`, `how are you`, `who are you` | Pattern matching |
| 15 | Time, date, jokes | `time`, `date`, `tell me a joke` | — |
| 16 | Open websites / search Google | `open youtube`, `search python tutorial` | — |
| 17 | Help | `help` | — |

---

## Feature Details

### 1. Campus Navigation (A*, BFS, DFS, IDS)
Finds a route between two places on a campus map of **10 places and 14 walking paths** (distances in metres).

**Places:** main gate, parking, admin block, library, cse block, cafeteria, auditorium, medical center, sports ground, hostel.

| Algorithm | Command word | What it finds |
|---|---|---|
| A* (default) | _(nothing)_ | The **shortest distance**, guided by straight-line distance as the heuristic |
| BFS | `bfs` | The route with the **fewest stops** |
| DFS | `dfs` | **Any** route (fast, but not always short) |
| IDS | `ids` | Fewest stops using **low memory** (repeated depth-limited search) |

```
You: route from main gate to hostel
Assistant: Using A*: Main Gate -> Admin Block -> Library -> Cse Block -> Hostel. Distance 435 metres, 4 stops, 5 nodes explored.

You: route from library to cafeteria using bfs
```
The reply also shows how many nodes were explored, so the algorithms can be compared.

### 2. Route Comparison
Runs all four search algorithms on the same trip and prints a table of **cost, nodes explored and path**.

```
You: compare routes from medical center to sports ground
Algo  | Cost  | Explored | Path
BFS   |   ...
DFS   |   ...
IDS   |   ...
A*    |   ...   (always the shortest distance)
```

### 3. Live Route Re-planning (D* Lite)
A student starts walking, but a place on the way is **blocked** (construction, event, locked gate). The student only discovers this when standing next to it. **D\* Lite** keeps the earlier results and repairs only the affected part of the plan, instead of searching again from scratch like A* would.

```
You: reroute from main gate to hostel if library is blocked
D* Lite: Main Gate -> Hostel, hidden blockage: Library
Initial plan : Main Gate -> Admin Block -> Library -> Cse Block -> Hostel (435 m)
At Admin Block: Library is blocked! Replanning...
New plan     : Admin Block -> Auditorium -> Cafeteria -> Cse Block -> Hostel
Route walked : Main Gate -> Admin Block -> Auditorium -> Cafeteria -> Cse Block -> Hostel (527 m)
```
- You can phrase it either way: `library is blocked, reroute from main gate to hostel`.
- Several blocked places can be given (`... if cse block is blocked and sports ground is blocked`).
- If you do not say what is blocked, the assistant blocks a stop on the normal route as a demo.
- It reports honestly when the blocked place was never in the way, or when **no route exists**.
- It compares the work done by D* Lite with restarting A* each time.

### 4. Study Timetable (Simulated Annealing / Hill Climbing)
Builds a **weekly timetable of 6 days x 4 slots** (9-10 AM, 11-12 PM, 3-4 PM, 7-8 PM) for these subjects and weekly hours:

| Subject | Hours / week | Hard subject? |
|---|---|---|
| Artificial Intelligence | 5 | Yes |
| DBMS | 4 | Yes |
| Operating Systems | 4 | Yes |
| Computer Networks | 4 | No |
| Maths | 3 | No |

The algorithm minimises a **cost** (lower is better) that penalises: the same subject in back-to-back slots, a hard subject in the tired last slot, the same subject too many times in a day, and unbalanced days.

- `make my study timetable` uses **Simulated Annealing** (it sometimes accepts a worse swap so it can escape local minima).
- `make my study timetable using hill climbing` uses **Hill Climbing** (only accepts improvements, can get stuck).
- The final cost is shown so the two methods can be compared.

### 5. Pass Predictor (Bayesian Network)
Asks three yes / no / skip questions and predicts the chance of passing by **inference by enumeration** on a Bayesian network:

```
Attendance     StudyHours
      \         /
      Understanding      Assignments
              \             /
                    Pass
```
- Questions: attendance above 75 percent? study more than 2 hours a day? all assignments submitted?
- You can **skip** any question; the missing evidence is simply left out of the calculation.
- Output: chance of good understanding, chance of passing, and advice (on track / improve attendance and study time / high risk).

```
You: will i pass
Assistant: Is your attendance above 75 percent? Say yes, no, or skip.
You: yes
...
Assistant: Based on the Bayesian network, chance of good understanding is 60 percent and chance of passing is 72 percent.
```

### 6. Focus Tracker (Hidden Markov Model)
You describe what you did in each 15 minute block of a study session using the words `reading`, `notes`, `phone` or `break`. The HMM guesses the **hidden state** (Focused or Distracted) of every block.

- **Viterbi algorithm** gives the most likely sequence of hidden states.
- **Forward algorithm** gives the probability of the whole activity sequence.
- Output: a block-by-block table and the percentage of the session you were focused.

```
You: check my focus
You: reading reading phone notes
Block | Activity | Hidden state
    1 | reading  | Focused
    ...
You were focused for about 75 percent of your session.
```

### 7. Student Group Clustering (EM Algorithm)
"Which type of student am I?" The **EM (Expectation-Maximisation) algorithm** fits a Gaussian Mixture Model to the study hours and attendance of 60 students (data is generated with a fixed seed, so results are repeatable). The group of each student is a **hidden variable** that EM discovers on its own.

- Shows the **log-likelihood** at each iteration (it only goes up) and when EM converges.
- Prints the three learned groups: **Consistent achiever, Average learner, Needs support**, with their share, average study hours and average attendance.
- Then asks for **your** study hours and attendance and tells which group you most likely belong to, with the probability and advice.

```
You: which group am i
You: 4
You: 85
With 4 hours of study and 85 percent attendance, you are most likely an Average learner (78 percent sure). ...
```

### 8. Campus Escape (Wumpus World)
A **logical agent** explores a 4x4 cave (new random world every time) with pits, a Wumpus and gold. It cannot see the map and only receives percepts: **Breeze** (next to a pit), **Stench** (next to the Wumpus) and **Glitter** (gold here).

How it thinks:
- Its knowledge base stores every percept.
- It uses **model checking**: a cell is marked safe only when it has no pit and no Wumpus in *every* world that agrees with what it knows.
- If it can pinpoint the Wumpus, it shoots it with its single arrow.
- If nothing is provably safe, it takes the **least risky guess** (using pit probabilities) and says so.
- Scoring: -1 per move, -10 for the arrow, +1000 for escaping with the gold, -1000 for dying.

The output shows the step-by-step reasoning, the final map and the score. (Because it sometimes has to guess, it can occasionally lose, as a real agent would.)

### 9. Brain Games
- **Towers of Hanoi** (`play hanoi with 4 disks`): solved by **recursion**; shows every move and confirms the 2^n - 1 move count. Supports 1 to 6 disks (default 3).
- **8 Puzzle** (`play 8 puzzle`): generates a random solvable puzzle and solves it with **A\* using Manhattan distance**; shows the start state, goal state, the moves of the blank and the number of states explored.

### 10. Syllabus Coverage
Type `syllabus` to print a table of every lab topic, the assistant feature that uses it, and an example command.

### 11. General Assistant Features
- **Wikipedia answers:** `what is ...`, `who is ...`, `what are ...`, `tell me about ...`, `explain ...`, `define ...`, `wikipedia ...` return a short summary (needs internet). Ambiguous topics pick the first suggested page; unknown topics get a polite "not found".
- **Small talk:** `hello`, `hi`, `hey`, `good morning`, `how are you`, `who are you`, `what is your name`, `who made you`, `thanks`, `i am bored`.
- **Time and date:** `time`, `date`.
- **Jokes:** `tell me a joke` (uses `pyjokes`, with a built-in list as backup).
- **Websites:** `open youtube`, `open google`, `open github`, `open gmail`, `open stackoverflow`.
- **Google search:** `search python tutorial`.
- **Help:** `help` shows every command.
- **Exit:** `bye`, `exit`, `quit` or `stop`.

---

## The Web Interface

Run `python app.py` and use the chat page in the browser:

- Chat window with message bubbles; tables, timetables and move lists appear in a code-style box.
- A small **tag under each answer** shows which feature and algorithm was used (for example "Pass Predictor · Bayesian Network").
- **Quick-action buttons** for every main feature. During yes / no questions they switch to **Yes / No / Skip** buttons.
- **Microphone button** to speak a command, and **spoken replies** (toggle with the Voice button). Works in Chrome, Edge and Safari.
- **New chat** button, and automatic light / dark theme.
- Works on a phone-size screen too.

---

## How It Works

1. **Input:** the user types or speaks a command.
2. **Intent detection:** the command is matched against keywords (in a fixed order) to find what the user wants. Small talk is checked early so greetings are never missed, and specific features are checked before general ones.
3. **Action:** the matching module runs (for example `dstar.py` for re-planning).
4. **Multi-step questions:** features that need more input (pass predictor, focus tracker, EM) ask follow-up questions and wait for the answers.
5. **Output:** the answer is shown (and spoken). The loop continues until the user says `bye`.

The web server (`app.py`) reuses the same intent detection and modules as the terminal version, so both behave exactly the same. It uses only Python's standard library.

---

## Project Structure

```
ai-virtual-assistant/
├── main.py                    # main loop, intent detection, help, syllabus table (terminal)
├── app.py                     # web UI server (standard library only)
├── ui/
│   └── index.html             # chat interface (buttons, voice in/out)
├── requirements.txt           # wikipedia, pyjokes
├── requirements-voice.txt     # optional: terminal voice mode
├── README.md
└── modules/
    ├── speech.py              # voice input / output (terminal mode)
    ├── utilities.py           # small talk, time, date, web, Wikipedia, jokes
    ├── campus_navigation.py   # A*, BFS, DFS, IDS + campus map
    ├── dstar.py               # D* Lite live re-planning
    ├── study_planner.py       # Simulated Annealing, Hill Climbing
    ├── pass_predictor.py      # Bayesian Network
    ├── focus_tracker.py       # Hidden Markov Model
    ├── em_clustering.py       # EM algorithm (Gaussian Mixture)
    ├── wumpus_world.py        # Wumpus World logical agent
    └── brain_games.py         # Towers of Hanoi, 8 Puzzle
```

---

## How to Run

**Web UI (recommended)** — works on Mac, Windows and Linux with Python 3.8 or newer, nothing to install:

```bash
python app.py
```

Then open **http://127.0.0.1:8000** (it opens automatically). On Windows you can also use `py app.py`; on Mac `python3 app.py`. If port 8000 is busy, the next free port is used and printed in the terminal. Stop with `Ctrl+C`.

For Wikipedia answers and real jokes, install the two small libraries (optional):

```bash
pip install -r requirements.txt
```

**Terminal version (optional):**

```bash
python main.py           # typing mode
python main.py --voice   # voice mode (needs a microphone and requirements-voice.txt)
```

If voice libraries are not installed, the assistant still works in typing mode. The web UI does not need them, because it uses the browser for voice.

---

## Sample Commands

```
hello
route from main gate to hostel
route from library to cafeteria using bfs
compare routes from medical center to sports ground
reroute from main gate to hostel if library is blocked
make my study timetable
make my study timetable using hill climbing
will i pass
check my focus
which group am i
play wumpus world
play hanoi with 4 disks
play 8 puzzle
what is machine learning
who is alan turing
tell me a joke
time
date
open youtube
search python tutorial
syllabus
help
bye
```

---

## Testing Done

- **A\*** was checked against Dijkstra's algorithm for every pair of places: always the shortest route. (Path lengths were set so the straight-line heuristic never overestimates.)
- **D\* Lite** was checked on 2,672 random replanning cases: every result matched the true shortest path, and it did less total work than restarting A*.
- **Wumpus World** was played 600 times on random worlds: the agent never died because of faulty logic, only after a flagged risky guess.
- **EM** log-likelihood increases at every iteration, and the three true groups were recovered from 30 different starting points.
- **Bayesian Network** result for no evidence (P(pass) = 0.753) matches an independent hand calculation.
- All commands were run end to end through the web server, and the app was run under simulated Windows conditions (Windows line endings, folder name with spaces, Windows console encoding).

## Limitations

- The campus map, subjects and student data are sample data made for this project.
- Wikipedia answers and Google search need an internet connection.
- Browser voice input needs Chrome, Edge or Safari and microphone permission.
- The Wumpus agent sometimes has to guess, so it can lose.

---

## Technologies

Python 3 (standard library for the web server and all algorithms), HTML / CSS / JavaScript for the interface, `wikipedia` and `pyjokes` (optional), `pyttsx3`, `SpeechRecognition` and `PyAudio` (optional, terminal voice mode only).

---

## Lab Syllabus Coverage

| Lab topic | Where it is used |
|---|---|
| DFS, BFS, Iterative Deepening Search | Campus Navigation, Route Comparison |
| Simulated Annealing, Hill Climbing | Study Timetable |
| A* | Campus Navigation, 8 Puzzle |
| D* (D* Lite) | Live Re-planning |
| Wumpus World | Campus Escape game |
| 8 Puzzle, Towers of Hanoi | Brain Games |
| Bayesian Network | Pass Predictor |
| EM Algorithm | Student Group Clustering |
| Hidden Markov Model | Focus Tracker |
| **Build a Virtual Assistant** | This whole project |

Type `syllabus` in the assistant to see this table.
