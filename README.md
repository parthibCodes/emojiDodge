🎮 Emoji Dodge: A Python Survival Game Built with Pygame
========================================================

> "Stay alive. Dodge. Survive. Spin your luck."

🧠 Project Overview
-------------------

**Emoji Dodge** is a casual survival game made using **Python** and **Pygame**. You control an emoji character that must dodge falling obstacles. The longer you survive and the more obstacles you dodge, the higher your score. It features power-ups, a spinning reward wheel, dynamic day-night mode, and a combo system to spice things up.

🔧 Tech Stack
-------------

*   **Language:** Python
    
*   **Library:** Pygame
    
*   **Tools:** PyCharm, custom emoji font rendering
    

🎮 Game Features
----------------

### 🧍 Player Controls

*   Move left/right using **arrow keys**
    
*   Player is represented by an **emoji** (customizable pressing the key 'C')
    

### 🚫 Obstacles

*   Randomly falling objects that the player must avoid
    
*   Speed increases over time (difficulty scaling)
    

### 🛡️ Lives System

*   Player has 3 lives
    
*   Short invincibility after getting hit to prevent instant death
    

### ⚡ Power-Ups

*   **Savior Buddy:** Gives bonus life or shields
    
*   **Slow Time:** Temporarily slows all falling objects
    

### 🌙 Day-Night Cycle

*   Background switches between day and night every 30 seconds
    

### 💥 Combo System

*   Earn combo bonuses by dodging multiple obstacles in a row
    
*   Bonus points for perfect dodging streaks
    

### 🌀 Spin-the-Wheel (Survivor Buddy)

*   After a game-over, you get a **chance to spin** for a reward (extra life, slow time, etc.)
    
*   Adds unpredictability and fun
    

🧑‍💻 Behind the Scenes
-----------------------

### Class Structure

*   GameSettings: Manages game state like score, speed, lives, power-up intervals
    
*   reset\_game(): Cleanly resets all states without restarting the program
    
*   show\_game\_over(): Displays final score, game over screen, and triggers spin wheel
    

### Custom Fonts & Emojis

*   Used SysFont for base UI
    
*   Rendered emojis as text using emoji fonts for universal cross-platform support
    

### Game Loop Highlights

*   Handles real-time physics (collision detection)
    
*   Uses pygame.time.get\_ticks() for power-up cooldowns
    
*   Smooth animations and overlay transitions for game-over effects
    

📸 Screenshots / Demo GIF
-------------------------


![Screenshot 2025-06-06 161753](https://github.com/user-attachments/assets/5bcf4c6e-5ad8-47e6-8a85-c4508b63098c)
![image](https://github.com/user-attachments/assets/da32dd78-34fd-4750-a862-ac9061811752)
![image](https://github.com/user-attachments/assets/57634c85-e4f6-4d1f-80f5-b2c7e07bb345)


🚀 How to Run the Game
----------------------

### Requirements:

*   Python 3.x
    
*   pygame (Install via pip install pygame)
    

### Run:

`   python main.py   `

🔮 Future Plans
---------------

*   Add high score leaderboard
    
*   Sound effects and background music
    
*   Unlockable emojis with achievements
    
*   Mobile port using Kivy or Godot
    

🧠 Lessons Learned
------------------

*   Mastered game loops, event handling, collision detection with Pygame
    
*   Learned about clean architecture using class-based state management
    
*   Got better at debugging game states and integrating randomness (spin logic)
    

✨ Final Thoughts
----------------

**Emoji Dodge** was a passion project mixing logic, fun, and design. It helped me understand not just how to make games, but how to structure code that's extensible and modular. It’s also a stepping stone toward more complex game or AI-driven interaction projects.
