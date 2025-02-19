import React from "react";
import axios from "axios";
import { Toaster, toast } from "sonner";
import {
  MeetingProvider,
  useMeeting,
  usePubSub,
} from "@videosdk.live/react-sdk";
import { Loader2, GamepadIcon } from "lucide-react";
import { ParticipantCard } from "./components/ParticipantCard";
import { TicTacToe } from "./components/TicTacToe";
import { MeetingControls } from "./components/MeetingControls";
import type { GameState } from "./types";

const VIDEOSDK_TOKEN = import.meta.env.VITE_APP_AUTH_TOKEN;

const initialGameState: GameState = {
  board: Array(9).fill(null),
  currentPlayer: "X",
  winner: null,
  isGameOver: false,
};

interface MeetingViewProps {
  meetingId: string;
  setMeetingId: (id: string | null) => void;
  playerName: string;
}

const MeetingView: React.FC<MeetingViewProps> = ({
  setMeetingId,
  meetingId,
}) => {
  const { participants, localParticipant } = useMeeting();
  const [gameState, setGameState] = React.useState<GameState>(initialGameState);
  const [aiJoined, setAiJoined] = React.useState(false);

  const { publish } = usePubSub("GAME_MOVES", {
    onMessageReceived: (data) => {
      const message = JSON.parse(data.message);
      switch (message.type) {
        case "move":
          if (!gameState.isGameOver) {
            handleMove(message.position, message.player);
          }
          break;

        case "game_over":
          setGameState((prev) => ({
            ...prev,
            winner: message.winner,
            isGameOver: true,
            board: message.finalBoard,
          }));
          break;

        case "reset":
          setGameState(initialGameState);
          break;
      }
    },
  });

  // Replace existing handleMove with:
  const handleMove = (position: number, player: "X" | "O") => {
    // check boundaries
    if (gameState.isGameOver) {
      toast.error("Game already finished!");
      return;
    }
    if (position < 0 || position > 8 || gameState.board[position]) {
      toast.error("Invalid move!");
      return;
    }

    // reset game state
    setGameState((prev) => {
      const newBoard = [...prev.board];
      newBoard[position] = player;

      const winner = calculateWinner(newBoard);
      const isDraw = !winner && newBoard.every((cell) => cell !== null);

      if (winner || isDraw) {
        publish(
          JSON.stringify({
            type: "game_over",
            winner,
            finalBoard: newBoard,
          }),
          { persist: true }
        );
      }

      return {
        board: newBoard,
        currentPlayer: player === "X" ? "O" : "X",
        winner,
        isGameOver: !!winner || isDraw,
      };
    });
  };

  const handleGameReset = () => {
    publish(JSON.stringify({ type: "reset" }), { persist: true });
    setGameState(initialGameState);
  };

  const inviteAI = async () => {
    try {
      await axios.post("http://127.0.0.1:8000/join-player", {
        meeting_id: meetingId,
        token: VIDEOSDK_TOKEN,
      });
      toast.success("AI Agent joined the game!");
    } catch (error) {
      toast.error("Failed to invite AI Agent");
    }
  };

  const calculateWinner = (board: Array<string | null>): string | null => {
    const lines = [
      [0, 1, 2],
      [3, 4, 5],
      [6, 7, 8],
      [0, 3, 6],
      [1, 4, 7],
      [2, 5, 8],
      [0, 4, 8],
      [2, 4, 6],
    ];

    for (const [a, b, c] of lines) {
      if (board[a] && board[a] === board[b] && board[a] === board[c]) {
        return board[a];
      }
    }
    return null;
  };

  React.useEffect(() => {
    const aiParticipant = Array.from(participants.values()).find((p) =>
      p.displayName.includes("AI")
    );
    setAiJoined(!!aiParticipant);
  }, [participants]);

  if (!meetingId || !localParticipant) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div
          className="fixed inset-0 bg-cover bg-center bg-no-repeat opacity-20"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?q=80&w=1920')",
          }}
        />
        <div className="relative z-10 flex flex-col items-center space-y-4">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
          <p className="text-white text-lg">Setting up your game...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div
        className="fixed inset-0 bg-cover bg-center bg-no-repeat opacity-20"
        style={{
          backgroundImage:
            "url('https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?q=80&w=1920')",
        }}
      />

      <div className="relative z-10 container mx-auto px-4 py-8">
        {!aiJoined ? (
          <div className="flex flex-col items-center justify-center min-h-[80vh] space-y-8">
            <div className="w-full max-w-xl">
              <ParticipantCard participant={localParticipant} />
            </div>

            <div className="bg-gray-800/90 p-8 rounded-lg shadow-xl text-center max-w-md w-full">
              <p className="text-gray-300 mb-6">Tic Tac Toe!</p>
              <button
                onClick={inviteAI}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium flex items-center justify-center space-x-2 w-full"
              >
                <GamepadIcon className="w-5 h-5" />
                <span>Play Against AI</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <ParticipantCard participant={localParticipant} />
              {Array.from(participants.values()).map(
                (participant) =>
                  !participant.local && (
                    <ParticipantCard
                      key={participant.id}
                      participant={participant}
                      width="300px"
                    />
                  )
              )}
            </div>

            <div className="flex items-center justify-center">
              <TicTacToe
                gameState={gameState}
                onMove={(position) => {
                  if (gameState.currentPlayer === "X") {
                    publish(
                      JSON.stringify({
                        type: "move", // Add type field
                        position,
                        player: "X",
                      }),
                      {
                        persist: true,
                      }
                    );
                    handleMove(position, "X");
                  }
                }}
                onRestart={handleGameReset} // Update this prop
                isPlayerTurn={gameState.currentPlayer === "X"}
              />
            </div>
          </div>
        )}
      </div>

      <MeetingControls setMeetingId={setMeetingId} />
      <Toaster position="top-center" />
    </div>
  );
};

