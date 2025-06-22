import os
from dotenv import load_dotenv
import logging
from logging.config import dictConfig

class Config:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Environment variables
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.GROQ_TRANSLATION_MODEL = os.getenv("GROQ_TRANSLATION_MODEl")
        self.GROQ_TRANSCRIPTION_MODEL = os.getenv("GROQ_TRANSCRIPTION_MODEL")
        self.GROQ_TRANSCRIPTION_ENDPOINT = os.getenv("GROQ_TRANSCRIPTION_ENDPOINT")
        self.GROQ_TRANSLATION_ENDPOINT = os.getenv("GROQ_TRANSLATION_ENDPOINT")


        # Other config variables can be added here

        # Setup logging configuration
        self.setup_logging()

    def setup_logging(self):
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": "INFO",
                },
            },
            "root": {
                "handlers": ["console"],
                "level": "INFO",
            },
        }
        dictConfig(logging_config)

    def get_logger(self, name=None):
        return logging.getLogger(name)
