from videosdk import MeetingConfig, VideoSDK, MeetingEventHandler, Meeting, PubSubSubscribeConfig, PubSubPublishConfig
import asyncio
class AIAgent:
    def __init__(self, meeting_id: str, authToken: str, name: str):
        self.meeting_config = MeetingConfig(
            name=name,
            meeting_id=meeting_id,
            token=authToken,
            mic_enabled=False,
            webcam_enabled=False
        )
        # Listen to Meeting Events
        # subscribe to pubsub topic - GAME_MOVES
        # receive cliet's response
        self.ai_agent = VideoSDK.init_meeting(**self.meeting_config)
        
        
    async def join(self):
        self.ai_agent.add_event_listener(GameEventHandler(agent=self.ai_agent))
        await self.ai_agent.async_join()
    
    async def leave(self):
        self.ai_agent.leave()
    
class GameEventHandler(MeetingEventHandler):
    def __init__(self, agent: Meeting):
        self.pubsub_topic = "GAME_MOVES"
        self.agent = agent
            
    def receive_client_msg(self, data):
        message = data["message"]
        print(f"client's response : {message}")
        # LLM to generate server response
        # publish response back to client
    
    async def publish_to_pubsub(self):
        publish_config=PubSubPublishConfig(
            topic=self.pubsub_topic,
            message="" # llm response
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
        