import os
from pathlib import Path
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ProductionConfig:
    """Production configuration for Jarvis Assistant"""

    # Application Settings
    ENVIRONMENT = os.getenv('JARVIS_ENV', 'production')
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # API Keys
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    GOOGLE_CALENDAR_API_KEY = os.getenv('GOOGLE_CALENDAR_API_KEY')

    # Database Configuration
    DB_PATH = os.getenv('DB_PATH', 'jarvis.db')
    DB_BACKUP_PATH = os.getenv('DB_BACKUP_PATH', 'backup/jarvis_backup.db')

    # Server Configuration
    HOST = os.getenv('HOST', 'localhost')
    PORT = int(os.getenv('PORT', 8000))
    MODE = os.getenv('MODE', None)

    # Audio Configuration
    AUDIO_DEVICE_INDEX = int(os.getenv('AUDIO_DEVICE_INDEX', 0))
    AUDIO_SAMPLE_RATE = int(os.getenv('AUDIO_SAMPLE_RATE', 16000))
    AUDIO_CHUNK_SIZE = int(os.getenv('AUDIO_CHUNK_SIZE', 1024))

    # Voice Recognition
    VOICE_LANGUAGE = os.getenv('VOICE_LANGUAGE', 'en-US')
    VOICE_RATE = int(os.getenv('VOICE_RATE', 174))
    VOICE_VOLUME = float(os.getenv('VOICE_VOLUME', 0.9))

    # Security Settings
    ENABLE_FACE_AUTH = os.getenv('ENABLE_FACE_AUTH', 'true').lower() == 'true'
    ALLOW_REMOTE_ACCESS = os.getenv('ALLOW_REMOTE_ACCESS', 'false').lower() == 'true'
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', 3600))

    # Feature Flags
    ENABLE_WEATHER = os.getenv('ENABLE_WEATHER', 'true').lower() == 'true'
    ENABLE_CALENDAR = os.getenv('ENABLE_CALENDAR', 'true').lower() == 'true'
    ENABLE_NOTES = os.getenv('ENABLE_NOTES', 'true').lower() == 'true'
    ENABLE_NEWS = os.getenv('ENABLE_NEWS', 'true').lower() == 'true'
    ENABLE_SMART_HOME = os.getenv('ENABLE_SMART_HOME', 'false').lower() == 'true'

    # Logging Configuration
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/jarvis.log')
    LOG_MAX_SIZE = os.getenv('LOG_MAX_SIZE', '10MB')
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))

    # Performance Settings
    MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 10))
    CACHE_DURATION = int(os.getenv('CACHE_DURATION', 300))  # seconds
    API_RATE_LIMIT = int(os.getenv('API_RATE_LIMIT', 60))  # requests per minute

    # File Paths
    BASE_DIR = Path(__file__).parent.parent
    RECORDINGS_PATH = BASE_DIR / os.getenv('RECORDINGS_PATH', 'data/recordings')
    MODELS_PATH = BASE_DIR / os.getenv('MODELS_PATH', 'data/models')
    TEMP_PATH = BASE_DIR / os.getenv('TEMP_PATH', 'data/temp')

    # Ensure directories exist
    RECORDINGS_PATH.mkdir(parents=True, exist_ok=True)
    MODELS_PATH.mkdir(parents=True, exist_ok=True)
    TEMP_PATH.mkdir(parents=True, exist_ok=True)

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_keys = [
            'OPENWEATHER_API_KEY',
            'NEWS_API_KEY',
            'GOOGLE_CALENDAR_API_KEY'
        ]

        missing_keys = []
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)

        if missing_keys:
            print(f"Warning: Missing API keys: {missing_keys}")
            print("Some features may not work correctly.")
            return False

        return True

# Load production configuration
config = ProductionConfig()

# Validate configuration on import
if not config.validate():
    print("Configuration validation failed. Please check your .env file.")