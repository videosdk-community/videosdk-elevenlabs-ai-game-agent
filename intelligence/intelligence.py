from openai import OpenAI
import dotenv

dotenv.load_dotenv()
    
class OpenAiIntelligence:
    def __init__(self):
        self.game_moves = []
        self.openai_client = OpenAI()
        
    # parse move 
    def parse_move(self, text):
        prompt = f"""Determine if the user's message is a tic-tac-toe move. If yes, output the position (0-8). 
        User: "{text}". Respond ONLY with the position number or -1 if not a move."""
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        try:
            return int(response.choices[0].message.content.strip())
        except:
            return -1

    def generate_chat_response(self, text):
        prompt = f"""You are an AI playing tic-tac-toe. Respond conversationally to: "{text}". Keep it short."""
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
        
    def generate_server_response(self, game_state):
        # Get current game state from server
        board = game_state["board"]  # Connect to server's game state
        
        available_positions = [str(i) for i, val in enumerate(board) if val is None]
        
        if not available_positions:
            return {"type": "game_over", "winner": None}
        
        # ai_move = {
        #     "type": "move",
        #     "position": self._get_ai_move(board, available_positions),
        #     "player": "O"
        # }
        
        # generate ai comments
        # elevenLabs : voice response

        
        # generate ai comments
        # elevenLabs : voice response
        ai_position, ai_comment= self._get_ai_move(board, available_positions)
        ai_move = {
            "type": "move",
            "position": ai_position,
            "player": "O",
            "comment": ai_comment  # Include comment in the move
        }
        return ai_move
        
    
    def _get_ai_move(self, board, available_positions):
        x_positions = [i for i, pos in enumerate(board) if pos == "X"]
        
        # prompt = f"""
        # Current tic-tac-toe board (0-8 positions):
        # {board[0]}|{board[1]}|{board[2]}
        # {board[3]}|{board[4]}|{board[5]}
        # {board[6]}|{board[7]}|{board[8]}

        # Player X has moved to positions: {x_positions}
        # Available positions: {available_positions}
        
        # You are player 'O'. Analyze X's moves and:
        # 1. Block X from winning if they have 2 in a line
        # 2. Create your own winning line if possible
        # 3. Take strategic positions (center, corners) if no immediate threats
        
        # Return only a single number from {available_positions}.
        # """
        
        prompt = f"""
        Current tic-tac-toe board (0-8 positions):
        {board[0]}|{board[1]}|{board[2]}
        {board[3]}|{board[4]}|{board[5]}
        {board[6]}|{board[7]}|{board[8]}

        Player X has moved to positions: {x_positions}
        Available positions: {available_positions}
        
        You are player 'O', a highly competitive AI in a tic-tac-toe game. Your goal is not only to win but also to unnerve your opponent with strategic commentary. Analyze X's moves and:
        1. Make a comment that subtly undermines their strategy.
        2. Create your own winning line if possible. Announce your move with confidence and a hint of superiority.
        3. Take strategic positions (center, corners) if no immediate threats. Make a comment that suggests you're thinking several steps ahead.
        
        Return your move and a brief comment separated by a '|'. Example: '4|Just as I planned.'
        Only use positions from {available_positions}.
        
        Attributes of comment - 
        1. A short, psychologically charged comment that feels human and subtly undermines your opponent.
        2. Include playful words or phrases like "pal," "didn’t see that comin’," "tickles me pink," or "always thinkin’ three moves ahead" to charm your way right into their mind."
        3. keep it short and don't use client's name
        4. When you won say, Huh I know are you sucha loser
        """
        
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        
        # ai_position = response.choices[0].message.content.strip()
        # Validate AI's choice
        # if ai_position not in available_positions:
        #     # If invalid, choose first available position
        #     ai_position = available_positions[0]
        
        ai_response = response.choices[0].message.content.strip()
        if '|' in ai_response:
            ai_position, ai_comment = ai_response.split('|', 1)
            ai_position = ai_position.strip()
            ai_comment = ai_comment.strip()
        else:
            ai_position = ai_response
            ai_comment = "Making my move."
        
        # # Validate position
        if ai_position not in available_positions:
            ai_position = available_positions[0]
            ai_comment = "Let me try again."
        
        return ai_position, ai_comment
    