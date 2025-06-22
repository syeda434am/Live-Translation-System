#!/usr/bin/env python3
from com.mhire.config.config import Config
from com.mhire.services.transcription import Transcription
from com.mhire.services.translation import Translation
from com.mhire.visuals.gui import GUI

def main():
    # Initialize configuration
    config = Config()
    
    # Initialize services
    transcription_service = Transcription(config)
    translation_service = Translation(config)
    
    # Initialize and run GUI
    gui = GUI(config, transcription_service, translation_service)
    gui.run()

if __name__ == "__main__":
    main()