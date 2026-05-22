PAO Memory Trainer

This is a comprehensive, terminal-based Python application designed to help you build, memorize, and master the Person-Action-Object (PAO) mnemonic system. The PAO system is a highly effective memory technique used by memory athletes to remember long sequences of numbers or playing cards by grouping them into memorable, bizarre visual images.
Program Overview

The PAO Memory Trainer handles everything from the initial data entry of your 100 PAO mappings (numbers 00 through 99) to rigorous daily testing. The program tracks your progress, logs your fastest translation times, manages daily/weekly study goals, and features live-updating terminal graphics.

Primary Goals

    List Generation: Provide a streamlined interface to build and edit your 00-99 PAO list without leaving the terminal.

    Mnemonic Reinforcement: Use a targeted flashcard training system to drill individual number mappings into your long-term memory.

    Speed Translation: Train your brain to instantly recognize a 6-digit chunk and translate it into a Person, Action, and Object as fast as possible.

    Memory Competitions: Simulate real-world memory sports by generating massive random number strings and giving you a fixed countdown timer to memorize them.

How to Use the Program

Prerequisites: * Python 3.x installed.

    A Windows operating system (this script utilizes Windows-specific libraries like msvcrt for live keystroke capturing and winsound for audio).

Getting Started:

    Run the script from your terminal: python pao_training.py.

    The program will automatically generate the required PAO Data and config folders upon first launch.

    Type edit or add at the main menu to open the PAO Data Editor.

    Begin assigning a Person, Action, and Object to the numbers 00 through 99. You must complete at least one full PAO before the game modes unlock.

    Once you have populated your list, select one of the three game modes from the main menu to begin training.

Key Features & Game Modes

    The Data Editor: A live-updating grid that shows which numbers you have completed. It checks for duplicates in real-time across your dataset so you don't accidentally assign the same action or object to two different people.

    Training Mode: A flashcard-style drill for your mappings. It features an adaptive 3-tier hint system that slowly reveals the initials and word shapes of your target answer if you get stuck.

    Speed Recall: The program generates a string of random numbers (ranging from 18 to 120 digits depending on difficulty) and times how long it takes you to type out the correct PAO sentences. It tracks your personal best times down to the tenth of a second.

    Countdown Mode: A two-phase memorization challenge. Phase 1 provides a massive block of numbers and a live countdown timer for you to memorize them. Phase 2 clears the screen and requires you to recall the string from memory.

    Progress Tracking: The software tracks your longest correct answer streaks, calculates your daily/weekly study goals, and displays a comprehensive scoreboard on the main menu.

Details You Might Miss (Under the Hood)

    Smart Text Parsing: You do not need to type perfectly to get a correct answer. The program features a custom text cleaner that strips away punctuation, ignores stop words (like "a", "the", "is", "to"), and stems suffixes. For example, if your action is "running", typing "run" will be marked as correct.

    Multiple Variations: In the Data Editor, you can use semicolons to add acceptable variations for a single item. Typing guitar; electric guitar means the program will accept either answer as correct during testing.

    Inferred Letter Mapping: The program attempts to automatically learn the initials of your Persons (e.g., 07 = James Bond = J B) to power the hint system. You can manually edit these letter mappings by typing change during Training Mode.

    Resume Training: If you quit in the middle of a Training Mode session, the program saves the exact "deck" of unused numbers so you can pick up right where you left off later.

    Dynamic Menus: You can type quit to exit, edit to change your PAO numbers, or open to immediately pop open the raw text files in Windows File Explorer from almost any prompt in the game.
