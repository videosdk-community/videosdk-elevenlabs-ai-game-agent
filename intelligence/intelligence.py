from openai import OpenAI
import dotenv

dotenv.load_dotenv()
    
class OpenAiIntelligence:
    def __init__(self):
        self.game_moves = []
        self.openai_client = OpenAI()
        
    def generate_server_response(self, game_state):
        # Get current game state from server
        board = game_state["board"]  # Connect to server's game state
        
        available_positions = [str(i) for i, val in enumerate(board) if val is None]
        
        if not available_positions:
            return {"type": "game_over", "winner": None}
        
        ai_move = {
            "type": "move",
            "position": self._get_ai_move(board, available_positions),
            "player": "O"
        }
        
        # generate ai comments
        # elevenLabs : voice response
        return ai_move
    
    def _get_ai_move(self, board, available_positions):
        x_positions = [i for i, pos in enumerate(board) if pos == "X"]
        
        prompt = f"""
        Current tic-tac-toe board (0-8 positions):
        {board[0]}|{board[1]}|{board[2]}
        {board[3]}|{board[4]}|{board[5]}
        {board[6]}|{board[7]}|{board[8]}

        Player X has moved to positions: {x_positions}
        Available positions: {available_positions}
        
        You are player 'O'. Analyze X's moves and:
        1. Block X from winning if they have 2 in a line
        2. Create your own winning line if possible
        3. Take strategic positions (center, corners) if no immediate threats
        
        Return only a single number from {available_positions}.
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        ai_position = response.choices[0].message.content.strip()
        # Validate AI's choice
        if ai_position not in available_positions:
            # If invalid, choose first available position
            ai_position = available_positions[0]
            
        return ai_position 