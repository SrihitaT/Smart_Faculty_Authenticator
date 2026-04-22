# Smart_Faculty_Authenticator

# Biometric Butler: 3-Factor Authentication (3FA) Workspace Security

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![IoT](https://img.shields.io/badge/IoT-BLE-orange.svg)

An intelligent, multi-modal security system designed for faculty workspace protection. This "Butler" ensures that only authorized personnel can access sensitive directories and web environments by verifying **Who they are**, **What they know**, and **What they possess**.

## Security Architecture (The 3-Factor Pipeline)

The system eliminates the "Single Point of Failure" found in traditional password systems by requiring three distinct verification layers:

1.  **Biometric Factor (Who you are):** * Uses **RetinaFace** for high-accuracy detection and **VGG-Face** (via DeepFace) for identifying facial features.
2.  **Knowledge Factor (What you know):** * Integrated **Google Speech-to-Text API** to verify a customizable spoken passphrase.
3.  **Possession Factor (What you have):** * **Primary:** A **BLE (Bluetooth Low Energy)** scan for a registered hardware MAC address with a threshold of -85dBm.
    * **Secondary/Fallback:** An **Out-of-Band (OOB)** approval request pushed to the user's smartphone via the **Telegram Bot API**.

## Key Features
- **In-Memory Audio Processing:** Uses `io.BytesIO` to handle voice data in RAM, avoiding slow Disk I/O and enhancing privacy.
- **Interactive Enrollment:** A dedicated `enroll.py` script with Text-to-Speech (TTS) guidance for onboarding new users.
- **Dynamic Workspace Loading:** Uses the `os` library to automatically launch specific URLs (Linways, WhatsApp) and local folders upon successful authentication.
- **Asynchronous Execution:** Multi-threaded architecture ensures the webcam UI remains responsive while background scans (BLE/Voice) occur.

## Project Structure
```text
├── faculty_db/             # Biometric Store: Contains (.jpg) photos and (.pkl) embeddings
├── allmix6.py              # Main 3FA security pipeline and GUI
├── enroll.py               # Interactive enrollment script with TTS guidance
├── updatedfaculty_macs.json # Central Configuration (MAC addresses, Folders, Passwords)
└── README.md

## Tech Stack

AI/ML: DeepFace (VGG-Face), OpenCV, RetinaFace

Voice/Audio: Google Speech Recognition, gTTS, Pygame Mixer

Connectivity: Bleak (BLE), Telegram Bot API

System: Threading, OS, IO, JSON

 Installation & Setup
Clone the repository:

Bash
git clone [https://github.com/SrihitaT/Smart_Faculty_Authenticator.git](https://github.com/SrihitaT/Smart_Faculty_Authenticator.git)

Install dependencies:

Bash
pip install deepface opencv-python bleak python-telegram-bot SpeechRecognition gTTS pygame
Enroll a User:
Run enroll.py. Follow the voice prompts to capture your photo and enter your name in the terminal.

Bash
python enroll.py
Configuration:
Update updatedfaculty_macs.json with your specific Bluetooth MAC address, local folder paths, and desired voice password.

Launch the Butler:

Bash
python allmix6.py
 Academic Foundations
This project leverages foundational research in biometrics and security:

Parkhi et al. (2015): Deep Face Recognition (VGG-Face).

O'Gorman (2003): Philosophy of Multi-Factor Authentication.

Serengil & Ozpinar (2020): DeepFace Holistic Framework.

Disclaimer: This project is a security prototype. Ensure compliance with data protection regulations when storing biometric data.
