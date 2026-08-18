# 🏊 42 Piscine Exam Simulator

Welcome to the ultimate **42 Piscine Exam Simulator**! 🚀

This project is a highly realistic, offline simulation of the infamous 42 Piscine Exams (Exam00, Exam01, Exam02, Exam03). It faithfully reproduces the behavior of the real **Moulinette** and the `examshell` environment, including:
- 🎲 Dynamic difficulty scaling based on your successes and failures.
- 📂 Automatic workspace generation (`rendu` and `subjects`).
- 📝 Realistic trace logs (`trace/`) exactly like the real exam.
- 💾 Automatic session archiving so you never lose your practice history.
- 🌈 A beautiful TrueColor Cyberpunk ASCII boot sequence!

---

## 🛠️ Installation & Usage

The simulator is written in pure Python and requires **no external dependencies**. It is designed to run anywhere, whether you are practicing at home on Windows or warming up on a campus iMac.

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/42-exam-simulator.git
cd 42-exam-simulator
```

### 2. Choose your version
We provide three specialized launchers depending on your operating system. They all use the same exercise database (`pool/`) but are optimized for terminal handling on their respective systems:

#### 🍎 macOS (42 School iMacs)
Perfect for running natively on the school's Apple machines.
```bash
chmod +x examshell_mac.py
./examshell_mac.py
```
*(Or simply `python3 examshell_mac.py`)*

#### 🐧 Linux (Ubuntu / Debian)
Optimized for 42 campus machines booting on a Linux session. It hooks into the native `gnome-terminal`.
```bash
chmod +x examshell_linux.py
./examshell_linux.py
```
*(Or simply `python3 examshell_linux.py`)*

#### 🪟 Windows
Perfect for training at home. It hooks into PowerShell.
```powershell
python examshell.py
```

---

## 🎮 How it works

1. **Select your Exam**: Upon launch, the simulator will ask you to pick an exam (e.g., `Exam00`, `Exam01`, `Exam02`, `Exam03`).
2. **Assignments**: Type `status` or `subject` to get your first assignment.
3. **Workspace**: A `rendu/` directory will pop up. This is your workspace. Inside, you will find a `subjects/` folder containing the instructions for your current exercise.
4. **Grading**: Once you have written your `.c` file in the `rendu/` directory, simply type:
   ```bash
   grademe
   ```
   - **SUCCESS**: You get points and move to a harder level.
   - **FAILURE**: You stay on the same exercise. Check the `trace/` folder for compiler errors or diff outputs!

---

## 📁 The `pool/` Database
This simulator uses a massive, community-sourced database of exercises, rigorously classified by difficulty level to match the real Moulinette's internal algorithms. 
*(Includes tricky edge-case exercises like `inter`, `ft_split`, and bitwise operators!)*

Good luck, and may the Moulinette be with you! 🍀
