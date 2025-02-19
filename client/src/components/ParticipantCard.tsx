import React from "react";
import { useParticipant } from "@videosdk.live/react-sdk";
import { Bot, User, Mic, MicOff } from "lucide-react";
import clsx from "clsx";

interface ParticipantCardProps {
  width?: string;
  participant: {
    id: string;
    displayName: string;
    local: boolean;
    width?: string;
  };
}

export const ParticipantCard: React.FC<ParticipantCardProps> = ({
  participant,
  width,
}) => {
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const audioRef = React.useRef<HTMLAudioElement>(null);

  const {
    webcamStream,
    micStream,
    webcamOn,
    micOn,
    isActiveSpeaker,
    displayName,
  } = useParticipant(participant.id);

  // Handle webcam stream
  React.useEffect(() => {
    if (videoRef.current && webcamStream && webcamOn) {
      const mediaStream = new MediaStream();
      mediaStream.addTrack(webcamStream.track);
      videoRef.current.srcObject = mediaStream;
      videoRef.current.play().catch((error) => {
        console.error("Error playing video:", error);
      });
    }

    return () => {
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    };
  }, [webcamStream, webcamOn]);

  // Handle audio stream
  React.useEffect(() => {
    if (audioRef.current && micStream && micOn) {
      const mediaStream = new MediaStream();
      mediaStream.addTrack(micStream.track);
      audioRef.current.srcObject = mediaStream;
      audioRef.current.play().catch((error) => {
        console.error("Error playing audio:", error);
      });
    }

    return () => {
      if (audioRef.current) {
        audioRef.current.srcObject = null;
      }
    };
  }, [micStream, micOn]);

  const isAI = participant.displayName.includes("AI");

  return (
    <div className="relative rounded-lg overflow-hidden bg-gray-800 aspect-video">
      <div className="absolute inset-0">
        {webcamOn && webcamStream ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted={participant.local}
            className={clsx(
              `w-full h-full object-cover ${`isAI ? w-[${width}]`}`,
              isActiveSpeaker && "ring-2 ring-blue-500"
            )}
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gray-700">
            <div
              className={clsx(
                "p-4 rounded-full",
                isActiveSpeaker ? "bg-blue-500/20" : "bg-gray-600"
              )}
            >
              {isAI ? (
                <Bot className="w-16 h-16 text-gray-400" />
              ) : (
                <User className="w-16 h-16 text-gray-400" />
              )}
            </div>
          </div>
        )}
      </div>

      <audio ref={audioRef} autoPlay playsInline muted={participant.local} />

      <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/80 to-transparent">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div
              className={clsx(
                "p-1.5 rounded-full",
                isAI ? "bg-blue-500/20" : "bg-gray-500/20"
              )}
            >
              {isAI ? (
                <Bot className="w-4 h-4 text-blue-400" />
              ) : (
                <User className="w-4 h-4 text-gray-400" />
              )}
            </div>
            <span className="text-white font-medium">
              {displayName || participant.displayName}{" "}
              {participant.local && "(You)"}
            </span>
          </div>
          <div className="flex items-center space-x-2">
            {isActiveSpeaker && (
              <span className="px-2 py-0.5 text-xs bg-green-500 rounded-full text-white">
                Speaking
              </span>
            )}
            {micOn ? (
              <Mic className="w-4 h-4 text-white" />
            ) : (
              <MicOff className="w-4 h-4 text-red-500" />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
