import asyncio
from videosdk.stream import MediaStreamTrack
import traceback
from typing import Dict, List
import numpy as np

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    ListenWebSocketClient
)
from dotenv import load_dotenv
import os
from asyncio.log import logger

LEARNING_RATE = 0.1
LENGTH_THRESHOLD = 5
SMOOTHING_FACTOR = 3
BASE_WPM = 150.0
VAD_THRESHOLD_MS = 25
UTTERANCE_CUTOFF_MS = 300

load_dotenv()

class DeepgramSTT:
    def __init__(self, callback):
        self.callback = callback
        self.deepgram_connections: Dict[str, ListenWebSocketClient] = {}
        self.finalize_called: Dict[str, bool] = {}
        self.vad_threshold_ms: int = VAD_THRESHOLD_MS
        self.utterance_cutoff_ms: int = UTTERANCE_CUTOFF_MS
        self.model = "nova-2"
        self.speed_coefficient: float = 1.0
        self.wpm_0 = BASE_WPM * self.speed_coefficient
        self.wpm = self.wpm_0
        self.speed_coefficient = self.speed_coefficient
        self.language = "en-US"
        self.buffer = ""
        self.words_buffer = []
        
        # Initialize Deepgram Client with keepalive
        self.client = DeepgramClient(
            api_key=os.getenv("DEEPGRAM_API_KEY"),
            config=DeepgramClientOptions(options={"keepalive": True}),
        )

    def start(self, peer_id: str, peer_name: str, track):
        def on_transcript(connection, result, **kwargs):
            self._handle_transcript(peer_id=peer_id, peer_name=peer_name, result=result)

        def on_error(connection, error, **kwargs):
            print(f"Deepgram error for {peer_id}: {error}")

        def on_close(connection, close, **kwargs):
            print(f"Deepgram connection closed for {peer_id}")
        
        def on_open(connection, open, **kwargs):
            print(f"Deepgram connection opened fro {peer_id}")

        # Configure live transcription options
        options = LiveOptions(
            model=self.model,
            language=self.language,
            smart_format=True,
            encoding="linear16",
            channels=2,
            sample_rate=48000,
            interim_results=True,
            vad_events=True,
            filler_words=True,
            punctuate=True,
            endpointing=int(self.vad_threshold_ms * (1 / self.speed_coefficient)),
            utterance_end_ms=max(
                int(self.utterance_cutoff_ms * (1 / self.speed_coefficient)), 1000
            ),
            no_delay=True,
        )

        # Create and configure Deepgram connection
        dg_connection = self.client.listen.live.v("1")
        dg_connection.on(LiveTranscriptionEvents.Open, on_open)
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_transcript)
        dg_connection.on(LiveTranscriptionEvents.Close, on_close)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)
        dg_connection.start(options)

        self.deepgram_connections[peer_id] = dg_connection
        self.finalize_called[peer_id] = False

        # Start audio processing task
        asyncio.create_task(self._process_audio(peer_id, track))
    
    async def _process_audio(self, peer_id: str, track: MediaStreamTrack):
        try:
            while True:
                frame = await track.recv()
                audio_data = frame.to_ndarray()
                pcm_frame = audio_data.flatten().astype(np.int16).tobytes()
                
                if peer_id in self.deepgram_connections:
                    self.deepgram_connections[peer_id].send(pcm_frame)
        except Exception as e:
            print(f"Audio processing error for {peer_id}: {e}")
            traceback.print_exc()
        finally:
            self._cleanup(peer_id)

    def update_speed_coefficient(self, wpm: int, message: str):
        if wpm is not None:
            length = len(message.strip().split())
            p_t = min(
                1,
                LEARNING_RATE
                * ((length + SMOOTHING_FACTOR) / (LENGTH_THRESHOLD + SMOOTHING_FACTOR)),
            )
            self.wpm = self.wpm * (1 - p_t) + wpm * p_t
            self.speed_coefficient = self.wpm / BASE_WPM
            logger.info(f"Set speed coefficient to {self.speed_coefficient}")
            
    def produce_text(self, text: str, peer_name: str, is_final: bool = False):
        try:
            if is_final and text:
                # Schedule the async callback to run in the existing loop:
                self.callback(peer_name, text)
        except RuntimeError:
            # This catches the “no running event loop” scenario in case
            # the code is invoked outside of any running loop. You may
            # need to initialize your own loop or handle differently.
            print("No running event loop. Make sure to run in an async context.")
        except Exception as e:
            print("Error while producing text", e)

    def is_endpoint(self, deepgram_response):
        is_endpoint = (deepgram_response.channel.alternatives[0].transcript) and (
            deepgram_response.speech_final
        )
        return is_endpoint

    def calculate_duration(self, words: List[dict]) -> float:
        if len(words) == 0:
            return 0.0
        return words[-1]["end"] - words[0]["start"]
        
    def _handle_transcript(self, peer_id, peer_name, result):
        try:
            top_choice = result.channel.alternatives[0]

            if len(top_choice.transcript) == 0:
                return

            # Check for transcript, confidentce and
            if (
                top_choice.transcript
                and top_choice.confidence > 0.0
                and result.is_final
            ):
                # Get words
                words = top_choice.words
                if words:
                    # Add words to buffer
                    self.words_buffer.extend(words)

                self.buffer = f"{self.buffer} {top_choice.transcript}"
                

            if (self.buffer and self.is_endpoint(result)) or self.finalize_called[peer_id]:

                duration_seconds = self.calculate_duration(self.words_buffer)
                # print("Duration seconds", duration_seconds)

                if duration_seconds is not None:
                    wpm = (
                        60 * len(self.buffer.split()) / duration_seconds
                        if duration_seconds
                        else None
                    )
                    print("WPM", wpm)
                    if wpm is not None:
                        self.update_speed_coefficient(wpm=wpm, message=self.buffer)

                self.produce_text(self.buffer, peer_name=peer_name, is_final=True)
                self.buffer = ""
                self.words_buffer = []

            if top_choice.transcript and top_choice.confidence > 0.0:
                if not result.is_final:
                    interim_message = f"{self.buffer} {top_choice.transcript}"
                else:
                    interim_message = self.buffer

                # if interim_message:
                #     self.produce_text(interim_message, peer_name=peer_name,is_final=False)

        except Exception as e:
            print("Error while transcript processing", e)

    def stop(self, peer_id: str):
        self._cleanup(peer_id)

    def _cleanup(self, peer_id: str):
        if peer_id in self.deepgram_connections:
            self.finalize_called[peer_id] = True
            connection = self.deepgram_connections.pop(peer_id)
            connection.finalize()
            connection.finish()