import pytesseract
import cv2
import numpy as np
from PIL import ImageGrab
import time
import datetime
import os
import threading
import tkinter as tk
import keyboard as kb
import sys

# === Chemin et OCR ===
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(__file__)

TESSERACT_PATH = os.path.join(BASE_PATH, "Tesseract-OCR", "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# === Constantes ===
CONFIG_FILE = os.path.join(BASE_PATH, "config.txt")
WORDS_TARGET = ["JOUR", "DAY", "TAG", "GIORNO", "DIA"]
TIMERS_CYCLE_1 = [268, 179, 209, 179]
TIMERS_CYCLE_2 = [265, 179, 209, 179]
OCR_LOG_DIR = os.path.join(BASE_PATH, "ocr_logs")

# === États globaux ===
timer_durations = TIMERS_CYCLE_1.copy()
thread_en_cours = False
etat = "WAITING"
masque = False
background = False
interruption = False
x_position = y_position = None

# === Config loader ===
def load_config():
    global x_position, y_position, background
    if not os.path.exists(CONFIG_FILE):
        return
    try:
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                if line.startswith("position="):
                    x_position, y_position = map(int, line.strip().split("=")[1].split(","))
                elif line.startswith("background="):
                    background = bool(int(line.strip().split("=")[1]))
    except Exception as e:
        print(f"Erreur lecture config : {e}")


def save_config():
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(f"position={x_position},{y_position}\n")
            f.write(f"background={int(background)}\n")
    except Exception as e:
        print(f"Erreur sauvegarde config : {e}")

load_config()

# === UI ===
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.wm_attributes("-transparentcolor", "black")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.08)
window_height = int(screen_height * 0.07)

if x_position is None or y_position is None:
    x_position = (screen_width - window_width) // 2
    y_position = 0

root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
root.withdraw()

label_font_size = int(screen_height * 0.014)
timer_font_size = int(label_font_size * 1.7)

label = tk.Label(root, text="Waiting for \nexpedition...", fg="#D3D3D3", bg="black", font=("Times New Roman", label_font_size))
label.pack()
timer_label = tk.Label(root, text="", fg="white", bg="black", font=("Times New Roman", timer_font_size))
timer_label.pack()

# === Drag logic ===
_drag_data = {"x": 0, "y": 0}

def start_drag(event):
    _drag_data["x"] = event.x
    _drag_data["y"] = event.y

def do_drag(event):
    global x_position, y_position
    dx = event.x - _drag_data["x"]
    dy = event.y - _drag_data["y"]
    x_position = root.winfo_x() + dx
    y_position = root.winfo_y() + dy
    root.geometry(f"+{x_position}+{y_position}")
    save_config()

root.bind("<ButtonPress-1>", start_drag)
root.bind("<B1-Motion>", do_drag)

# === Affichage ===
def update_labels(texte, temps=None):
    label.config(text=texte)
    if temps is not None:
        minutes, secondes = divmod(temps, 60)
        couleur = "red" if temps < 60 else "white"
        timer_label.config(text=f"{minutes}:{secondes:02}", fg=couleur)
    else:
        timer_label.config(text="")

    bg_color = "#0A0A0A" if background else "black"
    label.config(bg=bg_color)
    timer_label.config(bg=bg_color)
    root.config(bg=bg_color)

    if not masque:
        root.deiconify()
    else:
        root.withdraw()
    root.update_idletasks()

# === Détection OCR ===
def check_jour_text():
    os.makedirs(OCR_LOG_DIR, exist_ok=True)
    img = ImageGrab.grab()
    img_np = np.array(img)
    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

    width, height = img.size
    top = int(height * 0.5)
    bottom = int(height * 0.65)
    left = int(width * 0.35)
    right = int(width * 0.65)
    cropped = gray[top:bottom, left:right]

    _, cropped = cv2.threshold(cropped, 200, 255, cv2.THRESH_BINARY_INV)
    cropped = cv2.medianBlur(cropped, 3)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OCR_LOG_DIR, f"ocr_debug_{timestamp}.png")
    cv2.imwrite(filename, cropped)

    text = pytesseract.image_to_string(cropped, lang='eng', config='--oem 3 --psm 7')
    text_upper = text.upper()
    print(f"Texte détecté brut : {repr(text_upper)}")
    return any(mot in text_upper for mot in WORDS_TARGET)

# === Timers ===
def executer_cycle():
    global interruption, timer_durations
    for idx, duree in enumerate(timer_durations):
        if interruption:
            return
        label_text = "closing in" if idx % 2 == 0 else "closing now"
        for t in range(duree, -1, -1):
            if interruption:
                return
            update_labels(label_text, t)
            time.sleep(1)

def lancer_timers():
    global thread_en_cours, etat, interruption, timer_durations
    if thread_en_cours:
        return
    thread_en_cours = True
    interruption = False

    timer_durations = TIMERS_CYCLE_1.copy()
    etat = "TIMER"
    executer_cycle()
    if interruption:
        thread_en_cours = False
        return
    update_labels("Boss")
    etat = "WAITING_2"

    while etat == "WAITING_2":
        if interruption:
            thread_en_cours = False
            return
        if check_jour_text():
            break
        time.sleep(0.2)  # Réduction du délai à 100 ms

    timer_durations = TIMERS_CYCLE_2.copy()
    etat = "TIMER"
    executer_cycle()
    if interruption:
        thread_en_cours = False
        return
    update_labels("Boss")
    etat = "FINAL"

    # Maintenir une boucle active pour que les raccourcis clavier continuent de fonctionner
    while etat == "FINAL":
        if interruption:
            break
        time.sleep(0.2)

    thread_en_cours = False

# === Boucle principale ===
def boucle_detection():
    global etat, thread_en_cours
    while True:
        if etat == "WAITING" and not thread_en_cours:
            update_labels("Waiting for \nexpedition...")
            if check_jour_text():
                threading.Thread(target=lancer_timers).start()
        time.sleep(0.2)  # Réduction du délai à 100 ms

threading.Thread(target=boucle_detection, daemon=True).start()

# === Raccourcis clavier ===
def reset_timer():
    global etat, interruption, thread_en_cours
    interruption = True
    thread_en_cours = False
    etat = "WAITING"

def quit_app():
    root.quit()

def toggle_visibility():
    global masque
    masque = not masque
    update_labels(label.cget("text"))

def toggle_background():
    global background
    background = not background
    save_config()
    update_labels(label.cget("text"))

def lancer_timers_manuel():
    threading.Thread(target=lancer_timers).start()

def setup_hotkeys():
    kb.add_hotkey('ctrl+r', reset_timer)
    kb.add_hotkey('ctrl+q', quit_app)
    kb.add_hotkey('ctrl+h', toggle_visibility)
    kb.add_hotkey('ctrl+b', toggle_background)
    kb.add_hotkey('ctrl+s', lancer_timers_manuel)

setup_hotkeys()

try:
    root.mainloop()
except KeyboardInterrupt:
    print("Arrêt manuel du programme.")
    quit_app()
