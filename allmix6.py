import cv2
import os
import time
import json
import asyncio
import threading
import io
import webbrowser
import sys
import requests
import speech_recognition as sr
from deepface import DeepFace
from bleak import BleakScanner
from gtts import gTTS
from pygame import mixer
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

# =========================
# 1. CONFIGURATION & STATE
# =========================
DB_PATH = "faculty_db"
FACULTY_JSON = "updatedfaculty_macs.json"
SCAN_WINDOW_SECONDS = 15 
SECRET_PASSWORD = "activate" 
TELEGRAM_TOKEN = "8147566009:AAElm-QC1Tfo9z48arviKok_9lCufP7zT_w"
CHAT_ID = "5790290228"

# Drive Paths
BASE_DOCS = r"C:\\Users\\SRIHITA\\Documents"
STUDENTS_DRIVE = os.path.join(BASE_DOCS, "Students_Drive")

mixer.init()
current_status = "SEARCHING FOR FACULTY"
is_authenticated = False 

def load_config():
    try:
        with open(FACULTY_JSON, "r") as f:
            data = json.load(f)
            return {k.lower(): v for k, v in data["faculty"].items()}, data["settings"]
    except Exception as e:
        print(f"Error loading JSON: {e}")
        sys.exit()

FACULTY_MAP, SETTINGS = load_config()

# =========================
# 2. SECURITY BUTLER CLASS
# =========================
class SecurityButler:
    def __init__(self):
        self.approval_status = "pending"

    async def start_telegram_bot(self):
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CallbackQueryHandler(self.handle_button))
        await app.initialize()
        await app.start()
        await app.updater.start_polling()

    async def handle_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        self.approval_status = "approved" if query.data == "approve" else "denied"
        await query.edit_message_text(text=f"Mobile Response: {self.approval_status.upper()}")

    def send_mobile_request(self, name):
        keyboard = {"inline_keyboard": [[
            {"text": "✅ Approve", "callback_data": "approve"},
            {"text": "❌ Deny", "callback_data": "deny"}
        ]]}
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID, 
            "text": f"🚨 <b>Butler Alert</b>\nIdentity: {name}\nAuthorize access?", 
            "reply_markup": json.dumps(keyboard), "parse_mode": "HTML"
        }
        requests.post(url, data=payload)

    async def scan_ble(self):
        start_time = time.time()
        while time.time() - start_time < SCAN_WINDOW_SECONDS:
            try:
                devices = await BleakScanner.discover(timeout=2.0)
                if any(d.address.lower() in FACULTY_MAP for d in devices): return True
            except: pass
        return False

butler_core = SecurityButler()

# =========================
# 3. UTILITIES & SEARCH
# =========================
def speak(text):
    global current_status
    current_status = f"SAYING: {text[:25]}..."
    # DISPLAY AI OUTPUT IN TERMINAL
    print(f"\n[AI BUTLER]: {text}") 
    try:
        tts = gTTS(text=text, lang="en")
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        mixer.music.load(fp, "mp3")
        mixer.music.play()
        while mixer.music.get_busy(): time.sleep(0.1)
    except: pass

def listen():
    global current_status
    current_status = "🎤 LISTENING..."
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=6, phrase_time_limit=5)
            query = r.recognize_google(audio).lower()
            
            # DISPLAY USER INPUT IN TERMINAL
            print(f"[USER]: {query}") 
            
            return query
        except Exception: 
            print("[USER]: (No audible speech detected)")
            return ""

def find_and_open_item(query, faculty_id):
    search_paths = [STUDENTS_DRIVE]

    num_map = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5"}
    stop_words = ["please", "open", "the", "show", "me", "find", "can", "you", "file"]
    
    words = query.split()
    search_keywords = [num_map.get(w, w) for w in words if w not in stop_words]

    speak(f"Searching drives for {' '.join(search_keywords)}...")
    found_items = []

    for drive in search_paths:
        for root, dirs, files in os.walk(drive):
            for item in files + dirs:
                if all(kw in item.lower() for kw in search_keywords):
                    found_items.append(os.path.join(root, item))

    if found_items:
        found_items.sort(key=len)
        os.startfile(found_items[0])
        speak("File opened. Task complete.")
    else:
        speak("No matching file found.")

# 4. AUTH WORKER (WITH AUTO-EXIT)

def auth_worker(detected_name):
    global is_authenticated, current_status
    
    speak(f"Hello {detected_name}. Provide secret word.")
    
    voice_input = listen() 
    if SECRET_PASSWORD in voice_input:
        speak("Voice verification successful. Verifying proximity.") 
        current_status = "📡 SCANNING BLE..."
        
        loop = asyncio.new_event_loop()
        ble_found = loop.run_until_complete(butler_core.scan_ble())
        
        if not ble_found:
            speak("BLE not found. Requesting mobile approval.")
            butler_core.approval_status = "pending"
            butler_core.send_mobile_request(detected_name)
            
            start_wait = time.time()
            while (time.time() - start_wait) < 30:
                if butler_core.approval_status == "approved":
                    ble_found = True
                    break
                elif butler_core.approval_status == "denied":
                    speak("Access denied.")
                    os._exit(0)
                time.sleep(0.5)

        if ble_found:
            is_authenticated = True
            current_status = "✅ AUTHORIZED"
            speak("Bluetooth verification successful. Access granted. What should I open?") 
            cmd = listen()
            if "linways" in cmd: webbrowser.open("https://linways.com/login")
            elif "whatsapp" in cmd: webbrowser.open("https://web.whatsapp.com")
            elif cmd: find_and_open_item(cmd, detected_name)
            
            time.sleep(2)
            os._exit(0) 
        else:
            speak("Timeout.")
            os._exit(0)
    else:
        speak("Wrong password.")
        os._exit(0)

# =========================
# 5. MAIN LOOP (RETINAFACE + VGG)
# =========================
async def main_loop():
    global current_status
    
    def bot_runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(butler_core.start_telegram_bot())
        loop.run_forever()
    threading.Thread(target=bot_runner, daemon=True).start()

    cap = cv2.VideoCapture(0)
    auth_thread_started = False

    print("--- Butler System Terminal Active ---")

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        color = (0, 255, 0) if is_authenticated else (0, 255, 255)
        cv2.rectangle(frame, (10, 10), (520, 60), (0,0,0), -1)
        cv2.putText(frame, f"BUTLER: {current_status}", (20, 45), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.imshow("Security Dashboard", frame)

        if not auth_thread_started and not is_authenticated:
            if int(time.time() * 10) % 20 == 0: 
                try:
                    results = DeepFace.find(img_path=frame, 
                                            db_path=DB_PATH, 
                                            model_name="VGG-Face", 
                                            detector_backend="retinaface", 
                                            enforce_detection=False, 
                                            silent=True)
                    if len(results) > 0 and not results[0].empty:
                        name = os.path.basename(results[0]["identity"][0]).split(".")[0]
                        threading.Thread(target=auth_worker, args=(name,), daemon=True).start()
                        auth_thread_started = True
                except: pass

        if cv2.waitKey(1) & 0xFF == ord("q"): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(main_loop())