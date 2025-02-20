from videosdk import MeetingConfig, VideoSDK, MeetingEventHandler
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
        self.ai_agent.add_event_listener()
        self.ai_agent = VideoSDK.init_meeting(**self.meeting_config)
        
        
    async def join(self):
        await self.ai_agent.async_join()
    
    async def leave(self):
        self.ai_agent.leave()
    
    