import cv2
import os
import time
from gtts import gTTS
from pygame import mixer
import io

# --- 1. SETUP ---
DB_DIR = "faculty_db"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# Initialize Pygame Mixer for Audio
mixer.init()

def speak(text):
    """Converts text to speech and plays it immediately."""
    print(f"Assistant: {text}")
    tts = gTTS(text=text, lang='en')
    # Save to a byte stream so we don't clutter the folder with mp3 files
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    mixer.music.load(fp, 'mp3')
    mixer.music.play()
    while mixer.music.get_busy(): # Wait for audio to finish
        time.sleep(0.1)

# --- 2. MAIN PROCESS ---
cap = cv2.VideoCapture(0) # 0 is your default laptop webcam

speak("Hello. Please look at the camera and press the Spacebar to capture your photo.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Show the live feed
    cv2.imshow("Enrollment - Press SPACE to Capture", frame)
    
    key = cv2.waitKey(1)
    
    # Press Space (ASCII 32)
    if key == 32:
        speak("Image captured. Please type your name in the terminal.")
        
        # Get name from Terminal
        name = input("Enter Faculty Name: ").strip()
        
        if name:
            filename = f"{name}.jpg"
            save_path = os.path.join(DB_DIR, filename)
            cv2.imwrite(save_path, frame)
            
            speak(f"Success. Faculty {name} has been added to the database.")
            break
        else:
            speak("Name cannot be empty. Please try again.")

    # Press ESC to quit
    elif key == 27:
        break

cap.release()
cv2.destroyAllWindows()