import os
import wave
import numpy as np
import requests
from typing import Optional, Dict, Any, List, Tuple
import queue
import sounddevice as sd
from dataclasses import dataclass
import time

from com.mhire.config.config import Config
from com.mhire.services.vad import VadOptions, get_speech_timestamps, collect_chunks

class Transcription:
    def __init__(self, config: Config):
        self.config = config
        self.sample_rate = 16000
        self.audio_queue = queue.Queue()
        self.running = False
        self.silence_threshold = 0.01
        self.min_silence_duration = 0.7
        self.max_sentence_duration = 10.0
        
        # Initialize VAD options
        self.vad_options = VadOptions(
            threshold=0.5,
            min_speech_duration_ms=250,
            min_silence_duration_ms=700,
            speech_pad_ms=30,
            max_speech_duration_s=10.0
        )
        
        self.audio_data = []
        self.silence_frames = 0
        self.total_frames = 0
        self.last_processed_time = 0

    def audio_callback(self, indata: np.ndarray, frames: int, time_info: Dict, status: Any) -> None:
        """Callback for audio input"""
        if status:
            print(status)
        self.audio_queue.put(indata.copy())

    def start_stream(self) -> None:
        """Start the audio stream"""
        self.running = True
        self.audio_data = []
        self.silence_frames = 0
        self.total_frames = 0
        self.last_processed_time = time.time()
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self.audio_callback
        )
        self.stream.start()

    def stop_stream(self) -> None:
        """Stop the audio stream"""
        if self.running:
            self.running = False
            if hasattr(self, 'stream'):
                self.stream.stop()
                self.stream.close()

    def process_audio_chunk(self, audio_chunk: np.ndarray, selected_src_lang: Optional[str] = None) -> Optional[str]:
        """Process a chunk of audio and return transcription"""
        # Apply VAD to remove silence and noise
        speech_timestamps = get_speech_timestamps(
            audio_chunk,
            self.vad_options,
            sampling_rate=self.sample_rate
        )
        
        if not speech_timestamps:
            return None

        # Extract speech segments
        audio_segments, _ = collect_chunks(audio_chunk, speech_timestamps)
        processed_audio = np.concatenate(audio_segments)
        
        # Save processed audio as temporary WAV file
        temp_wav = "temp_audio.wav"
        with wave.open(temp_wav, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes((processed_audio * 32767).astype(np.int16).tobytes())

        try:
            # Use Groq's audio transcription API
            with open(temp_wav, 'rb') as audio_file:
                files = {
                    'file': ('audio.wav', audio_file, 'audio/wav'),
                    'model': (None, self.config.GROQ_TRANSCRIPTION_MODEL),
                }
                
                if selected_src_lang:
                    files['language'] = (None, selected_src_lang)
                
                response = requests.post(
                    self.config.GROQ_TRANSCRIPTION_ENDPOINT,
                    headers={"Authorization": f"Bearer {self.config.GROQ_API_KEY}"},
                    files=files
                )
            
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
                
            if response.status_code == 200:
                return response.json()['text']
            else:
                print(f"Transcription error: {response.text}")
                return None

        except Exception as e:
            print(f"Error during transcription: {e}")
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            return None

    def get_next_transcription(self, selected_src_lang: Optional[str] = None) -> Optional[str]:
        """Get next transcription from the audio stream"""
        try:
            data = self.audio_queue.get(timeout=0.1)
            current_frame = data.flatten()
            self.audio_data.append(current_frame)
            self.total_frames += len(current_frame)
            
            # Calculate audio energy for silence detection
            frame_energy = np.sqrt(np.mean(current_frame**2))
            
            # Update silence counter
            if frame_energy < self.silence_threshold:
                self.silence_frames += len(current_frame)
            else:
                self.silence_frames = 0
            
            # Convert frames to duration
            silence_duration = self.silence_frames / self.sample_rate
            total_duration = self.total_frames / self.sample_rate
            current_time = time.time()
            
            # Check if we should process the current audio
            should_process = (
                (silence_duration >= self.min_silence_duration and total_duration > 1.0) or
                total_duration >= self.max_sentence_duration or
                (total_duration >= 2.0 and current_time - self.last_processed_time >= 2.0)
            )
            
            if should_process and self.audio_data:
                audio_chunk = np.concatenate(self.audio_data)
                transcription = self.process_audio_chunk(audio_chunk, selected_src_lang)
                
                # Reset buffers and counters
                self.audio_data = []
                self.silence_frames = 0
                self.total_frames = 0
                self.last_processed_time = current_time
                
                if transcription:
                    return transcription.strip()
            
        except queue.Empty:
            pass  # No new audio data
        except Exception as e:
            print(f"Error during processing: {e}")
        
        return None