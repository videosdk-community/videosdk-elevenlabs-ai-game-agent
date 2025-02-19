// import React from "react";
// import { useMeeting } from "@videosdk.live/react-sdk";
// import { Phone, Video, VideoOff, Mic, MicOff } from "lucide-react";

// interface MeetingControlsProps {
//   setMeetingId: any;
// }

// export const MeetingControls: React.FC<MeetingControlsProps> = ({
//   setMeetingId,
// }) => {
//   const { toggleMic, toggleWebcam, localMicOn, localWebcamOn, end } =
//     useMeeting();
//   const handleEndMeeting = () => {
//     end();
//     setMeetingId(null);
//   };
//   return (
//     <div className="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/90 to-transparent">
//       <div className="flex items-center justify-center space-x-4">
//         <button
//           onClick={() => toggleMic()}
//           className={`p-3 rounded-full ${
//             localMicOn
//               ? "bg-gray-700 hover:bg-gray-600"
//               : "bg-red-500 hover:bg-red-600"
//           }`}
//         >
//           {localMicOn ? (
//             <Mic className="w-6 h-6 text-white" />
//           ) : (
//             <MicOff className="w-6 h-6 text-white" />
//           )}
//         </button>

//         <button
//           onClick={() => toggleWebcam()}
//           className={`p-3 rounded-full ${
//             localWebcamOn
//               ? "bg-gray-700 hover:bg-gray-600"
//               : "bg-red-500 hover:bg-red-600"
//           }`}
//         >
//           {localWebcamOn ? (
//             <Video className="w-6 h-6 text-white" />
//           ) : (
//             <VideoOff className="w-6 h-6 text-white" />
//           )}
//         </button>

//         <button
//           onClick={() => handleEndMeeting()}
//           className="p-3 rounded-full bg-red-500 hover:bg-red-600"
//         >
//           <Phone className="w-6 h-6 text-white transform rotate-225" />
//         </button>
//       </div>
//     </div>
//   );
// };

import React from "react";
import { useMeeting } from "@videosdk.live/react-sdk";
import { Phone, Video, VideoOff, Mic, MicOff } from "lucide-react";

interface MeetingControlsProps {
  setMeetingId: (id: string | null) => void;
}

export const MeetingControls: React.FC<MeetingControlsProps> = ({
  setMeetingId,
}) => {
  const { toggleMic, toggleWebcam, localMicOn, localWebcamOn, end } =
    useMeeting();

  const handleEndMeeting = () => {
    end();
    setMeetingId(null);
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/90 to-transparent">
      <div className="flex items-center justify-center space-x-4">
        <button
          onClick={() => toggleMic()}
          className={`p-3 rounded-full ${
            localMicOn
              ? "bg-gray-700 hover:bg-gray-600"
              : "bg-red-500 hover:bg-red-600"
          }`}
        >
          {localMicOn ? (
            <Mic className="w-6 h-6 text-white" />
          ) : (
            <MicOff className="w-6 h-6 text-white" />
          )}
        </button>

        <button
          onClick={() => toggleWebcam()}
          className={`p-3 rounded-full ${
            localWebcamOn
              ? "bg-gray-700 hover:bg-gray-600"
              : "bg-red-500 hover:bg-red-600"
          }`}
        >
          {localWebcamOn ? (
            <Video className="w-6 h-6 text-white" />
          ) : (
            <VideoOff className="w-6 h-6 text-white" />
          )}
        </button>

        <button
          onClick={() => handleEndMeeting()}
          className="p-3 rounded-full bg-red-500 hover:bg-red-600"
        >
          <Phone className="w-6 h-6 text-white transform rotate-225" />
        </button>
      </div>
    </div>
  );
};
