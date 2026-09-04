# CODEVISION

> *"Practice. Build. Visualize. Understand."*

CodeVision is a comprehensive, production-grade educational coding and project-learning platform engineered from scratch. It integrates a LeetCode-style multi-language Online Judge, an interactive custom Code Execution Visualizer (without relying on third-party tools), a comprehensive DSA Visualizer (Sorting, Searching, Graphs, Trees, DP, Big-O Complexity), a 2-panel Project Lab with milestone testing and live skill tracking, Timed Contests, Placement & Interview Preparation, Learning Paths, and data-driven Skill Analytics.

---

## 🌟 Core Modules & Architecture

1. **Explore & Home**: High-impact portal introducing platform capabilities and fast-track learning routes.
2. **Problem Library (60+ Real DSA Questions)**: Curated repository spanning Arrays, Strings, Linked Lists, Stacks, Queues, Trees, Heaps, Graphs, Sorting, Searching, Dynamic Programming, Greedy, Recursion, Backtracking, Bit Manipulation, and Math.
3. **Multi-Language Online Judge**:
   - Subprocess sandbox with timeout protection, memory limits, and output normalization.
   - Evaluates against public and strictly protected hidden test cases.
   - Supported languages: **Python 3**, **JavaScript (Node.js)**, **C++ (g++)**, **Java**, and **C (gcc)**.
   - System compiler detection with fallback notices.
4. **Code Execution Visualizer**:
   - Custom AST and frame-stepping tracer built in Python.
   - Step-by-step navigation (First, Prev, Play, Pause, Next, Last, Speed, Slider).
   - Real-time Variables Table, Dynamic Memory Heap References, Call Stack, and Standard Output.
5. **DSA & Algorithm Visualizer**:
   - Sorting: Bubble Sort, Selection Sort, Insertion Sort, Quick Sort.
   - Searching: Binary Search, Linear Search.
   - Interactive Big-O Complexity curves ($O(1)$, $O(\log n)$, $O(n)$, $O(n \log n)$, $O(n^2)$).
6. **Project Lab**:
   - Real-world software engineering practice: Expense Tracker, Student Management System, Educational ML House Price Predictor, Spam SMS Classifier, URL Shortener.
   - Divided into structured milestones with live test verification and skill delta tracking.
7. **Timed Contests**:
   - 30, 60, and 90-minute challenges with live countdown clock, wrong-answer penalty, and real-time standings.
8. **Interview Preparation & Company Filters**:
   - Placement MCQs and quizzes for DSA, OOP, DBMS, OS, and Computer Networks.
   - Company tags for TCS, Infosys, Wipro, Accenture, Cognizant, Amazon, Microsoft, Google, Zoho, and Freshworks.
9. **Learning Paths**: Structured 3-stage roadmap (Beginner Foundation $	o$ Core Data Structures $	o$ Advanced Algorithms).
10. **Student Dashboard & Analytics**:
    - Problem solved metrics (Easy, Medium, Hard breakdown), Streaks, Points, Rating, Accuracy, Best Runtime.
    - Chart.js Skill Radar & 30-day GitHub-style coding heatmap.
   - Adaptive weak-topic detection and recommendations.
11. **Leaderboard & Gamification**:
    - Global rankings sorted by points with problem solve counts as tie-breaker.
    - 15 unlockable milestone badges.
12. **Student Portfolio & Notes**:
    - Shareable verified portfolio cards showing completed project scores and skill proficiencies.
    - Personal problem notes and revision bookmarks.
13. **Admin Panel (`/admin`)**:
    - Full CRUD management for Problems, Test Cases, Projects, Milestones, Users, and Contests.

---

## 🛠 Technology Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy, Werkzeug (PBKDF2 SHA-256 password hashing)
- **Database**: SQLite (Development) / PostgreSQL-ready SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, FontAwesome, Monaco Editor, Chart.js
- **Execution & Tracing**: Python AST parsing, `sys.settrace` frame analyzer, Subprocess sandbox

---

## 🚀 Installation & Setup (Windows)

```powershell
# 1. Navigate to project root
cd D:\PROJECTS\CodeVision-AI

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application (Tables and 60+ questions are auto-seeded on first run)
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🐧 Installation & Setup (Linux / macOS)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

---

## 🔑 Default Credentials

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full access to `/admin` dashboard & management |
| **Student** | `student` | `student123` | Demo student profile with solved problems & stats |

---

## 🔒 Security & Sandbox Architecture

- **Development Sandbox**: Subprocess execution with strict 5.0-second timeouts, per-execution isolated temporary directories, process isolation, memory monitoring, and output truncation (max 50 KB).
- **Hidden Test Case Protection**: Hidden inputs and outputs are evaluated internally on the judge server and never returned in API payloads.
- **Production Architecture**: Designed for containerized Docker/gVisor microVM runners with:
  - CPU quotas (`--cpus=0.5`)
  - Memory caps (`--memory=128m`)
  - Read-only root filesystem
  - Disabled network (`--network=none`)
  - Non-root unprivileged execution user

---

## 🧪 Verification & Testing

To run the full automated verification test suite:

```powershell
python -m unittest scratch/test_suite.py
```

Tests verify:
- Registration, login, logout, and password hashing
- Problem library filtering, multi-topic searches, and hidden test encapsulation
- Online Judge custom run and multi-case submissions
- Execution step tracer with variables, heap memory, and call stack capture
- Static code quality and complexity analysis
- DSA sorting and searching visualization traces
- Project Lab milestone validation
- Admin APIs and compiler status detection