function App() {
  const [meetingId, setMeetingId] = React.useState<string | null>(null);
  const [playerName, setPlayerName] = React.useState("");

  const createMeeting = async () => {
    try {
      const response = await axios.post(
        "https://api.videosdk.live/v2/rooms",
        {},
        {
          headers: {
            Authorization: VIDEOSDK_TOKEN,
          },
        }
      );
      setMeetingId(response.data.roomId);
    } catch (error) {
      toast.error("Failed to create game room");
    }
  };

  if (!meetingId) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div
          className="fixed inset-0 bg-cover bg-center bg-no-repeat opacity-20"
          style={{
            backgroundImage:
              "url('https://images.unsplash.com/photo-1558591710-4b4a1ae0f04d?q=80&w=1920')",
          }}
        />
        <div className="relative z-10 flex flex-col items-center text-center">
          <h1 className="text-4xl font-bold text-white mb-6">
            Tic Tac Toe AI Challenge
          </h1>
          <p className="text-gray-300 mb-8 max-w-md">
            Challenge our AI in an exciting game of Tic Tac Toe! Test your
            strategic skills against an intelligent opponent.
          </p>
          <div className="bg-gray-800/90 p-8 rounded-lg shadow-xl max-w-md w-full mb-6">
            <label
              htmlFor="playerName"
              className="block text-white text-sm font-medium mb-2"
            >
              Enter Your Name
            </label>
            <input
              type="text"
              id="playerName"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value.trim())}
              placeholder="Your name"
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={createMeeting}
            disabled={!playerName}
            className="px-8 py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg text-white font-medium text-lg flex items-center space-x-2 transition-colors duration-200"
          >
            <GamepadIcon className="w-6 h-6" />
            <span>Start Game</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <MeetingProvider
      config={{
        meetingId,
        micEnabled: true,
        webcamEnabled: true,
        name: playerName,
        debugMode: true,
      }}
      token={VIDEOSDK_TOKEN}
      joinWithoutUserInteraction
    >
      <MeetingView
        meetingId={meetingId}
        setMeetingId={setMeetingId}
        playerName={playerName}
      />
    </MeetingProvider>
  );
}

export default App;
