# # stt/deepgram.py
# import asyncio
# from deepgram import (
#     Deepgram,
    
# )
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class DeepgramSTT:
#     def __init__(self, callback):
#         self.deepgram = Deepgram(os.getenv("DEEPGRAM_API_KEY"))
#         self.callback = callback
#         self.transcriptions = {}

#     def start(self, peer_id, peer_name, track):
#         loop = asyncio.get_event_loop()
#         self.transcriptions[peer_id] = loop.create_task(
#             self.transcribe_audio(peer_id, track)
#         )

#     async def transcribe_audio(self, peer_id, track):
#         dg_connection = self.deepgram.transcription.live({
#             'model': 'nova-2',
#             'interim_results': False,
#             'smart_format': True,
#         })

#         dg_connection.registerHandler(dg_connection.event.CLOSE, lambda _: print(f"Deepgram connection closed for {peer_id}"))
#         dg_connection.registerHandler(dg_connection.event.TRANSCRIPT_RECEIVED, lambda data: self.handle_transcript(data, peer_id))

#         while True:
#             try:
#                 frame = await track.recv()
#                 dg_connection.send(frame.data)
#             except Exception as e:
#                 print(f"Error in transcribing audio: {e}")
#                 break

#         dg_connection.finish()

#     def handle_transcript(self, data, peer_id):
#         transcript = data['channel']['alternatives'][0]['transcript']
#         if transcript.strip():
#             asyncio.create_task(self.callback(transcript))

#     def stop(self, peer_id):
#         if peer_id in self.transcriptions:
#             self.transcriptions[peer_id].cancel()
#             del self.transcriptions[peer_id]


# stt/deepgram.py

import asyncio
from datetime import datetime, timezone
import traceback
from typing import Dict
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

load_dotenv()

class DeepgramSTT:
    def __init__(self, callback):
        self.callback = callback
        self.deepgram_connections: Dict[str, ListenWebSocketClient] = {}
        self.finalize_called: Dict[str, bool] = {}
        
        # Initialize Deepgram Client with keepalive
        self.client = DeepgramClient(
            api_key=os.getenv("DEEPGRAM_API_KEY"),
            config=DeepgramClientOptions(options={"keepalive": True}),
        )

    def start(self, peer_id: str, peer_name: str, track):
        def on_transcript(connection, result, **kwargs):
            self._handle_transcript(peer_id, peer_name, result)

        def on_error(connection, error, **kwargs):
            print(f"Deepgram error for {peer_id}: {error}")

        def on_close(connection, close, **kwargs):
            print(f"Deepgram connection closed for {peer_id}")
        
        def on_open(connection, open, **kwargs):
            print(f"Deepgram connection opened fro {peer_id}")

        # Configure live transcription options
        options = LiveOptions(
            model="nova-2",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=48000,
            interim_results=True,
            vad_events=True,
            punctuate=True,
            endpointing=300,
            utterance_end_ms=1000
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

    async def _process_audio(self, peer_id: str, track):
        try:
            while not self.finalize_called.get(peer_id, True):
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

    def _handle_transcript(self, peer_id: str, peer_name: str, result):
        try:
            transcript = result.channel.alternatives[0].transcript
            print("Current Transcipt", transcript)
            if transcript.strip():
                is_final = result.is_final
                self.callback(transcript, peer_id, peer_name, is_final)
        except KeyError as e:
            print(f"Error parsing transcript: {e}")

    def stop(self, peer_id: str):
        self._cleanup(peer_id)

    def _cleanup(self, peer_id: str):
        if peer_id in self.deepgram_connections:
            self.finalize_called[peer_id] = True
            connection = self.deepgram_connections.pop(peer_id)
            connection.finalize()
            connection.finish()