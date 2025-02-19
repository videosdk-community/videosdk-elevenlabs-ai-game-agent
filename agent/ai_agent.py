from videosdk import MeetingConfig, VideoSDK
class AIAgent:
    def __init__(self, meeting_id: str, authToken: str, name: str):
        self.meeting_config = MeetingConfig(
            name=name,
            meeting_id=meeting_id,
            token=authToken,
            mic_enabled=False,
            webcam_enabled=False
        )
        
    async def join(self):
        ai_agent = VideoSDK.init_meeting(**self.meeting_config)
        await ai_agent.async_join()
    