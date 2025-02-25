from elevenlabs import ElevenLabs, VoiceSettings
from videosdk.stream import MediaStreamTrack
import os
import asyncio

api_key=os.getenv("ELEVENLABS_API_KEY")

# tts/elevenlabs.py
class ElevenLabsTTS:
    def __init__(self, output_track: MediaStreamTrack):
        self.elevenlabs_client = ElevenLabs(api_key=api_key)
        self.model = "eleven_turbo_v2_5"
        self.output_track = output_track
        self.queue = asyncio.Queue()
        self.loop = asyncio.get_event_loop()
        self.processing_task = asyncio.create_task(self.process_queue())

    async def process_queue(self):
        while True:
            text = await self.queue.get()
            # Run synchronous generation in executor
            tts_bytes = await self.loop.run_in_executor(
                None, 
                self._generate_sync,
                text
            )
            self.output_track.add_new_bytes(tts_bytes)
            self.queue.task_done()

    def _generate_sync(self, text):
        """Synchronous generation method"""
        print(f"Generating TTS for: {text}")
        return self.elevenlabs_client.generate(
            text=text,
            voice="Will",
            stream=True,
            output_format="pcm_24000",
            model=self.model,
            voice_settings=VoiceSettings(
                stability=0.71, 
                similarity_boost=0.5, 
                style=0.0, 
                use_speaker_boost=True
                
            )
        )

    async def generate(self, text):
        """Async interface for adding to queue"""
        await self.queue.put(text)