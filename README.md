# starter-town-tactics
A tactical RPG project, focused on implementing AI and architecture concepts for use in my day job

# 🧠 Tactical RPG Project: Learning to Build, Code, and Think Like an SDM

## 🚩 Overview
This repo documents your journey from zero coding experience to building a tactical RPG from scratch, while learning AI, architecture, and software development principles that align with Amazon SDM standards.

## 🎯 Project Goals
- Build a Final Fantasy Tactics-style tactical RPG in Python using PyGame
- Use this project to learn AI, software architecture, and coding fundamentals
- Document and publish technical milestones, postmortems, and specs
- Demonstrate SDM-level decision-making, system design, and leadership

---

## ✅ 20-Week Study & Build Checklist

| Week | Build Goal | Study Focus | Checkpoint |
|------|------------|-------------|------------|
| 1 | Set up GitHub, Cursor, PyGame project | Python basics | GitHub repo initialized |
| 2 | Render tile grid, move one unit | Coordinates, PyGame drawing | Unit moves on grid |
| 3 | Add turn loop | Game loop logic | Player + AI take turns |
| 4 | Add combat: move, attack, end turn | OOP & states | Combat functional |
| 5 | Add AI: simple attack behavior | AI flow, decision trees | Enemy acts alone |
| 6 | Add classes/stats | Encapsulation | Unique unit stats working |
| 7 | Add death logic + animation | Sprite handling | Units disappear on death |
| 8 | Add items/spells (placeholders) | JSON modeling | Inventory working |
| 9 | Add terrain types | Pathfinding basics | Can't walk through walls |
| 10 | Write README + diagram | Architecture writing | README + diagram done |
| 11 | Build map selector UI | Scene switching | Menu picks maps |
| 12 | Add save/load | Serialization | Game resumes from file |
| 13 | Refactor modules | Code architecture | Codebase clean & modular |
| 14 | Bugfix postmortem | Debugging + RCA | Markdown write-up added |
| 15 | Add GPT-assisted enemy AI | Prompting, integration | GPT guides enemy turns |
| 16 | Win/loss conditions | Game state control | Game ends properly |
| 17 | Add music and polish | UX layer | Audio and menus clean |
| 18 | Package or deploy | Streamlit or PyInstaller | Game runs standalone or in browser |
| 19 | Write tech spec (e.g., skill tree) | Technical writing | Markdown spec written |
| 20 | Final retrospective + demo | SDM storytelling | Final video + write-up |

---

## 📂 Folder Structure
```
root/
├── game/                # Game code lives here
│   ├── main.py
│   ├── combat.py
│   ├── grid.py
│   ├── units.py
│   └── ai.py
├── docs/                # Project documentation
│   ├── dev_journal.md
│   ├── bug_postmortems.md
│   ├── architecture.md
│   ├── skill_tree_spec.md
│   └── retrospective.md
├── assets/              # Art, sound, music (optional)
├── README.md            # Project overview
└── requirements.txt     # Python packages
```

---

## 📚 Getting Started With GitHub (Step-by-Step)

### 1. 🔧 Create a GitHub Account
- Go to [https://github.com/](https://github.com/) and sign up.

### 2. 📁 Use Your Project Repository
- Go to your project: [https://github.com/rdowning07/starter-town-tactics](https://github.com/rdowning07/starter-town-tactics)
- Clone it:
```bash
git clone https://github.com/rdowning07/starter-town-tactics.git
cd starter-town-tactics
```

### 3. 💻 Start Working Locally
- Make sure you’re in the project folder
- Start editing and committing your work

```bash
# Track all changes
git add .

# Commit your message
git commit -m "Add Week 1 setup: grid + player movement"

# Push to GitHub
git push origin main
```

### 4. ✅ Use GitHub Projects for Kanban
- Go to your repo → Click "Projects"
- Create a new project board
- Add columns: Backlog, In Progress, Done
- Create tasks as issues, drag between columns as you work

---

## 🔗 Links You Should Bookmark
- [GitHub Docs (Official)](https://docs.github.com/en)
- [GitHub Learning Lab](https://lab.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Markdown Guide](https://www.markdownguide.org/)
- [PyGame Docs](https://www.pygame.org/docs/)
- [RedBlob Pathfinding](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
- [Behavior Trees Overview](https://gamedeveloper.com/programming/behavior-trees-for-ai-how-they-work)

---

You're ready to build, document, and share your journey like an SDM in training.
Let me know when you're ready for me to generate:
- Initial GitHub issues
- First code template (`main.py` + grid system)
- AI prompt templates for enemy decision-making
