import pickle
from flask import Flask, render_template, jsonify, request
from game import Board, Game
from mcts_alphaZero import MCTSPlayer
from policy_value_net_numpy import PolicyValueNetNumpy
import os

app = Flask(__name__)

# Load Model
class AIModel:
    def __init__(self):
        self.width = 8
        self.height = 8
        self.n_in_row = 5
        self.model_file = 'best_policy_8_8_5.model'
        self.mcts_player = None
        self.load_model()

    def load_model(self):
        try:
            # Check if model exists
            if not os.path.exists(self.model_file):
                print(f"Model file {self.model_file} not found!")
                return

            try:
                policy_param = pickle.load(open(self.model_file, 'rb'))
            except:
                policy_param = pickle.load(open(self.model_file, 'rb'), encoding='bytes')

            best_policy = PolicyValueNetNumpy(self.width, self.height, policy_param)
            # Reduce n_playout for faster web response.
            # Pure Numpy implementation is slow on CPU. 
            # 400 is too high for free tier (timeout). 64 is a compromise.
            self.mcts_player = MCTSPlayer(best_policy.policy_value_fn, c_puct=5, n_playout=64)
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            import traceback
            traceback.print_exc()

ai = AIModel()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/move', methods=['POST'])
def get_move():
    try:
        data = request.json
        moves = data.get('moves', []) # List of previous moves including the player's last move
        
        # Reconstruct board state
        board = Board(width=ai.width, height=ai.height, n_in_row=ai.n_in_row)
        board.init_board(start_player=0)
        
        # Replay all moves
        for move in moves:
            if move in board.availables:
                board.do_move(move)
            else:
                return jsonify({'error': f'Invalid move sequence: {move}'}), 400

        # Check if game over after player's move
        end, winner = board.has_a_winner()
        if end:
             return jsonify({
                'move': -1,
                'game_over': True,
                'winner': winner
            })

        # AI thinks
        if ai.mcts_player is None:
             return jsonify({'error': 'AI model not not loaded'}), 500

        ai_move = ai.mcts_player.get_action(board)
        
        # Apply AI move simply to check for win
        board.do_move(ai_move)
        end, winner = board.has_a_winner()

        return jsonify({
            'move': int(ai_move),
            'game_over': end,
            'winner': winner
        })

    except Exception as e:
        print(f"CRITICAL ERROR in get_move: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
