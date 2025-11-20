import os
import sys
import eel
from pathlib import Path

# Add deployment directory to path
sys.path.append(str(Path(__file__).parent / 'deployment'))

from backend.auth import recoganize
from backend.auth.recoganize import AuthenticateFace
from backend.feature import *
from backend.command import *
from backend import calendar
from backend import notes

# Load configuration based on environment
if os.getenv('JARVIS_ENV') == 'production':
    try:
        from backend.config_prod import config
        print("Production configuration loaded")
    except ImportError:
        print("Warning: Production config not found, using default settings")
        config = None
else:
    print("Development mode")
    config = None



def start():
    
    eel.init("frontend") 
    
    play_assistant_sound()
    @eel.expose
    def init():
        eel.hideLoader()
        speak("Welcome to Jarvis")
        speak("Ready for Face Authentication")
        flag = recoganize.AuthenticateFace()
        if flag ==1:
            speak("Face recognized successfully")
            eel.hideFaceAuth()
            eel.hideFaceAuthSuccess()
            speak("Welcome to Your Assistant")
            eel.hideStart()
            play_assistant_sound()
        else:
            speak("Face not recognized. Please try again")
        
    os.system('start msedge.exe --app="http://127.0.0.1:8000/index.html"')
    
    
    
    eel.start("index.html", mode=None, host="localhost", block=True) 

