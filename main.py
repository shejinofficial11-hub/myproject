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
    # Configure Eel with production settings if available
    if config:
        host = config.HOST
        port = config.PORT
        mode = config.MODE
        print(f"Starting Jarvis on {host}:{port} in {mode or 'default'} mode")
    else:
        host = "localhost"
        port = 8000
        mode = None

    eel.init("frontend")

    play_assistant_sound()

    @eel.expose
    def init():
        eel.hideLoader()
        speak("Welcome to Jarvis")

        # Skip face auth in production if disabled
        if config and not config.ENABLE_FACE_AUTH:
            speak("Face authentication is disabled")
            eel.hideFaceAuth()
            eel.hideFaceAuthSuccess()
            speak("Welcome to Your Assistant")
            eel.hideStart()
            play_assistant_sound()
        else:
            speak("Ready for Face Authentication")
            flag = recoganize.AuthenticateFace()
            if flag == 1:
                speak("Face recognized successfully")
                eel.hideFaceAuth()
                eel.hideFaceAuthSuccess()
                speak("Welcome to Your Assistant")
                eel.hideStart()
                play_assistant_sound()
            else:
                speak("Face not recognized. Please try again")

    # Only auto-open browser in development mode
    if not config or config.DEBUG:
        if os.name == 'nt':  # Windows
            os.system(f'start msedge.exe --app="http://{host}:{port}/index.html"')
        elif os.name == 'posix':  # Linux/Mac
            os.system(f'xdg-open http://{host}:{port}/index.html')

    # Start Eel server
    eel.start("index.html", mode=mode, host=host, port=port, block=True)

def main():
    """Main entry point for production deployment"""
    try:
        # Set up logging for production
        if config:
            import logging
            from pathlib import Path

            log_dir = Path(config.LOG_FILE_PATH).parent
            log_dir.mkdir(parents=True, exist_ok=True)

            logging.basicConfig(
                filename=config.LOG_FILE_PATH,
                level=getattr(logging, config.LOG_LEVEL),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )

            logging.info("Jarvis AI Assistant starting in production mode")

        start()

    except Exception as e:
        if config:
            import logging
            logging.error(f"Failed to start Jarvis: {e}")
        else:
            print(f"Failed to start Jarvis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 

