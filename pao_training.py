import os
import random
import string
import json
import time
import sys
import msvcrt
import winsound
import shutil
from datetime import datetime, timedelta

# ==========================================
# WINDOWS WORKING DIRECTORY 
# ==========================================

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

PAO_DATA_DIR = "PAO Data"
CONFIG_DIR = "config"

def initialize_data_folder():
    """Ensures the PAO Data and config directories exist on startup."""
    if not os.path.exists(PAO_DATA_DIR):
        os.makedirs(PAO_DATA_DIR)
        
    for filename in ['person.txt', 'action.txt', 'object.txt']:
        file_path = os.path.join(PAO_DATA_DIR, filename)
        if not os.path.exists(file_path):
            if os.path.exists(filename):
                shutil.move(filename, file_path)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    pass
                    
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
        
    legacy_stats = 'stats.json'
    new_stats = os.path.join(CONFIG_DIR, 'stats.json')
    if os.path.exists(legacy_stats) and not os.path.exists(new_stats):
        shutil.move(legacy_stats, new_stats)

initialize_data_folder()

# ==========================================
# COLORS & AUDIO
# ==========================================
os.system("") 

C_BLACK = "\033[90m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN = "\033[96m"
C_WHITE = "\033[97m"
C_LAVENDER = "\033[38;5;141m"  
C_SLATE = "\033[38;5;103m"     
C_ORANGE = '\033[38;5;208m'

C_BOLD = "\033[1m"
C_RESET = "\033[0m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==========================================
# ASCII ART FONT
# ==========================================
ASCII_FONTS = {
    '0': [" ███ ", "█   █", "█   █", "█   █", " ███ "],
    '1': ["  █  ", " ██  ", "  █  ", "  █  ", " ███ "],
    '2': [" ███ ", "█   █", "  ██ ", " █   ", "█████"],
    '3': ["████ ", "    █", "  ██ ", "    █", "████ "],
    '4': ["   █ ", "  ██ ", " █ █ ", "█████", "   █ "],
    '5': ["█████", "█    ", "████ ", "    █", "████ "],
    '6': ["  ██ ", " █   ", "████ ", "█   █", " ███ "],
    '7': ["█████", "   █ ", "  █  ", " █   ", "█    "],
    '8': [" ███ ", "█   █", " ███ ", "█   █", " ███ "],
    '9': [" ███ ", "█   █", " ████", "   █ ", " ██  "],
    ':': ["   ", " █ ", "   ", " █ ", "   "]
}

def print_huge_number(num_str):
    print("\n")
    for i in range(5):
        line = ASCII_FONTS[num_str[0]][i] + "     " + ASCII_FONTS[num_str[1]][i]
        print(f"{C_CYAN}{C_BOLD}" + line.center(40) + f"{C_RESET}")
    print("\n")

def play_victory_jingle():
    winsound.Beep(523, 150)
    winsound.Beep(659, 150)
    winsound.Beep(784, 150)
    winsound.Beep(1046, 400)

# ==========================================
# Data Ingestion & Live Processing
# ==========================================

def clean_text(text):
    """Deep parses out stop words and stems plurals/suffixes for absolute precision."""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    stop_words = {
        'a', 'an', 'the', 'he', 'him', 'his', 'she', 'her', 'hers', 'it', 'its',
        'they', 'them', 'their', 'theirs', 'i', 'me', 'my', 'mine',
        'we', 'us', 'our', 'ours', 'you', 'your', 'yours',
        'is', 'are', 'was', 'were', 'am', 'be', 'been', 'being',
        'do', 'does', 'did', 'doing', 'have', 'has', 'had', 'having',
        'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must',
        'on', 'in', 'at', 'to', 'for', 'with', 'by', 'about', 'against',
        'between', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'from', 'up', 'down', 'out', 'off', 'over', 'under',
        'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of',
        'this', 'that', 'these', 'those', 'then', 'once', 'here', 'there',
        'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
        'more', 'most', 'other', 'some', 'such', 'only', 'own', 'same', 
        'so', 'than', 'too', 'very', 'just', 'now'
    }
    
    important_words = [word for word in text.split() if word not in stop_words]
    
    cleaned_words = []
    for w in important_words:
        modified = False
        if len(w) > 3:
            if w.endswith('ing'):
                w = w[:-3]
                modified = True
            elif w.endswith('ed'):
                w = w[:-2]
                modified = True
            elif w.endswith('es'):
                w = w[:-2]
                modified = True
            elif w.endswith('s') and not w.endswith('ss'):
                w = w[:-1]
                modified = True
            
            # Reduces things like "shredd" back to "shred" safely
            if modified and len(w) > 2 and w[-1] == w[-2] and w[-1] not in ['s', 'l', 'f']:
                w = w[:-1]
                
        cleaned_words.append(w)
        
    return " ".join(cleaned_words)

def live_input_with_bracket(item_name, existing_val):
    """Custom interceptor that dynamically draws the [clean_text] bracket above the cursor in real time."""
    user_input = ""
    while True:
        display_val = user_input if user_input else existing_val
        
        if user_input.strip().lower() in ['clear', 'reset']:
            bracket_text = f"{C_RED}CLEAR{C_RESET}"
        else:
            variations = [v.strip() for v in display_val.split(';') if v.strip()]
            cleaned_vars = []
            for v in variations:
                cl = clean_text(v)
                if cl and cl not in cleaned_vars:
                    cleaned_vars.append(cl)
            bracket_text = "; ".join(cleaned_vars) if cleaned_vars else ""
        
        sys.stdout.write(f"\r\033[K{item_name} [{bracket_text}]:\n")
        sys.stdout.write(f"\r\033[K> {user_input}")
        sys.stdout.flush()
        
        char = msvcrt.getch()
        if char in (b'\r', b'\n'):
            print()
            return user_input
        elif char == b'\x08':
            if len(user_input) > 0:
                user_input = user_input[:-1]
        else:
            try:
                c = char.decode('utf-8')
                if c.isprintable():
                    user_input += c
            except UnicodeDecodeError:
                pass
        
        sys.stdout.write("\033[1A")

def parse_pao_file(filepath):
    pao_dict = {}
    if not os.path.exists(filepath):
        print(f"Warning: '{filepath}' not found.")
        return pao_dict

    with open(filepath, 'r', encoding='utf-8') as file:
        for index, line in enumerate(file):
            key = str(index).zfill(2)
            valid_entries = [item.strip() for item in line.split(';') if item.strip()]
            pao_dict[key] = valid_entries
            
    return pao_dict

def load_all_pao_data():
    persons = parse_pao_file(os.path.join(PAO_DATA_DIR, 'person.txt'))
    actions = parse_pao_file(os.path.join(PAO_DATA_DIR, 'action.txt'))
    objects = parse_pao_file(os.path.join(PAO_DATA_DIR, 'object.txt'))
    return persons, actions, objects

def get_valid_count():
    persons, actions, objects = load_all_pao_data()
    return sum(1 for i in range(100) if str(i).zfill(2) in persons and persons[str(i).zfill(2)] and str(i).zfill(2) in actions and actions[str(i).zfill(2)] and str(i).zfill(2) in objects and objects[str(i).zfill(2)])

def update_pao_file(filepath, index, new_data):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        lines = []

    while len(lines) <= index:
        lines.append('\n')

    lines[index] = new_data.strip() + '\n'

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def check_for_duplicates(item_name, curr_val, check_dict, persons_dict, target_key):
    while True:
        new_val = live_input_with_bracket(item_name, curr_val)
        if not new_val.strip():
            return new_val
            
        if new_val.strip().lower() in ['clear', 'reset']:
            return new_val
            
        new_vals_clean = [clean_text(x) for x in new_val.split(';') if x.strip()]
        new_vals_clean = [x for x in new_vals_clean if x]
        
        duplicate_key = None
        for key, existing_items in check_dict.items():
            if key == target_key:
                continue 
            existing_clean = [clean_text(x) for x in existing_items]
            existing_clean = [x for x in existing_clean if x]
            
            if any(nv in existing_clean for nv in new_vals_clean):
                duplicate_key = key
                break
                
        if duplicate_key:
            person_name = persons_dict.get(duplicate_key, [f"Unknown ({duplicate_key})"])[0]
            print(f"\n{C_YELLOW}⚠️ Heads up!{C_RESET} This {item_name.lower()} is already in use by {C_CYAN}[{duplicate_key}] {person_name}{C_RESET}.")
            choice = input(f"Would you still like to proceed with this {item_name.lower()}? (y/n)\n> ").strip().lower()
            if choice == 'y':
                return new_val
            else:
                print(f"\n{C_MAGENTA}Let's try a different {item_name.lower()}.{C_RESET}\n")
                continue
                
        return new_val

def print_pao_grid(persons, actions, objects):
    print()
    for row in range(10):
        line = "    "
        for col in range(10):
            num = col * 10 + row
            num_str = str(num).zfill(2)
            has_p = num_str in persons and persons[num_str]
            has_a = num_str in actions and actions[num_str]
            has_o = num_str in objects and objects[num_str]
            
            count = sum([bool(has_p), bool(has_a), bool(has_o)])
            
            if count == 3:
                color = C_GREEN
            elif count > 0:
                color = C_YELLOW
            else:
                color = C_BLACK
                
            line += f"{color}{num_str}{C_RESET}    "
        print(line)
    print()

def manage_pao_data(global_stats):
    prev_count = get_valid_count()
    alert_msg = ""
    
    while True:
        clear_screen()
        print(f"\n{C_MAGENTA}{C_BOLD}")
        print("╔" + "═"*40 + "╗")
        print("║" + "PAO DATA EDITOR".center(40) + "║")
        print("╚" + "═"*40 + "╝")
        print(f"{C_RESET}")
        
        if alert_msg:
            print(alert_msg)
            alert_msg = ""
            
        persons, actions, objects = load_all_pao_data()
        print_pao_grid(persons, actions, objects)
            
        target_str = input(f"{C_BLACK}Enter PAO number to edit (00-99), '{C_RED}clear [num]{C_BLACK}' to wipe, or '{C_MAGENTA}back{C_BLACK}':\n>>> {C_RESET}").strip().lower()
        if target_str in ['back', 'quit', 'exit', 'menu', 'return', 'hub','h']:
            goal = global_stats["goals"].get("daily_encode_goal", 0)
            today_encoded = global_stats["goals"].get("today_encoded", 0)
            current_count = get_valid_count()
            
            if current_count < 100 and goal > 0 and today_encoded < goal:
                left = goal - today_encoded
                confirm = input(f"\n{C_YELLOW}Are you sure? You only have {left} left to reach your daily goal! (y/n){C_RESET}\n>>> ").strip().lower()
                if confirm != 'y':
                    continue
                    
            print(f"\n{C_MAGENTA}Returning to Menu...{C_RESET}")
            time.sleep(0.5)
            clear_screen()
            break
            
        if target_str.startswith('clear ') or target_str.startswith('reset '):
            parts = target_str.split()
            if len(parts) == 2 and parts[1].isdigit():
                target_idx = int(parts[1])
                if 0 <= target_idx <= 99:
                    update_pao_file(os.path.join(PAO_DATA_DIR, 'person.txt'), target_idx, "")
                    update_pao_file(os.path.join(PAO_DATA_DIR, 'action.txt'), target_idx, "")
                    update_pao_file(os.path.join(PAO_DATA_DIR, 'object.txt'), target_idx, "")
                    alert_msg = f"\n{C_GREEN}✅ PAO [{str(target_idx).zfill(2)}] has been entirely cleared!{C_RESET}\n"
                    continue
                    
        try:
            target_idx = int(target_str)
            if not (0 <= target_idx <= 99):
                alert_msg = f"{C_RED}Number must be between 0 and 99.{C_RESET}\n"
                continue
        except ValueError:
            alert_msg = f"{C_RED}Invalid command or number.{C_RESET}\n"
            continue

        target_key = str(target_idx).zfill(2)
        
        curr_p = "; ".join(persons.get(target_key, []))
        curr_a = "; ".join(actions.get(target_key, []))
        curr_o = "; ".join(objects.get(target_key, []))

        print(f"\n{C_CYAN}--- Editing PAO [{target_key}] ---{C_RESET}")
        print("Leave blank and press Enter to keep current value.")
        print("Use semicolons ';' to add variations (e.g., guitar; electric guitar)\n")
        
        new_p = live_input_with_bracket("Person", curr_p)
        new_a = check_for_duplicates("Action", curr_a, actions, persons, target_key)
        new_o = check_for_duplicates("Object", curr_o, objects, persons, target_key)

        if new_p.strip().lower() in ['clear', 'reset']:
            update_pao_file(os.path.join(PAO_DATA_DIR, 'person.txt'), target_idx, "")
        elif new_p.strip(): 
            update_pao_file(os.path.join(PAO_DATA_DIR, 'person.txt'), target_idx, new_p)
            
        if new_a.strip().lower() in ['clear', 'reset']:
            update_pao_file(os.path.join(PAO_DATA_DIR, 'action.txt'), target_idx, "")
        elif new_a.strip(): 
            update_pao_file(os.path.join(PAO_DATA_DIR, 'action.txt'), target_idx, new_a)
            
        if new_o.strip().lower() in ['clear', 'reset']:
            update_pao_file(os.path.join(PAO_DATA_DIR, 'object.txt'), target_idx, "")
        elif new_o.strip(): 
            update_pao_file(os.path.join(PAO_DATA_DIR, 'object.txt'), target_idx, new_o)

        alert_msg = f"\n{C_GREEN}✅ PAO [{target_key}] updated successfully!{C_RESET}\n"
        
        new_count = get_valid_count()
        if new_count > prev_count:
            diff = new_count - prev_count
            global_stats["goals"]["today_encoded"] = global_stats["goals"].get("today_encoded", 0) + diff
            
            goal = global_stats["goals"].get("daily_encode_goal", 0)
            current_today = global_stats["goals"]["today_encoded"]
            
            if goal > 0 and current_today >= goal and (current_today - diff) < goal:
                alert_msg += f"\n{C_GREEN}🎉 Goal Met! You encoded {goal} PAOs today! 🎉{C_RESET}\n"
                
                today_str = datetime.now().strftime('%Y-%m-%d')
                history = global_stats["goals"].get("history", [])
                if today_str not in history:
                    history.append(today_str)
                    global_stats["goals"]["history"] = history
                    play_victory_jingle()
                    
            save_stats(global_stats)
            prev_count = new_count

# ==========================================
# JSON, STATS, & GOALS
# ==========================================

STATS_FILE = os.path.join(CONFIG_DIR, 'stats.json')

def load_stats():
    default_stats = {
        "longest_streak": 0,
        "max_pao_memorized": 0,
        "records": {"speed_easy": 999.9, "speed_medium": 999.9, "speed_hard": 999.9, "speed_hardcore": 999.9},
        "countdown_records": {
            "countdown_easy_pao": 0, "countdown_medium_pao": 0, "countdown_hard_pao": 0, "countdown_hardcore_pao": 0,
            "countdown_easy_digits": 0, "countdown_medium_digits": 0, "countdown_hard_digits": 0, "countdown_hardcore_digits": 0
        },
        "frequencies": {
            "countdown_easy_pao": 0, "countdown_medium_pao": 0, "countdown_hard_pao": 0, "countdown_hardcore_pao": 0,
            "countdown_easy_digits": 0, "countdown_medium_digits": 0, "countdown_hard_digits": 0, "countdown_hardcore_digits": 0,
            "speed_easy": 0, "speed_medium": 0, "speed_hard": 0, "speed_hardcore": 0
        },
        "settings": {"is_chunked": False, "answer_mode": "pao"},
        "letter_mapping": {},
        "goals": {
            "daily_encode_goal": 0,
            "study_goal_type": "none",
            "study_goal_target": 0,
            "current_streak": 0,
            "history": [],
            "today_encoded": 0,
            "today_date": "",
            "last_known_streak": 0
        },
        "saved_training": {
            "pool": [],
            "original_total": 0
        }
    }
    
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            try:
                stats = json.load(f)
                for k, v in default_stats.items():
                    if k not in stats:
                        stats[k] = v
                    elif isinstance(v, dict):
                        for sub_k, sub_v in v.items():
                            if sub_k not in stats[k]:
                                stats[k][sub_k] = sub_v
                                
                if "easy" in stats.get("records", {}):
                    stats["records"]["speed_easy"] = stats["records"].pop("easy")
                    stats["records"]["speed_medium"] = stats["records"].pop("medium")
                    stats["records"]["speed_hard"] = stats["records"].pop("hard")
                    stats["records"]["speed_hardcore"] = stats["records"].pop("hardcore")
                    
                for k in stats["frequencies"]:
                    val = stats["frequencies"][k]
                    if val > 30: val -= 3
                    elif val > 10: val -= 2
                    elif val > 0: val -= 1
                    stats["frequencies"][k] = max(0, val)
                    
                return stats
            except json.JSONDecodeError:
                return default_stats
    return default_stats

def save_stats(stats):
    try:
        with open(STATS_FILE, 'w') as f:
            json.dump(stats, f, indent=4)
    except PermissionError:
        print(f"\n⚠️ WARNING: Could not save to {STATS_FILE}! ⚠️")

def format_time(t):
    return f"{t:.1f}s" if t < 999.9 else "--.-s"

def format_banner_row(label1, val1, label2, val2, color):
    left_text = f"{label1}: {val1}"
    right_text = f"{label2}: {val2}"
    left_pad = max(0, 18 - len(left_text))
    left_part = (" " * left_pad) + f"{label1}: {C_RED}{val1}{color} "
    right_pad = max(0, 19 - len(right_text))
    right_part = f" {label2}: {C_RED}{val2}{color}" + (" " * right_pad)
    return f"{left_part}|{right_part}"

def get_single_most_played(stats):
    freqs = stats.get("frequencies", {})
    if not freqs: return "None", "0"
    
    best_mode, best_val = "None", 0
    for mode, count in freqs.items():
        if count > best_val:
            best_val = count
            best_mode = mode
            
    if best_val == 0: return "None", "0"
    
    parts = best_mode.split('_')
    if parts[0] == 'countdown':
        if len(parts) == 3:
            name = f"Count ({parts[1].title()} - {'PAO' if parts[2]=='pao' else '#'})"
        else:
            name = f"Count ({parts[1].title()})"
        score = stats.get("countdown_records", {}).get(best_mode, 0)
        score_str = str(score)
    elif parts[0] == 'speed':
        name = f"Speed ({parts[1].title()})"
        score = stats.get("records", {}).get(best_mode, 999.9)
        score_str = format_time(score)
    else:
        name = best_mode.title()
        score_str = "0"
        
    return name, score_str

def get_monday(date_obj):
    return date_obj - timedelta(days=date_obj.weekday())

def calculate_streak_val(stats, valid_count):
    goals = stats.get("goals", {})
    history = set(goals.get("history", []))
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    
    if valid_count < 100:
        streak = 0
        check_date = today
        if today_str not in history:
            check_date -= timedelta(days=1)
            
        while check_date.strftime('%Y-%m-%d') in history:
            streak += 1
            check_date -= timedelta(days=1)
        return streak
    else:
        g_type = goals.get("study_goal_type", "none")
        target = goals.get("study_goal_target", 1)
        
        if g_type in ["daily", "none"]:
            streak = 0
            check_date = today
            if today_str not in history:
                check_date -= timedelta(days=1)
            while check_date.strftime('%Y-%m-%d') in history:
                streak += 1
                check_date -= timedelta(days=1)
            return streak
        elif g_type == "weekly":
            history_mondays = {}
            for d_str in history:
                d = datetime.strptime(d_str, '%Y-%m-%d').date()
                mon = get_monday(d)
                history_mondays[mon] = history_mondays.get(mon, set())
                history_mondays[mon].add(d)

            streak = 0
            curr_mon = get_monday(today)
            check_mon = curr_mon

            if len(history_mondays.get(check_mon, set())) >= target:
                streak += 1
                check_mon -= timedelta(days=7)
            elif len(history_mondays.get(check_mon, set())) < target:
                check_mon -= timedelta(days=7)

            while len(history_mondays.get(check_mon, set())) >= target:
                streak += 1
                check_mon -= timedelta(days=7)
            return streak

def get_streak_info(stats, valid_count):
    streak = calculate_streak_val(stats, valid_count)
    goals = stats.get("goals", {})
    history = set(goals.get("history", []))
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    
    if valid_count < 100:
        prog = goals.get("today_encoded", 0) if goals.get("today_date") == today_str else 0
        target = goals.get("daily_encode_goal", 0)
        return f"Daily Encode Progress: {prog}/{target}", f"Active Streak: {streak} Days"
    else:
        g_type = goals.get("study_goal_type", "none")
        target = goals.get("study_goal_target", 1)
        
        if g_type in ["daily", "none"]:
            prog = 1 if today_str in history else 0
            return f"Daily Study Progress: {prog}/{target}", f"Active Streak: {streak} Days"
        elif g_type == "weekly":
            prog = 0
            for i in range(7):
                if (today - timedelta(days=i)).strftime('%Y-%m-%d') in history:
                    prog += 1
            return f"Weekly Study Progress: {prog}/{target}", f"Active Streak: {streak} Weeks"

def mark_study_complete(global_stats):
    if get_valid_count() >= 100:
        today_str = datetime.now().strftime('%Y-%m-%d')
        history = global_stats["goals"].get("history", [])
        if today_str not in history:
            history.append(today_str)
            global_stats["goals"]["history"] = history
            save_stats(global_stats)

def print_scoreboard(stats):
    """The Main Dashboard Banner"""
    valid_count = get_valid_count()
    
    print(f"{C_SLATE}")
    print("╔" + "═"*40 + "╗")
    
    title2 = "P.A.O.  TRAINER".center(40)
    print(f"║{C_LAVENDER}{title2}{C_SLATE}║")
    
    print("╠" + "═"*40 + "╣")
    
    pao_text = f"Current PAO Memorized: {valid_count}".center(40)
    print(f"║{C_YELLOW}{pao_text}{C_SLATE}║")
    
    print("╠" + "═"*40 + "╣")
    
    top_mode_name, top_mode_score = get_single_most_played(stats)
    
    mode_str = f"Most Played: {top_mode_name} ({top_mode_score})"
    pad = max(0, 40 - len(mode_str)) // 2
    right_pad = 40 - len(mode_str) - pad
    print(f"║{C_LAVENDER}" + (" "*pad) + f"Most Played: {C_WHITE}{top_mode_name} ({top_mode_score}){C_LAVENDER}" + (" "*right_pad) + f"{C_SLATE}║")
    
    # Goals & Streaks Section
    print("╠" + "═"*40 + "╣")
    header_str = "Goals & Streaks"
    h_pad = max(0, 40 - len(header_str)) // 2
    h_rpad = 40 - len(header_str) - h_pad
    print(f"║{C_LAVENDER}" + (" "*h_pad) + header_str + (" "*h_rpad) + f"{C_SLATE}║")
    
    prog_str, streak_str = get_streak_info(stats, valid_count)
    
    p_pad = max(0, 40 - len(prog_str)) // 2
    p_rpad = 40 - len(prog_str) - p_pad
    print(f"║{C_LAVENDER}" + (" "*p_pad) + f"{C_WHITE}{prog_str}{C_LAVENDER}" + (" "*p_rpad) + f"{C_SLATE}║")

    s_pad = max(0, 40 - len(streak_str)) // 2
    s_rpad = 40 - len(streak_str) - s_pad
    print(f"║{C_LAVENDER}" + (" "*s_pad) + f"{C_WHITE}{streak_str}{C_LAVENDER}" + (" "*s_rpad) + f"{C_SLATE}║")
    
    print("╚" + "═"*40 + "╝")
    print(f"{C_RESET}")
    print(f"{C_BLACK}Type '{C_RED}quit{C_BLACK}' to exit | '{C_ORANGE}return{C_BLACK}' for hub | '{C_MAGENTA}edit{C_BLACK}' to edit | '{C_CYAN}open{C_BLACK}' for folder.{C_RESET}")

def print_speed_recall_banner(stats):
    print(f"{C_BLUE}{C_BOLD}")
    print("╔" + "═"*40 + "╗")
    print("║" + "S P E E D   R E C A L L".center(40) + "║")
    print("╠" + "═"*40 + "╣")
    
    e = format_time(stats['records'].get('speed_easy', 999.9))
    me = format_time(stats['records'].get('speed_medium', 999.9))
    h = format_time(stats['records'].get('speed_hard', 999.9))
    hc = format_time(stats['records'].get('speed_hardcore', 999.9))
    streak_val = str(stats['longest_streak'])

    print("║" + format_banner_row("Easy", e, "Medium", me, C_BLUE) + "║")
    print("║" + format_banner_row("Hard", h, "Hardcore", hc, C_BLUE) + "║")
    
    streak_text = f"Longest Streak: {streak_val}"
    streak_pad = max(0, 40 - len(streak_text)) // 2
    streak_right = 40 - len(streak_text) - streak_pad
    print("║" + (" " * streak_pad) + f"Longest Streak: {C_RED}{streak_val}{C_BLUE}" + (" " * streak_right) + "║")
    
    print("╚" + "═"*40 + "╝")
    print(f"{C_RESET}")

def print_countdown_banner(stats, ans_mode):
    print(f"{C_YELLOW}{C_BOLD}")
    print("╔" + "═"*40 + "╗")
    print("║" + "C O U N T D O W N".center(40) + "║")
    print("╠" + "═"*40 + "╣")
    
    m = 'pao' if ans_mode == 'pao' else 'digits'
    e = str(stats['countdown_records'].get(f'countdown_easy_{m}', 0))
    me = str(stats['countdown_records'].get(f'countdown_medium_{m}', 0))
    h = str(stats['countdown_records'].get(f'countdown_hard_{m}', 0))
    hc = str(stats['countdown_records'].get(f'countdown_hardcore_{m}', 0))
    
    print("║" + format_banner_row("Easy", e, "Medium", me, C_YELLOW) + "║")
    print("║" + format_banner_row("Hard", h, "Hardcore", hc, C_YELLOW) + "║")
    print("╚" + "═"*40 + "╝")
    print(f"{C_RESET}")

def print_training_banner():
    print(f"{C_MAGENTA}{C_BOLD}")
    print("╔" + "═"*40 + "╗")
    print("║" + "T R A I N I N G   R O O M".center(40) + "║")
    print("╚" + "═"*40 + "╝")
    print(f"{C_RESET}")

def print_session_summary(session):
    if session["countdown"]["played"] == 0 and session["speed"]["played"] == 0 and session["training"]["played"] == 0:
        return

    clear_screen()
    print("\n" + f"{C_WHITE}" + "="*40 + f"{C_RESET}")
    print("🏁 SESSION SUMMARY 🏁".center(40))
    print(f"{C_WHITE}" + "="*40 + f"{C_RESET}")
    
    if session["countdown"]["played"] > 0:
        print(f"\n{C_YELLOW}--- COUNTDOWN ---{C_RESET}")
        print(f"Total Games Played : {session['countdown']['played']}")
        avg = session['countdown']['total_score'] / session['countdown']['played']
        print(f"Average Score      : {avg:.1f}")
        print(f"Best Session Score : {session['countdown']['best']}")
        
    if session["speed"]["played"] > 0:
        print(f"\n{C_BLUE}--- SPEED RECALL ---{C_RESET}")
        print(f"Total Decoded : {session['speed']['played']}")
        acc = (session['speed']['correct'] / session['speed']['played'] * 100)
        print(f"Accuracy      : {acc:.1f}%")
        print(f"Best Streak   : {session['speed']['best_streak']}")
        print("Session Fastest Times:")
        if session["speed"]["fastest_speed_easy"] < 999: print(f"  Easy     : {format_time(session['speed']['fastest_speed_easy'])}")
        if session["speed"]["fastest_speed_medium"] < 999: print(f"  Medium   : {format_time(session['speed']['fastest_speed_medium'])}")
        if session["speed"]["fastest_speed_hard"] < 999: print(f"  Hard     : {format_time(session['speed']['fastest_speed_hard'])}")
        if session["speed"]["fastest_speed_hardcore"] < 999: print(f"  Hardcore : {format_time(session['speed']['fastest_speed_hardcore'])}")
        
    if session["training"]["played"] > 0:
        print(f"\n{C_MAGENTA}--- TRAINING ---{C_RESET}")
        print(f"Total Cards Trained : {session['training']['played']}")
        print(f"Best Streak         : {session['training']['best_streak']}")
        
    print(f"\n{C_WHITE}" + "="*40 + f"{C_RESET}")
    input(f"\n{C_BLACK}Press {C_LAVENDER}Enter{C_BLACK} to exit...{C_RESET}")

# ==========================================
# GENERATION & TRANSLATION
# ==========================================

def generate_pao_string(valid_pao_keys, digit_length, diff_mode):
    num_pairs = (digit_length + 1) // 2
    raw_string = ""
    
    for _ in range(num_pairs):
        raw_string += random.choice(valid_pao_keys)
        
    raw_string = raw_string[:digit_length]
        
    if diff_mode == "easy":
        chunks = [raw_string[i:i+6] for i in range(0, len(raw_string), 6)]
        return " ".join(chunks)
        
    return raw_string

def translate_pao_string(generated_string, persons, actions, objects):
    clean_string = generated_string.replace(" ", "")
    expected_answers_data = []
    primary_sentences = []
    
    idx = 0
    n = len(clean_string)
    
    while idx < n:
        remaining = n - idx
        
        if remaining >= 6:
            p_key, a_key, o_key = clean_string[idx:idx+2], clean_string[idx+2:idx+4], clean_string[idx+4:idx+6]
            idx += 6
        elif remaining >= 4:
            p_key, a_key, o_key = clean_string[idx:idx+2], clean_string[idx+2:idx+4], clean_string[idx+2:idx+4]
            idx += 4
        elif remaining >= 2:
            p_key, a_key, o_key = clean_string[idx:idx+2], clean_string[idx:idx+2], clean_string[idx:idx+2]
            idx += 2
        else:
            idx += 1
            continue
            
        p_list = persons.get(p_key, [f"[Missing Person {p_key}]"])
        a_list = actions.get(a_key, [f"[Missing Action {a_key}]"])
        o_list = objects.get(o_key, [f"[Missing Object {o_key}]"])
        
        expected_answers_data.append((p_list, a_list, o_list))
        
        sentence = f"{p_list[0]} {a_list[0]} {o_list[0]}."
        sentence = sentence[0].upper() + sentence[1:]
        primary_sentences.append(sentence)
        
    return expected_answers_data, " ".join(primary_sentences)

# ==========================================
# COUNTDOWN & LIVE TIMER SYSTEMS
# ==========================================

def run_memorization_timer(countdown_seconds, raw_str):
    start_time = time.time()
    last_printed_time = -1
    
    while msvcrt.kbhit():
        msvcrt.getch()
        
    if " " in raw_str:
        chunks = raw_str.split(" ")
        lines = [" ".join(chunks[i:i+10]) for i in range(0, len(chunks), 10)]
        formatted_str = "\n".join(lines)
    else:
        lines = [raw_str[i:i+60] for i in range(0, len(raw_str), 60)]
        formatted_str = "\n".join(lines)
        
    print(f"\nRandomly Generated String:\n{formatted_str}")
    sys.stdout.write(f"\n{C_BLACK}Memorize this string! (Press {C_LAVENDER}Enter{C_BLACK} to finish early)\n\n{C_RESET}")
    
    sys.stdout.write("\n\n\n\n\n")
    sys.stdout.write("\033[5A")
    
    sys.stdout.write("\033[?25l") 
    try:
        while True:
            elapsed = time.time() - start_time
            remaining = countdown_seconds - elapsed
            current_tenth = int(remaining * 10)
            
            if remaining <= 0:
                sys.stdout.write("\033[K\n" * 5)
                sys.stdout.write("\033[5A")
                print(f"\n{C_RED}{C_BOLD}⏰ TIME'S UP! ⏰{C_RESET}\n")
                time.sleep(1.5)
                break
                
            if current_tenth != last_printed_time:
                timer_color = C_YELLOW
                
                mins = int(remaining // 60)
                secs = int(remaining % 60)
                time_str = f"{mins}:{secs:02d}"
                
                for i in range(5):
                    line_parts = [ASCII_FONTS[char][i] for char in time_str]
                    ascii_line = "  ".join(line_parts)
                    sys.stdout.write(f"\033[K{timer_color}{C_BOLD}{ascii_line.center(40)}{C_RESET}\n")
                
                sys.stdout.write("\033[5A") 
                sys.stdout.flush()
                last_printed_time = current_tenth
                
            if msvcrt.kbhit():
                char = msvcrt.getch()
                if char in (b'\r', b'\n'):
                    sys.stdout.write("\033[5B")
                    print(f"\n{C_YELLOW}Memorization finished early.{C_RESET}")
                    time.sleep(0.5)
                    break
                    
            time.sleep(0.01)
    finally:
        sys.stdout.write("\033[?25h") 
        sys.stdout.flush()

def get_input_with_timer(prompt_text=None, countdown_seconds=None, show_timer=True):
    if prompt_text is None:
        prompt_text = f"{C_BLACK}Decode this string (type '{C_MAGENTA}back{C_BLACK}' for menu):{C_RESET}"
        
    sys.stdout.write(f"\n{prompt_text}\n\n")
    start_time = time.time()
    user_input = ""
    
    last_printed_time = -1
    last_printed_input = None
    needs_wipe = False 
    
    while True:
        elapsed = time.time() - start_time
        current_tenth = int(elapsed * 10)
        
        if countdown_seconds is not None:
            remaining = countdown_seconds - elapsed
            if remaining <= 0:
                sys.stdout.write(f"\r{C_RED}[0.0s]{C_RESET} >>> {user_input}\033[K\n")
                sys.stdout.flush()
                print(f"\n{C_RED}{C_BOLD}⏰ TIME'S UP! ⏰{C_RESET}\n")
                time.sleep(1)
                return user_input.strip(), elapsed
            display_time = remaining
            timer_color = C_CYAN if remaining > 60 else C_YELLOW if remaining > 10 else C_RED
        else:
            display_time = elapsed
            timer_color = C_CYAN
            
        if current_tenth != last_printed_time or user_input != last_printed_input:
            term_width = shutil.get_terminal_size().columns
            max_len = term_width - 30 
            
            display_text = user_input
            if len(user_input) > max_len:
                display_text = "..." + user_input[-(max_len-3):]
                
            if not show_timer:
                prompt = f"\r>>> {display_text}"
            else:
                prompt = f"\r{timer_color}[{display_time:.1f}s]{C_RESET} >>> {display_text}"
            
            if needs_wipe:
                sys.stdout.write(f"{prompt} \b\033[K")
                needs_wipe = False
            else:
                sys.stdout.write(f"{prompt}\033[K")
                
            sys.stdout.flush()
            
            last_printed_time = current_tenth
            last_printed_input = user_input
        
        if msvcrt.kbhit():
            char = msvcrt.getch()
            if char in (b'\r', b'\n'):
                print()  
                return user_input.strip(), elapsed
                
            elif char == b'\x08':
                if len(user_input) > 0:
                    user_input = user_input[:-1]
                    needs_wipe = True
            else:
                try:
                    decoded_char = char.decode('utf-8')
                    if decoded_char.isprintable():
                        user_input += decoded_char
                except UnicodeDecodeError:
                    pass 
        
        time.sleep(0.01)

def validate_with_feedback(user_input, expected_answers_data):
    cleaned_input = clean_text(user_input)
    all_correct = True
    feedback = []
    
    for i, (p_list, a_list, o_list) in enumerate(expected_answers_data):
        p_match = any(clean_text(p) in cleaned_input for p in p_list)
        a_match = any(clean_text(a) in cleaned_input for a in a_list)
        o_match = any(clean_text(o) in cleaned_input for o in o_list)
        
        if p_match and a_match and o_match:
            continue
        else:
            all_correct = False
            p_str = "Correct Person" if p_match else "Incorrect Person"
            a_str = "Correct Action" if a_match else "Incorrect Action"
            o_str = "Correct Object" if o_match else "Incorrect Object"
            feedback.append(f"Chunk {i+1} Failed: {p_str}, {a_str}, {o_str}")
            
    return all_correct, feedback

def grade_countdown(user_input, expected_data, raw_str, answer_mode):
    feedback = []
    score = 0
    streak_broken = False
    clean_raw = raw_str.replace(" ", "")
    
    if answer_mode == 'digits':
        clean_input = "".join([c for c in user_input if c.isdigit()])
        attempted_chunks = (len(clean_input) + 5) // 6 
        
        for i in range(attempted_chunks):
            if i >= len(expected_data): break
            
            user_chunk = clean_input[i*6 : i*6+6].ljust(6, 'X')
            expected_chunk = clean_raw[i*6 : i*6+6]
            
            p_match = user_chunk[0:2] == expected_chunk[0:2]
            a_match = user_chunk[2:4] == expected_chunk[2:4]
            o_match = user_chunk[4:6] == expected_chunk[4:6]
            
            if p_match and a_match and o_match:
                if not streak_broken: score += 1
            else:
                streak_broken = True
                p_str = "Correct Person" if p_match else f"Incorrect Person (Expected {expected_chunk[0:2]}, got {user_chunk[0:2]})"
                a_str = "Correct Action" if a_match else f"Incorrect Action (Expected {expected_chunk[2:4]}, got {user_chunk[2:4]})"
                o_str = "Correct Object" if o_match else f"Incorrect Object (Expected {expected_chunk[4:6]}, got {user_chunk[4:6]})"
                feedback.append(f"Chunk {i+1} Failed: {p_str}, {a_str}, {o_str}")
                if len(feedback) >= 10:
                    feedback.append("... (Additional errors hidden to save space)")
                    break
                    
        return score, attempted_chunks, feedback
        
    else: 
        sentences = [s.strip() for s in user_input.replace('?', '.').replace('!', '.').split('.') if s.strip()]
        attempted_chunks = len(sentences)
        if attempted_chunks == 0 and len(user_input) > 0:
            attempted_chunks = max(1, len(user_input.split()) // 4) 
            
        cleaned_input = clean_text(user_input)
        
        for i in range(attempted_chunks):
            if i >= len(expected_data): break
            p_list, a_list, o_list = expected_data[i]
            
            p_match = any(clean_text(p) in cleaned_input for p in p_list)
            a_match = any(clean_text(a) in cleaned_input for a in a_list)
            o_match = any(clean_text(o) in cleaned_input for o in o_list)
            
            if p_match and a_match and o_match:
                if not streak_broken: score += 1
            else:
                streak_broken = True
                p_str = "Correct Person" if p_match else "Incorrect Person"
                a_str = "Correct Action" if a_match else "Incorrect Action"
                o_str = "Correct Object" if o_match else "Incorrect Object"
                feedback.append(f"Chunk {i+1} Failed: {p_str}, {a_str}, {o_str}")
                if len(feedback) >= 10:
                    feedback.append("... (Additional errors hidden to save space)")
                    break
                    
        return score, attempted_chunks, feedback

# ==========================================
# TRAINING MODE & HINT SYSTEM
# ==========================================

def verify_letter_mapping(valid_pao_keys, persons, stats, force_prompt=False):
    highest_digit = 9
    current_mapping = stats.get("letter_mapping", {})
    inferred_new = False
    
    for i in range(highest_digit + 1):
        digit_str = str(i)
        if digit_str not in current_mapping:
            inferred_new = True
            key = f"0{i}" 
            
            if key in persons and persons[key]:
                person_name = persons[key][0].strip()
                words = person_name.split()
                if i == 0:
                    current_mapping[digit_str] = words[0][0].upper() if words else "?"
                else:
                    if len(words) > 1:
                        current_mapping[digit_str] = words[1][0].upper()
                    elif len(words) == 1 and len(words[0]) >= 2:
                        current_mapping[digit_str] = words[0][1].upper()
                    else:
                        current_mapping[digit_str] = "?"
            else:
                current_mapping[digit_str] = "?"
                
    if not inferred_new and not force_prompt:
        return current_mapping

    alert_msg = ""
    while True:
        clear_screen()
        if alert_msg:
            print(alert_msg)
            
        if force_prompt:
            print(f"\n{C_CYAN}--- Letter Mapping Editor ---{C_RESET}")
        else:
            print(f"\n{C_CYAN}Hi there! I have inferred some data but can get it wrong.{C_RESET}")
            print("This is the data we have for each number:")
            
        mapping_strs = [f"{i} = {current_mapping[str(i)]}" for i in range(highest_digit + 1)]
        print("\n" + "   |   ".join(mapping_strs))
        
        choice = input(f"\nWould you like to make any changes? (y/n)\n>>> ").strip().lower()
        if choice == 'y':
            target = input(f"Please press the number you would like to change. (0-{highest_digit})\n>>> ").strip()
            if target.isdigit() and 0 <= int(target) <= highest_digit:
                new_letter = input(f"What letter would you like to change the number {target} to?\n>>> ").strip().upper()
                if len(new_letter) == 1 and new_letter.isalpha():
                    current_mapping[target] = new_letter
                    alert_msg = f"\n{C_GREEN}Your numbers have been updated.{C_RESET}"
                else:
                    alert_msg = f"\n{C_RED}Invalid input. Please enter a single letter.{C_RESET}"
            else:
                alert_msg = f"\n{C_RED}Invalid response. Please select a number 0-{highest_digit}.{C_RESET}"
        elif choice == 'n':
            break
        else:
            alert_msg = f"\n{C_RED}Please type 'y' or 'n'.{C_RESET}"
            
    stats["letter_mapping"] = current_mapping
    save_stats(stats)
    
    return current_mapping

def generate_hints(pao_number, person_string, letter_mapping):
    digit_1 = pao_number[0]
    digit_2 = pao_number[1]
    
    letter_1 = letter_mapping.get(digit_1, "?")
    letter_2 = letter_mapping.get(digit_2, "?")
    
    tier_1 = f"{letter_1} {letter_2}"
    
    words = person_string.split()
    matched_d1 = False
    matched_d2 = False
    blanked_words = []
    
    for word in words:
        if not word: 
            continue
        
        if not matched_d1 and word[0].upper() == letter_1:
            blanked_words.append(word[0] + "_" * (len(word) - 1))
            matched_d1 = True
        elif not matched_d2 and word[0].upper() == letter_2:
            blanked_words.append(word[0] + "_" * (len(word) - 1))
            matched_d2 = True
        else:
            blanked_words.append("_" * len(word))
            
    tier_2 = " ".join(blanked_words)
    
    return tier_1, tier_2

def play_training_mode(valid_pao_keys, persons, actions, objects, global_stats, session):
    letter_mapping = verify_letter_mapping(valid_pao_keys, persons, global_stats)
    
    saved_training = global_stats.get("saved_training", {})
    saved_pool = saved_training.get("pool", [])
    original_total = saved_training.get("original_total", 0)
    
    saved_pool = [x for x in saved_pool if x in valid_pao_keys]

    pool = []
    total_in_pool = 0

    if saved_pool:
        clear_screen()
        print_training_banner()
        print(f"\n{C_CYAN}You have an incomplete training deck waiting for you.{C_RESET}")
        print(f"There are {len(saved_pool)} PAOs remaining to review.")
        choice = input(f"\nWould you like to pick up right where you left off? (y/n)\n>>> ").strip().lower()
        if choice == 'y':
            pool = saved_pool
            total_in_pool = original_total
        else:
            pool = list(valid_pao_keys)
            random.shuffle(pool)
            total_in_pool = len(pool)
            global_stats["saved_training"] = {"pool": [], "original_total": 0}
            save_stats(global_stats)
    else:
        pool = list(valid_pao_keys)
        random.shuffle(pool)
        total_in_pool = len(pool)
    
    start_time = time.time()
    first_try_correct = 0
    current_streak = 0
    best_streak = 0
    cards_graded = 0
    user_quit = False
    full_exit = False
    hub_exit = False
    
    while pool:
        current_num = pool[0]
        expected_data, primary_text = translate_pao_string(current_num, persons, actions, objects)
        
        person_string = expected_data[0][0][0]
        tier_1, tier_2 = generate_hints(current_num, person_string, letter_mapping)
        tier_3 = person_string
        
        clear_screen()
        print_training_banner()
        print(f"\n{C_BLACK}Type '{C_RED}quit{C_BLACK}' to exit | '{C_ORANGE}return{C_BLACK}' for hub | '{C_MAGENTA}back{C_BLACK}' for menu | '{C_CYAN}hint{C_BLACK}' for help.\n{C_RESET}")
        print("-" * 40)
        print(f"Remaining: {len(pool)}/{total_in_pool}".center(40))
        print_huge_number(current_num)
        
        attempts = 0
        hints_used = 0
        penalty_flag = False
        graded_this_round = False
        
        while True:
            user_guess = input(f"Answer the PAO:\n\n>>> ").strip().lower()
            
            if user_guess in ['quit', 'exit', 'q']:
                user_quit = True
                full_exit = True  
                break
            elif user_guess in ['return', 'hub', 'h']:
                user_quit = True
                hub_exit = True
                break
            elif user_guess in ['back', 'menu', 'b']:
                user_quit = True
                break
            elif user_guess in ['change', 'edit','e']:
                letter_mapping = verify_letter_mapping(valid_pao_keys, persons, global_stats, force_prompt=True)
                clear_screen()
                print_training_banner()
                print(f"\n{C_BLACK}Type '{C_RED}quit{C_BLACK}' to exit | '{C_ORANGE}return{C_BLACK}' for hub | '{C_MAGENTA}back{C_BLACK}' for menu | '{C_CYAN}hint{C_BLACK}' for help.\n{C_RESET}")
                print("-" * 40)
                print(f"Remaining: {len(pool)}/{total_in_pool}".center(40))
                print_huge_number(current_num)
                continue
            elif user_guess in ['hint', 'help']:
                hints_used += 1
                if hints_used == 1:
                    print(f"\n{C_CYAN}Hint 1: {tier_1}{C_RESET}\n")
                elif hints_used == 2:
                    print(f"\n{C_CYAN}Hint 2: {tier_2}{C_RESET}\n")
                elif hints_used >= 3:
                    print(f"\n{C_CYAN}Hint 3: {tier_3}{C_RESET}\n")
                    penalty_flag = True
                continue
                
            if not graded_this_round:
                cards_graded += 1
                graded_this_round = True
                
            is_correct, feedback = validate_with_feedback(user_guess, expected_data)
            
            if is_correct:
                if penalty_flag:
                    print(f"\n{C_GREEN}✅ Correct!{C_RESET}")
                    print(f"{C_YELLOW}Card reshuffled back into the deck for further review.{C_RESET}\n")
                    pool.append(pool.pop(0))
                    time.sleep(1.5)
                    break
                else:
                    if attempts == 0 and hints_used == 0:
                        first_try_correct += 1
                        current_streak += 1
                        best_streak = max(best_streak, current_streak)
                    
                    print(f"\n{C_GREEN}✅ Correct!{C_RESET}\n")
                    pool.pop(0)
                    time.sleep(1.0) 
                    break
                
            else:
                attempts += 1
                current_streak = 0
                print(f"\n{C_RED}❌ Not quite.{C_RESET}")
                
                if attempts >= 2:
                    penalty_flag = True
                    
                if not penalty_flag:
                    print("Targeted Feedback:")
                    for error in feedback:
                        print(f"  - {error}")
                    print(f"{C_YELLOW}Try again, or type 'hint' for help!{C_RESET}\n")
                else:
                    print(f"The answer is: {C_YELLOW}{primary_text}{C_RESET}")
                    print(f"Type it out to reinforce the memory! (This card will be reshuffled)\n")

        if user_quit:
            break

    if pool:
        global_stats["saved_training"] = {
            "pool": pool,
            "original_total": total_in_pool
        }
    else:
        global_stats["saved_training"] = {
            "pool": [],
            "original_total": 0
        }
    save_stats(global_stats)

    session["training"]["played"] += cards_graded
    session["training"]["best_streak"] = max(session["training"]["best_streak"], best_streak)
    
    if cards_graded > 0:
        mark_study_complete(global_stats)

    if full_exit:
        return 'quit'  
    if hub_exit:
        return 'hub'
        
    if not user_quit:
        while True:
            choice = input("\nTrain again? (y/n)\n\n>>> ").strip().lower()
            if choice == 'y':
                return play_training_mode(valid_pao_keys, persons, actions, objects, global_stats, session)
            elif choice in ['return', 'hub', 'h']:
                return 'hub'
            elif choice in ['quit', 'exit', 'q']:
                return 'quit'
            elif choice == 'n':
                return 'menu'
    else:
        return 'menu'

# ==========================================
# GAME LOOP
# ==========================================

def play_game():
    global_stats = load_stats()
    
    session = {
        "countdown": {"played": 0, "total_score": 0, "best": 0},
        "speed": {"played": 0, "correct": 0, "best_streak": 0, "current_streak": 0,
                  "fastest_speed_easy": 999.9, "fastest_speed_medium": 999.9, "fastest_speed_hard": 999.9, "fastest_speed_hardcore": 999.9},
        "training": {"played": 0, "best_streak": 0}
    }
    
    is_chunked = global_stats["settings"].get("is_chunked", False)
    answer_mode = global_stats["settings"].get("answer_mode", "pao")
    
    alert_msg = ""
    
    while True:
        today_str = datetime.now().strftime('%Y-%m-%d')
        if global_stats["goals"].get("today_date") != today_str:
            global_stats["goals"]["today_encoded"] = 0
            global_stats["goals"]["today_date"] = today_str
            save_stats(global_stats)
            
        persons, actions, objects = load_all_pao_data()
        
        valid_pao_keys = []
        for i in range(100):
            key = str(i).zfill(2)
            has_p = key in persons and persons[key]
            has_a = key in actions and actions[key]
            has_o = key in objects and objects[key]
            if has_p and has_a and has_o:
                valid_pao_keys.append(key)
                
        current_valid_count = len(valid_pao_keys)
        
        # Streak Verification & Loss Detection
        current_streak_val = calculate_streak_val(global_stats, current_valid_count)
        last_known_streak = global_stats["goals"].get("last_known_streak", 0)
        
        if current_streak_val == 0 and last_known_streak > 0:
            time_unit = "weeks" if global_stats["goals"].get("study_goal_type") == "weekly" and current_valid_count >= 100 else "days"
            alert_msg = f"\n{C_RED}You lost a streak of {last_known_streak} {time_unit}. Don't worry, every master builder stumbles. Let's start a new one today!{C_RESET}\n"
            global_stats["goals"]["last_known_streak"] = 0
            save_stats(global_stats)
        elif current_streak_val > 0 and current_streak_val != last_known_streak:
            global_stats["goals"]["last_known_streak"] = current_streak_val
            save_stats(global_stats)
        
        # Phase 1 Initialization
        if current_valid_count < 100 and global_stats["goals"].get("daily_encode_goal", 0) == 0:
            clear_screen()
            print_scoreboard(global_stats)
            print(f"\n{C_CYAN}Welcome to the Mind Palace!{C_RESET}")
            print("To build your palace, consistency is key.")
            while True:
                try:
                    goal_in = input("How many PAOs do you want to encode per day? (e.g., 3, 5, 10)\n>>> ").strip()
                    goal = int(goal_in)
                    if goal > 0:
                        global_stats["goals"]["daily_encode_goal"] = goal
                        save_stats(global_stats)
                        print(f"\n{C_GREEN}Goal set to {goal} PAOs per day!{C_RESET}")
                        time.sleep(1.5)
                        break
                except ValueError:
                    pass
        
        # Phase 2 Initialization (Level up to 100)
        if current_valid_count > global_stats.get("max_pao_memorized", 0):
            clear_screen()
            print(f"\n{C_YELLOW}⭐ PAO Count updated to {current_valid_count}! ⭐{C_RESET}")
            
            if current_valid_count == 100:
                print(f"\n{C_GREEN}{C_BOLD}")
                print("╔" + "═"*40 + "╗")
                print("║" + "🏆 MASTER OF THE MIND PALACE! 🏆".center(40) + "║")
                print("╠" + "═"*40 + "╣")
                print("║" + "You have successfully encoded all 100".center(40) + "║")
                print("║" + "P.A.O. numbers! This is a massive".center(40) + "║")
                print("║" + "achievement. Keep up the practice to".center(40) + "║")
                print("║" + "become a true memory legend!".center(40) + "║")
                print("╚" + "═"*40 + "╝")
                print(f"{C_RESET}")
                play_victory_jingle()
            
            has_records = any(t < 999.9 for t in global_stats["records"].values()) or global_stats["longest_streak"] > 0
            if has_records:
                while True:
                    wipe = input("\nWipe your old high scores to start fresh with this larger list? (y/n)\n\n>>> ").strip().lower()
                    if wipe == 'y':
                        global_stats["records"] = {"speed_easy": 999.9, "speed_medium": 999.9, "speed_hard": 999.9, "speed_hardcore": 999.9}
                        global_stats["longest_streak"] = 0
                        print(f"{C_YELLOW}Scores wiped! A clean slate awaits.{C_RESET}\n")
                        break
                    elif wipe == 'n':
                        print(f"{C_YELLOW}Old scores kept!{C_RESET}\n")
                        break
            
            global_stats["max_pao_memorized"] = current_valid_count
            save_stats(global_stats)
            
        elif current_valid_count < global_stats.get("max_pao_memorized", 0):
            global_stats["max_pao_memorized"] = current_valid_count
            save_stats(global_stats)
            
        # Post-100 Study Goal Setup Catch
        if current_valid_count == 100 and global_stats["goals"].get("study_goal_type", "none") == "none":
            clear_screen()
            print(f"\n{C_GREEN}{C_BOLD}🏆 MASTER OF THE MIND PALACE! 🏆{C_RESET}")
            print("\nNow it's time to set a Study Goal to maintain your palace.")
            print(f"Type '{C_GREEN}daily{C_RESET}' to train every day.")
            print(f"Type '{C_YELLOW}weekly{C_RESET}' to train X days per week.")
            while True:
                g_type = input(">>> ").strip().lower()
                if g_type in ['daily', 'weekly']:
                    global_stats["goals"]["study_goal_type"] = g_type
                    if g_type == 'weekly':
                        while True:
                            try:
                                target = int(input("How many days per week? (1-7)\n>>> ").strip())
                                if 1 <= target <= 7:
                                    global_stats["goals"]["study_goal_target"] = target
                                    break
                            except ValueError:
                                pass
                    else:
                        global_stats["goals"]["study_goal_target"] = 1
                    save_stats(global_stats)
                    print(f"\n{C_GREEN}Study Goal Set! Let's keep those memories sharp.{C_RESET}")
                    time.sleep(1.5)
                    break
            
        clear_screen()
        print_scoreboard(global_stats)
        if alert_msg:
            print(alert_msg)
            alert_msg = ""
        
        print(f"\n {C_LAVENDER}Select Game Mode:{C_RESET}")
        print(f"   {C_WHITE}[1] Countdown{C_RESET}")
        print(f"   {C_WHITE}[2] Speed Recall{C_RESET}")
        print(f"   {C_WHITE}[3] Training{C_RESET}")
        
        game_mode = input("\n>>> ").strip().lower()
        
        if game_mode in ['quit', 'exit', 'q']:
            print_session_summary(session)
            sys.exit(99)
            
        if game_mode in ['return', 'hub', 'h']:
            print_session_summary(session)
            sys.exit(0)
            
        if game_mode in ['add', 'edit', 'a', 'e', '+']:
            manage_pao_data(global_stats)
            continue
            
        if game_mode in ['open', 'file', 'config', 'configure', 'txt', 'o']:
            print(f"{C_CYAN}Opening File Explorer...{C_RESET}\n")
            os.startfile(os.path.join(script_dir, PAO_DATA_DIR))  
            time.sleep(1)
            continue
            
        if game_mode == '3':
            if not valid_pao_keys:
                print(f"\n{C_RED}You must encode at least 1 full PAO before training!{C_RESET}")
                print(f"{C_YELLOW}Type 'edit' to open the PAO Data Editor.{C_RESET}")
                time.sleep(2.5)
                continue
            result = play_training_mode(valid_pao_keys, persons, actions, objects, global_stats, session)
            if result == 'quit':
                print_session_summary(session)
                sys.exit(99)
            if result == 'hub':
                print_session_summary(session)
                sys.exit(0)
            continue
            
        elif game_mode == '1': # COUNTDOWN MODE
            if not valid_pao_keys:
                print(f"\n{C_RED}You must encode at least 1 full PAO before playing!{C_RESET}")
                print(f"{C_YELLOW}Type 'edit' to open the PAO Data Editor.{C_RESET}")
                time.sleep(2.5)
                continue
                
            while True:
                clear_screen()
                print_countdown_banner(global_stats, answer_mode)
                print(f"\n{C_BLACK}Type '{C_RED}quit{C_BLACK}' to exit | '{C_ORANGE}return{C_BLACK}' for hub | '{C_MAGENTA}back{C_BLACK}' for menu{C_RESET}")
                
                chunk_status = f"{C_GREEN}Enabled{C_RESET}" if is_chunked else f"{C_RED}Disabled{C_RESET}"
                ans_status = f"{C_GREEN}#{C_RESET}" if answer_mode == 'digits' else f"{C_GREEN}PAO{C_RESET}"
                
                print(f"\n[Settings] Chunked: {chunk_status} | Answer Mode: {ans_status}")
                if answer_mode == 'digits':
                    print(f"--Type '{C_YELLOW}chunked{C_RESET}' for easier mode and '{C_YELLOW}PAO{C_RESET}' to answer with your people, actions, and objects--")
                else:
                    print(f"--Type '{C_YELLOW}chunked{C_RESET}' for easier mode and '{C_YELLOW}#{C_RESET}' to answer with numbers--")
                    
                print(f"\n {C_YELLOW}Select Difficulty Mode:{C_RESET}")
                print(f"   {C_YELLOW}[1]{C_RESET} Easy     (30 mins)")
                print(f"   {C_YELLOW}[2]{C_RESET} Medium   (15 mins)")
                print(f"   {C_YELLOW}[3]{C_RESET} Hard     (10 mins)")
                print(f"   {C_YELLOW}[4]{C_RESET} Hardcore (5 mins)")
                print(f"   {C_YELLOW}[5]{C_RESET} Custom   (Choose your own length)\n")
                
                choice = input(">>> ").strip().lower()
                
                if choice in ['back', 'menu']:
                    break
                if choice in ['quit', 'exit', 'q']:
                    print_session_summary(session)
                    sys.exit(99)
                if choice in ['return', 'hub', 'h']:
                    print_session_summary(session)
                    sys.exit(0)
                if choice in ['chunked', 'chunk', 'space', 'spaced', 'group', 'grouped']:
                    is_chunked = not is_chunked
                    global_stats["settings"]["is_chunked"] = is_chunked
                    save_stats(global_stats)
                    continue
                if choice in ['#', 'digits', 'digit', 'num', 'number']:
                    answer_mode = 'digits'
                    global_stats["settings"]["answer_mode"] = answer_mode
                    save_stats(global_stats)
                    continue
                if choice in ['pao']:
                    answer_mode = 'pao'
                    global_stats["settings"]["answer_mode"] = answer_mode
                    save_stats(global_stats)
                    continue
                    
                length = 1200
                if choice == '1':   diff_mode, time_limit = "countdown_easy", 30 * 60
                elif choice == '2': diff_mode, time_limit = "countdown_medium", 15 * 60
                elif choice == '3': diff_mode, time_limit = "countdown_hard", 10 * 60
                elif choice == '4': diff_mode, time_limit = "countdown_hardcore", 5 * 60
                elif choice == '5':
                    diff_mode = "countdown_custom"
                    try:
                        time_in = input("Enter time limit (in minutes):\n>>> ").strip()
                        if time_in in ['back', 'menu']: continue
                        if time_in in ['quit', 'exit', 'q']: 
                            print_session_summary(session)
                            sys.exit(99)
                        if time_in in ['return', 'hub', 'h']:
                            print_session_summary(session)
                            sys.exit(0)
                        time_limit = float(time_in) * 60
                        
                        len_in = input("Enter custom length:\n>>> ").strip()
                        if len_in in ['back', 'menu']: continue
                        if len_in in ['quit', 'exit', 'q']: 
                            print_session_summary(session)
                            sys.exit(99)
                        if len_in in ['return', 'hub', 'h']:
                            print_session_summary(session)
                            sys.exit(0)
                        length = int(len_in)
                        
                        if length <= 0 or time_limit <= 0:
                            print("Invalid input. Length and time must be positive.")
                            time.sleep(1.5)
                            continue
                    except ValueError:
                        print("Invalid numbers.")
                        time.sleep(1.5)
                        continue
                else:
                    print("Invalid choice.")
                    time.sleep(1)
                    continue
                
                is_standard = diff_mode != "countdown_custom"
                if is_standard:
                    full_mode = f"{diff_mode}_{answer_mode}"
                    global_stats["frequencies"][full_mode] = global_stats["frequencies"].get(full_mode, 0) + 1
                    save_stats(global_stats)
                
                # --- GAME START ---
                clear_screen()
                print(f"\n{C_YELLOW}Ready... go!{C_RESET}")
                time.sleep(0.9)

                fmt_mode = "easy" if is_chunked else "hard"
                raw_str = generate_pao_string(valid_pao_keys, length, fmt_mode)
                expected_data, primary_text = translate_pao_string(raw_str, persons, actions, objects)
                
                run_memorization_timer(time_limit, raw_str)
                
                clear_screen()
                print(f"\n{C_CYAN}{C_BOLD}--- RECALL PHASE ---{C_RESET}")
                if answer_mode == 'digits':
                    prompt_str = f"{C_BLACK}Type the raw numbers you memorized:{C_RESET}"
                else:
                    prompt_str = f"{C_BLACK}Type the P.A.O. sentences you memorized:{C_RESET}"
                    
                user_guess, _ = get_input_with_timer(prompt_text=prompt_str, countdown_seconds=None, show_timer=False)

                if user_guess.lower() in ['back', 'menu']:
                    print(f"\n{C_MAGENTA}Returning to Countdown Menu...{C_RESET}")
                    time.sleep(0.75)
                    continue 
                
                if user_guess.lower() in ['quit', 'exit', 'q']:
                    print_session_summary(session)
                    sys.exit(99)
                if user_guess.lower() in ['return', 'hub', 'h']:
                    print_session_summary(session)
                    sys.exit(0)
                    
                score, attempted, feedback = grade_countdown(user_guess, expected_data, raw_str, answer_mode)
                session["countdown"]["played"] += 1
                session["countdown"]["total_score"] += score
                session["countdown"]["best"] = max(session["countdown"]["best"], score)
                
                if attempted > 0:
                    mark_study_complete(global_stats)
                
                if is_standard:
                    global_stats["frequencies"][full_mode] += 1
                    
                    if score > global_stats["countdown_records"].get(full_mode, 0):
                        global_stats["countdown_records"][full_mode] = score
                        save_stats(global_stats)
                        play_victory_jingle()
                        print(f"\n{C_YELLOW}🌟 NEW {full_mode.replace('_', ' ').upper()} HIGH SCORE: {score} 🌟{C_RESET}")
                    else:
                        save_stats(global_stats)
                    
                print(f"\n{C_GREEN}Score: {score} consecutive perfect chunks!{C_RESET}")
                
                if feedback:
                    print(f"\n{C_RED}❌ Missed Chunks (Out of {attempted} attempted):{C_RESET}")
                    for err in feedback:
                        print(f"  - {err}")
                else:
                    if attempted > 0:
                        print(f"\n{C_GREEN}All {attempted} attempted chunks were flawless!{C_RESET}")
                
                post_action = input(f"\n{C_BLACK}Type '{C_RED}quit{C_BLACK}' to exit | '{C_ORANGE}return{C_BLACK}' for hub | '{C_MAGENTA}back{C_BLACK}' (or {C_LAVENDER}Enter{C_BLACK}) for menu\n>>> {C_RESET}").strip().lower()
                if post_action in ['quit', 'exit', 'q']:
                    print_session_summary(session)
                    sys.exit(99)
                if post_action in ['return', 'hub', 'h']:
                    print_session_summary(session)
                    sys.exit(0)
                
        elif game_mode == '2': # SPEED RECALL MODE
            if not valid_pao_keys:
                print(f"\n{C_RED}You must encode at least 1 full PAO before playing!{C_RESET}")
                print(f"{C_YELLOW}Type 'edit' to open the PAO Data Editor.{C_RESET}")
                time.sleep(2.5)
                continue
                
            while True:
                clear_screen()
                print_speed_recall_banner(global_stats)
                print(f"\n{C_BLACK}Type '{C_RED}quit{C_BLACK}' to exit | '{C_ORANGE}return{C_BLACK}' for hub | '{C_MAGENTA}back{C_BLACK}' for menu{C_RESET}")
                
                print(f"\n {C_BLUE}Select Difficulty Mode:{C_RESET}")
                print(f"   {C_YELLOW}[1]{C_RESET} Easy     (18 digits - spaced)")
                print(f"   {C_YELLOW}[2]{C_RESET} Medium   (30 digits)")
                print(f"   {C_YELLOW}[3]{C_RESET} Hard     (60 digits)")
                print(f"   {C_YELLOW}[4]{C_RESET} Hardcore (120 digits)")
                print(f"   {C_YELLOW}[5]{C_RESET} Custom   (Choose your own length)\n")
                
                choice = input(">>> ").strip().lower()
                
                if choice in ['back', 'menu']:
                    break
                if choice in ['quit', 'exit', 'q']:
                    print_session_summary(session)
                    sys.exit(99)
                if choice in ['return', 'hub', 'h']:
                    print_session_summary(session)
                    sys.exit(0)
                
                if choice == '1':   diff_mode, length = "speed_easy", 18
                elif choice == '2': diff_mode, length = "speed_medium", 30
                elif choice == '3': diff_mode, length = "speed_hard", 60
                elif choice == '4': diff_mode, length = "speed_hardcore", 120
                elif choice == '5':
                    diff_mode = "speed_custom"
                    custom_in = input("Enter custom even length:\n>>> ").strip().lower()
                    if custom_in in ['quit', 'exit', 'q']: 
                        print_session_summary(session)
                        sys.exit(99)
                    if custom_in in ['return', 'hub', 'h']:
                        print_session_summary(session)
                        sys.exit(0)
                    if custom_in in ['back', 'menu']: continue
                    try:
                        length = int(custom_in)
                        if length <= 0 or length % 2 != 0:
                            print("Must be a positive EVEN number.")
                            time.sleep(1.5)
                            continue
                    except ValueError:
                        print("Invalid number.")
                        time.sleep(1)
                        continue
                else:
                    print("Invalid choice.")
                    time.sleep(1)
                    continue
                
                is_standard = diff_mode != "speed_custom"
                if is_standard:
                    global_stats["frequencies"][diff_mode] = global_stats["frequencies"].get(diff_mode, 0) + 1
                    save_stats(global_stats)
                
                clear_screen()
                print(f"\n{C_YELLOW}Ready... go!{C_RESET}")
                time.sleep(0.9)

                fmt_mode = "easy" if choice == '1' else "hard"
                raw_str = generate_pao_string(valid_pao_keys, length, fmt_mode)
                expected_data, primary_text = translate_pao_string(raw_str, persons, actions, objects)
                
                print(f"\nRandomly Generated String:\n{raw_str}")
                user_guess, elapsed = get_input_with_timer(show_timer=True)

                if user_guess.lower() in ['back', 'menu']:
                    print(f"\n{C_MAGENTA}Returning to Speed Recall Menu...{C_RESET}")
                    time.sleep(0.75)
                    continue 
                
                if user_guess.lower() in ['quit', 'exit', 'q']:
                    print_session_summary(session)
                    sys.exit(99)
                if user_guess.lower() in ['return', 'hub', 'h']:
                    print_session_summary(session)
                    sys.exit(0)
                    
                session["speed"]["played"] += 1
                is_correct, feedback = validate_with_feedback(user_guess, expected_data)
                
                if user_guess:
                    mark_study_complete(global_stats)
                
                if is_correct:
                    session["speed"]["correct"] += 1
                    session["speed"]["current_streak"] += 1
                    
                    if session["speed"]["current_streak"] > session["speed"]["best_streak"]:
                        session["speed"]["best_streak"] = session["speed"]["current_streak"]
                    if session["speed"]["current_streak"] > global_stats["longest_streak"]:
                        global_stats["longest_streak"] = session["speed"]["current_streak"]
                        
                    print(f"\n{C_GREEN}✅ Great job!{C_RESET}")
                    
                    if session["speed"]["current_streak"] > 0 and session["speed"]["current_streak"] % 5 == 0:
                        print(f"{C_YELLOW}🔥 {session['speed']['current_streak']} IN A ROW! 🔥{C_RESET}")
                        
                    if is_standard:
                        global_stats["frequencies"][diff_mode] += 1
                        time_key = f"fastest_{diff_mode}"
                        
                        if elapsed < session["speed"].get(time_key, 999.9):
                            session["speed"][time_key] = elapsed
                            
                        if elapsed < global_stats["records"].get(diff_mode, 999.9):
                            global_stats["records"][diff_mode] = elapsed
                            save_stats(global_stats) 
                            
                            print(f"\n{C_YELLOW}{C_BOLD}")
                            print("  " + "*"*34)
                            print("🌟" + "NEW PERSONAL BEST RECORD!".center(34) + "🌟")
                            time_text = f"{diff_mode.replace('speed_', '').upper()} MODE: {elapsed:.1f}s"
                            print("🌟" + time_text.center(34) + "🌟")
                            print("  " + "*"*34)
                            print(f"{C_RESET}")
                            
                            play_victory_jingle()
                        else:
                            save_stats(global_stats)
                else:
                    session["speed"]["current_streak"] = 0 
                    print(f"\n{C_RED}❌ Not quite.{C_RESET}")
                    print("Targeted Feedback:")
                    for error in feedback:
                        print(f"  - {error}")
                    print(f"\nThe expected answer was:\n{primary_text}")

                post_action = input(f"\n{C_BLACK}Type '{C_RED}quit{C_BLACK}' to exit | '{C_ORANGE}return{C_BLACK}' for hub | '{C_MAGENTA}back{C_BLACK}' (or {C_LAVENDER}Enter{C_BLACK}) for menu\n>>> {C_RESET}").strip().lower()
                if post_action in ['quit', 'exit', 'q']:
                    print_session_summary(session)
                    sys.exit(99)
                if post_action in ['return', 'hub', 'h']:
                    print_session_summary(session)
                    sys.exit(0)

        else:
            print("Invalid choice. Please select 1, 2, or 3.")
            time.sleep(1)
            continue

if __name__ == "__main__":
    play_game()
