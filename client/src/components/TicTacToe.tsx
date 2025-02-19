import React from "react";
import clsx from "clsx";
import { X, Circle, RotateCcw } from "lucide-react";
import type { GameState } from "../types";

interface TicTacToeProps {
  gameState: GameState;
  onMove: (position: number) => void;
  onRestart: () => void;
  isPlayerTurn: boolean;
}

export const TicTacToe: React.FC<TicTacToeProps> = ({
  gameState,
  onMove,
  onRestart,
  isPlayerTurn,
}) => {
  const renderCell = (position: number) => {
    const value = gameState.board[position];
    const isWinningCell = false;

    return (
      <button
        key={position}
        onClick={() => isPlayerTurn && !value && onMove(position)}
        disabled={!isPlayerTurn || !!value || gameState.isGameOver}
        className={clsx(
          "w-full h-full flex items-center justify-center",
          "border border-gray-600 bg-gray-800/50",
          "transition-colors duration-200",
          {
            "hover:bg-gray-700/50":
              isPlayerTurn && !value && !gameState.isGameOver,
            "bg-green-900/20": isWinningCell,
          }
        )}
      >
        {value === "X" && <X className="w-8 h-8 text-blue-400" />}
        {value === "O" && <Circle className="w-8 h-8 text-red-400" />}
      </button>
    );
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="aspect-square grid grid-cols-3 gap-2 bg-gray-900/50 p-2 rounded-lg">
        {Array.from({ length: 9 }).map((_, i) => renderCell(i))}
      </div>

      <div className="mt-4 text-center text-white">
        {gameState.isGameOver ? (
          <div className="space-y-4">
            <p className="text-xl font-bold">
              {gameState.winner ? `${gameState.winner} Wins!` : "It's a Draw!"}
            </p>
            {gameState.isGameOver && (
              <button
                onClick={onRestart}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium flex items-center justify-center space-x-2 mx-auto"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Play Again</span>
              </button>
            )}
          </div>
        ) : (
          <p className="text-lg">{isPlayerTurn ? "Your Turn" : "AI's Turn"}</p>
        )}
      </div>
    </div>
  );
};
