export interface Participant {
  id: string;
  displayName: string;
  isLocal: boolean;
  webcamOn: boolean;
  micOn: boolean;
  isActiveSpeaker: boolean;
  videoStream?: MediaStream;
  audioStream?: MediaStream;
}

export type GameState = {
  board: Array<string | null>;
  currentPlayer: 'X' | 'O';
  winner: string | null;
  isGameOver: boolean;
};

export type GameMove = {
  position: number;
  player: 'X' | 'O';
};