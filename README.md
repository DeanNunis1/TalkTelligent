# TalkTelligent

This program provides an interface for real-time audio transcription using a microphone. It includes functionality for detecting questions within the transcriptions and provides answers to them using OpenAI's GPT-4.

## Installation

Ensure that Python 3.8+ is installed on your machine. The application also requires the following Python libraries: tkinter, pyaudio, asyncio, websockets, json, openai, pymysql, and bcrypt. Install these using pip:

```bash
pip install requirements.txt
```

## Usage

Run the GUI.py script to start the application. Once running, you can log in or register a new account. After logging in, click the "Start Transcription" button to start transcribing audio from your default microphone. If a question is detected in the transcription, it will be sent to OpenAI's GPT-4 model for answering. The application also keeps track of your total usage time.

## Files

- **GUI.py:** This script handles the graphical user interface for the application, including the login and registration screens and the main transcription screen.

- **TT_Backend.py:** This script handles the core functionality of the application. It uses pyaudio to get audio data from the microphone, sends this data to Deepgram for real-time transcription, detects questions within the transcriptions, and sends these questions to OpenAI's GPT-4 model for answering.

- **Database.py:** This script handles interaction with the database. It includes functionality for logging in, registering a new account, and tracking the total usage time.

## Security Notice

Please do not hardcode your database credentials or API keys into your scripts. Instead, use environment variables or a secure secret manager to store these.

