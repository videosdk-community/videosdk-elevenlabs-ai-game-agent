from videosdk import MeetingConfig, VideoSDK, MeetingEventHandler, Meeting, PubSubSubscribeConfig, PubSubPublishConfig, ParticipantEventHandler, Participant
import asyncio
import json
from intelligence.intelligence import OpenAiIntelligence
from tts.elevenlabs import ElevenLabsTTS
from agent.audio_stream_track import CustomAudioStreamTrack
from videosdk.stream import MediaStreamTrack
from stt.deepgram import DeepgramSTT

class AIAgent:
    def __init__(self, meeting_id: str, authToken: str, name: str):
        # 2
        self.loop = asyncio.get_running_loop()
        self.audio_track = CustomAudioStreamTrack(
            loop=self.loop,
            handle_interruption=True
        )
        
        self.meeting_config = MeetingConfig(
            name=name,
            meeting_id=meeting_id,
            token=authToken,
            mic_enabled=True,
            webcam_enabled=False,
            custom_microphone_audio_track=self.audio_track
        )
        # Listen to Meeting Events
        # subscribe to pubsub topic - GAME_MOVES``
        # receive cliet's response
        self.ai_agent = VideoSDK.init_meeting(**self.meeting_config)
        
        
        
        
    async def join(self):
        # 3
        self.ai_agent.add_event_listener(GameEventHandler(agent=self.ai_agent, audio_track=self.audio_track))
        await self.ai_agent.async_join()
    
    def leave(self):
        self.ai_agent.leave()
    
class GameEventHandler(MeetingEventHandler):
    def __init__(self, agent: Meeting, audio_track: MediaStreamTrack):
        super().__init__()
        self.agent = agent
        self.pubsub_topic = "GAME_MOVES"
        self.openai_client = OpenAiIntelligence()
        self.game_state = {
            "board": [None]*9,
            "current_player": "X",
            "winner": None,
            "game_over": False
        }
        
        # 4
        self.audio_track= audio_track
        self.tts = ElevenLabsTTS(output_track=self.audio_track)
        self.stt = DeepgramSTT(callback=self.handle_transcript)
        
    def check_winner(self):
        board = self.game_state["board"]
        lines = [
            [0,1,2], [3,4,5], [6,7,8],  # rows
            [0,3,6], [1,4,7], [2,5,8],  # columns
            [0,4,8], [2,4,6]  # diagonals
        ]
        for line in lines:
            a, b, c = line
            if board[a] and board[a] == board[b] == board[c]:
                return board[a]
        return None
   
    async def publish_game_state(self):
        state_message = {
            "type": "state_update",
            "game_state": self.game_state
        }
        await self.publish_to_pubsub(state_message)
 
    async def generate_ai_move(self):
            ai_move = self.openai_client.generate_server_response(game_state=self.game_state)
            # 1. get ai comment
            comment = ai_move.get("comment", "")
            
            # 2. Generate TTS and get the audio bytes
            await self.tts.generate(comment)

          
            await self.publish_to_pubsub(ai_move)
            await self.publish_game_state()
            
            
    async def validate_and_process_move(self, move: dict):
        position = int(move["position"])
        player = move["player"]
        
        if self.game_state["game_over"]:
            return
            
        if player != self.game_state["current_player"]:
            return
            
        if position < 0 or position > 8:
            return
            
        if self.game_state["board"][position] is not None:
            return

        # Update game state
        self.game_state["board"][position] = player
        self.game_state["current_player"] = "O" if player == "X" else "X"
        
        # Check for winner
        winner = self.check_winner()
        if winner or None not in self.game_state["board"]:
            self.game_state["winner"] = winner
            self.game_state["game_over"] = True
            await self.publish_game_state()
        elif player == "X":
            await self.generate_ai_move()

    def receive_client_msg(self, data):
        try:
            message = json.loads(data["message"])
            if message.get("type") == "reset":
                self.game_state = {
                    "board": [None]*9,
                    "current_player": "X",
                    "winner": None,
                    "game_over": False
                }
                asyncio.create_task(self.publish_game_state())
            elif message.get("type") == "move":
                asyncio.create_task(self.validate_and_process_move(message))
        except Exception as e:
            print(f"Error processing message: {str(e)}")

    async def publish_to_pubsub(self, ai_move: dict):
        publish_config=PubSubPublishConfig(
            topic=self.pubsub_topic,
            message=json.dumps(ai_move) # llm response
        )
        await self.agent.pubsub.publish(pubsub_config=publish_config)
                  
    async def subscribe_to_pubsub(self):
        pubsub_config = PubSubSubscribeConfig(
            topic=self.pubsub_topic,
            cb=self.receive_client_msg
        )
            
        await self.agent.pubsub.subscribe(pubsub_config=pubsub_config)

        
    def on_meeting_joined(self, data):
        asyncio.create_task(self.subscribe_to_pubsub())

    def on_participant_joined(self, participant):
        print(f"Participant {participant.display_name} joined")
        participant.add_event_listener(
            ParticipantSTTEventListener(stt=self.stt, participant=participant)
        )

    def on_participant_left(self, participant):
        print(f"Participant {participant.display_name} left")
        self.stt.stop(peer_id=participant.id)

    async def handle_transcript(self, transcript, peer_id, peer_name, is_final):
        print("text: ", transcript)
        # Check if the transcript is a game move
        position = await self.openai_client.parse_move(transcript)
        if position is not None and 0 <= position <= 8:
            if self.game_state["board"][position] is None and not self.game_state["game_over"]:
                move_msg = {"type": "move", "position": position, "player": "X"}
                await self.validate_and_process_move(move_msg)
        else:
            # Generate conversational response
            response = self.openai_client.generate_chat_response(transcript)
            await self.tts.generate(response)


class ParticipantSTTEventListener(ParticipantEventHandler):
    def __init__(self, stt: DeepgramSTT, participant: Participant):
        super().__init__()
        self.stt = stt
        self.participant = participant

    def on_stream_enabled(self, stream):
        if stream.kind == "audio":
            self.stt.start(
                peer_id=self.participant.id,
                peer_name=self.participant.display_name,
                track=stream.track
            )

    def on_stream_disabled(self, stream):
        if stream.kind == "audio":
            self.stt.stop(peer_id=self.participant.id)

        