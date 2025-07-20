# 🛠️ Starter Town Tactics — Development Plan

## 🌟 Primary Goal:

Use the development of a turn-based tactics game to build software development fluency, demonstrate architectural thinking, and gain practical AI skills — ultimately to **prepare for Amazon SDM or PMT roles**.

---

## 📂 Project Structure

# 🛠️ Starter Town Tactics — Development Plan

## 🌟 Primary Goal:

Use the development of a turn-based tactics game to build software development fluency, demonstrate architectural thinking, and gain practical AI skills — ultimately to **prepare for Amazon SDM or PMT roles**.

---

## 📂 Project Structure

# 🛠️ Starter Town Tactics — Development Plan

## 🌟 Primary Goal:

Use the development of a turn-based tactics game to build software development fluency, demonstrate architectural thinking, and gain practical AI skills — ultimately to **prepare for Amazon SDM or PMT roles**.

---

## 📂 Project Structure

starter-town-tactics/
├── game/ # All source code
├── docs/
│ └── dev-log.md # Weekly dev log (journal of progress and reflections)
│ └── plan.md # Long-term development and learning plan
├── requirements.txt # Python dependencies
└── README.md # Project overview and setup instructions


---

## 🔁 Weekly Workflow

Each week, follow this rhythm:

1. **Plan the Week**

   - Define learning goals and dev milestones.
   - Use `docs/dev-log.md` to log weekly **goals** at the top.

2. **Build**

   - Work iteratively on the game and/or architecture.
   - Commit early, commit often. Use descriptive messages.

3. **Reflect and Log**

   - At the end of the week (or milestone):
     - Update `docs/dev-log.md` with:
       - `### Goals`
       - `### Accomplishments`
       - `### Reflections`
       - `### Next Up`
     - Commit with:
       ```bash
       git add docs/dev-log.md
       git commit -m "Add Week [N] dev log entry"
       git push origin main
       ```

4. **Push and Review**

   - Push all updates to GitHub.
   - Review the commit log to ensure your history is clean and informative.

---

## 🗓️ Dev Log Template (`docs/dev-log.md`)

```markdown
---

## Week [N] — [Title or Theme]

### Goals:
- [e.g. Implement basic input handling]
- [e.g. Practice event-driven architecture]

### Accomplishments:
- [e.g. Wrote `input_handler.py` to abstract keyboard input]
- [e.g. Learned how Pygame event queue works]

### Reflections:
- [e.g. Struggled with key repeat but learned how to handle it via flags]
- [e.g. Feeling more confident with game loops and input models]

### Next Up:
- [e.g. Add basic tile map rendering]
- [e.g. Start architecting game state transitions]

---
| Week  | Theme                      | Outcome                                             |
| ----- | -------------------------- | --------------------------------------------------- |
| 1     | Setup & Hello World        | Pygame installed, repo initialized, dev log started |
| 2     | Game Loop & Input          | Input handling system, key events                   |
| 3     | Map & Tiles                | Tile grid rendering, camera prototype               |
| 4     | Entity System              | Basic units with position/state                     |
| 5     | Turn Order & Phases        | Simple turn manager & unit selection                |
| 6–10  | Core Combat Loop           | Movement, attack, health                            |
| 11–14 | AI Behavior & Agents       | Rule-based + simple ML (optional)                   |
| 15–18 | Menus, Feedback & Polish   | UX enhancements, sound, effects                     |
| 19–20 | Final Polish, Docs & Demos | README, gameplay loop, documentation                |



