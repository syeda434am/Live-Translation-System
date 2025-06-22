import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from typing import Optional

from com.mhire.config.config import Config
from com.mhire.services.transcription import Transcription
from com.mhire.services.translation import Translation

class GUI:
    def __init__(self, config: Config, transcription: Transcription, translation: Translation):
        self.root = tk.Tk()
        self.config = config
        self.transcription = transcription
        self.translation = translation
        
        # Initialize main window
        self.root.title("Real-time Multilingual Speech Translation (Groq API)")
        self.root.minsize(800, 600)
        self.root.state('zoomed')
        
        self.setup_gui()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_gui(self):
        """Set up the GUI components"""
        # Configure root window to expand
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        self._setup_language_selection(main_frame)
        self._setup_text_areas(main_frame)
        self._setup_buttons(main_frame)

    def _setup_language_selection(self, main_frame):
        """Set up language selection components"""
        # Create language selection frame
        lang_frame = ttk.Frame(main_frame)
        lang_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        lang_frame.columnconfigure(1, weight=1)
        
        # Source language selection
        src_frame = ttk.LabelFrame(lang_frame, text="Source Language")
        src_frame.pack(side=tk.LEFT, padx=5)
        self.src_lang_var = tk.StringVar(value="Auto")
        src_combo = ttk.Combobox(src_frame, textvariable=self.src_lang_var, 
                               values=list(self.translation.get_supported_languages().keys()), 
                               state="readonly", width=10)
        src_combo.pack(padx=5, pady=5)
        
        # Target language selection
        tgt_frame = ttk.LabelFrame(lang_frame, text="Target Language")
        tgt_frame.pack(side=tk.RIGHT, padx=5)
        self.tgt_lang_var = tk.StringVar(value="English")
        tgt_combo = ttk.Combobox(tgt_frame, textvariable=self.tgt_lang_var,
                               values=[lang for lang in self.translation.get_supported_languages().keys() if lang != "Auto"],
                               state="readonly", width=10)
        tgt_combo.pack(padx=5, pady=5)

    def _setup_text_areas(self, main_frame):
        """Set up text areas for transcription and translation"""
        # Create text areas frame
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.columnconfigure(1, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        # Transcription text area
        trans_frame = ttk.LabelFrame(text_frame, text="Transcription")
        trans_frame.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        trans_frame.columnconfigure(0, weight=1)
        trans_frame.rowconfigure(0, weight=1)
        
        self.text_area = scrolledtext.ScrolledText(trans_frame)
        self.text_area.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Translation text area
        tran_frame = ttk.LabelFrame(text_frame, text="Translation")
        tran_frame.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        tran_frame.columnconfigure(0, weight=1)
        tran_frame.rowconfigure(0, weight=1)
        
        self.translation_area = scrolledtext.ScrolledText(tran_frame)
        self.translation_area.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))

    def _setup_buttons(self, main_frame):
        """Set up control buttons"""
        # Create buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Create buttons
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_transcription)
        self.start_button.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_transcription, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))

    def update_gui_safely(self, widget: tk.Text, text: str) -> None:
        """Thread-safe method to update GUI widgets"""
        try:
            self.root.after(0, lambda: widget.insert(tk.END, text))
            self.root.after(0, lambda: widget.see(tk.END))
        except Exception as e:
            print(f"GUI update error: {e}")

    def start_transcription(self) -> None:
        """Start the transcription process"""
        self.transcription.start_stream()
        
        # Start processing thread
        self.process_thread = threading.Thread(target=self._process_audio)
        self.process_thread.start()
        
        # Update button states
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Add initial message
        src_lang = self.src_lang_var.get()
        tgt_lang = self.tgt_lang_var.get()
        self.text_area.insert(tk.END, f"Listening... Speak something! (Source: {src_lang})\n")
        self.translation_area.insert(tk.END, f"Translation will appear here (Target: {tgt_lang})\n")

    def stop_transcription(self) -> None:
        """Stop the transcription process"""
        self.transcription.stop_stream()
        if hasattr(self, 'process_thread'):
            self.process_thread.join(timeout=1.0)
        
        # Update button states safely
        try:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            # Add stopped message safely
            self.update_gui_safely(self.text_area, "\nTranscription stopped.\n")
            self.update_gui_safely(self.translation_area, "\nTranslation stopped.\n")
        except:
            pass

    def _process_audio(self) -> None:
        """Process audio and update GUI with results in real-time"""
        selected_src_lang = self.translation.get_language_code(self.src_lang_var.get())
        
        while self.transcription.running:
            transcription = self.transcription.get_next_transcription(selected_src_lang)
            
            if transcription:
                # Add newline only if transcription ends with sentence-ending punctuation
                ends_sentence = any(transcription.rstrip().endswith(p) for p in '.!?')
                newline = '\n' if ends_sentence else ' '
                
                # Update transcription area safely
                self.update_gui_safely(self.text_area, transcription + newline)
                
                # Get selected languages
                selected_tgt_lang = self.translation.get_language_code(self.tgt_lang_var.get())
                
                # Perform translation and update translation area safely
                translation = self.translation.translate_text(
                    transcription,
                    selected_src_lang or "en",  # Default to English if Auto
                    selected_tgt_lang
                )
                # Add newline to translation only for complete sentences
                self.update_gui_safely(self.translation_area, translation + newline)

    def on_closing(self) -> None:
        """Handle window closing event"""
        self.stop_transcription()
        self.root.destroy()

    def run(self) -> None:
        """Start the GUI main loop"""
        self.root.mainloop()