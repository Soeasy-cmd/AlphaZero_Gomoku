import pickle
from flask import Flask, render_template, jsonify, request
from game import Board, Game
from mcts_alphaZero import MCTSPlayer
import os
import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F

app = Flask(__name__)

# --- PyTorch Model Definition (Inline to avoid file dependency issues) ---
class Net(nn.Module):
    def __init__(self, board_width, board_height):
        super(Net, self).__init__()
        self.board_width = board_width
        self.board_height = board_height
        # common layers
        self.conv1 = nn.Conv2d(4, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        # action policy layers
        self.act_conv1 = nn.Conv2d(128, 4, kernel_size=1)
        self.act_fc1 = nn.Linear(4*board_width*board_height,
                                 board_width*board_height)
        # state value layers
        self.val_conv1 = nn.Conv2d(128, 2, kernel_size=1)
        self.val_fc1 = nn.Linear(2*board_width*board_height, 64)
        self.val_fc2 = nn.Linear(64, 1)

    def forward(self, state_input):
        # common layers
        x = F.relu(self.conv1(state_input))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        # action policy layers
        x_act = F.relu(self.act_conv1(x))
        x_act = x_act.view(-1, 4*self.board_width*self.board_height)
        x_act = F.log_softmax(self.act_fc1(x_act), dim=1)
        # state value layers
        x_val = F.relu(self.val_conv1(x))
        x_val = x_val.view(-1, 2*self.board_width*self.board_height)
        x_val = F.relu(self.val_fc1(x_val))
        x_val = torch.tanh(self.val_fc2(x_val))
        return x_act, x_val

class PolicyValueNetPytorch:
    def __init__(self, board_width, board_height, net_params):
        self.device = torch.device("cpu")
        self.policy_value_net = Net(board_width, board_height).to(self.device)
        self.load_params_from_numpy(net_params)
        self.policy_value_net.eval()

    def load_params_from_numpy(self, params):
        # Theano params order in the pickle file based on policy_value_net_numpy.py investigation
        # [conv1_w, conv1_b, conv2_w, conv2_b, conv3_w, conv3_b, 
        #  act_conv1_w, act_conv1_b, act_fc1_w, act_fc1_b,
        #  val_conv1_w, val_conv1_b, val_fc1_w, val_fc1_b, val_fc2_w, val_fc2_b]
        
        # Helper to convert numpy array to torch parameter
        def to_param(arr):
             return torch.nn.Parameter(torch.from_numpy(arr).float())

        state_dict = self.policy_value_net.state_dict()
        
        # 0, 1: conv1
        # Theano weights are flipped for convolution. PyTorch does correlation.
        # So we need to flip the weights to match Theano's behavior.
        state_dict['conv1.weight'] = torch.from_numpy(params[0][:, :, ::-1, ::-1].copy()).float()
        state_dict['conv1.bias'] = torch.from_numpy(params[1]).float()
        
        # 2, 3: conv2
        state_dict['conv2.weight'] = torch.from_numpy(params[2][:, :, ::-1, ::-1].copy()).float()
        state_dict['conv2.bias'] = torch.from_numpy(params[3]).float()
        
        # 4, 5: conv3
        state_dict['conv3.weight'] = torch.from_numpy(params[4][:, :, ::-1, ::-1].copy()).float()
        state_dict['conv3.bias'] = torch.from_numpy(params[5]).float()
        
        # 6, 7: act_conv1
        state_dict['act_conv1.weight'] = torch.from_numpy(params[6][:, :, ::-1, ::-1].copy()).float()
        state_dict['act_conv1.bias'] = torch.from_numpy(params[7]).float()
        
        # 8, 9: act_fc1
        # Numpy: dot(x, W) -> W shape (in, out). PyTorch: linear(x, W) -> W shape (out, in).
        # So we need transpose.
        state_dict['act_fc1.weight'] = torch.from_numpy(params[8].T).float()
        state_dict['act_fc1.bias'] = torch.from_numpy(params[9]).float()
        
        # 10, 11: val_conv1
        state_dict['val_conv1.weight'] = torch.from_numpy(params[10][:, :, ::-1, ::-1].copy()).float()
        state_dict['val_conv1.bias'] = torch.from_numpy(params[11]).float()
        
        # 12, 13: val_fc1
        state_dict['val_fc1.weight'] = torch.from_numpy(params[12].T).float()
        state_dict['val_fc1.bias'] = torch.from_numpy(params[13]).float()
        
        # 14, 15: val_fc2
        state_dict['val_fc2.weight'] = torch.from_numpy(params[14].T).float()
        state_dict['val_fc2.bias'] = torch.from_numpy(params[15]).float()

        self.policy_value_net.load_state_dict(state_dict)

    def policy_value_fn(self, board):
        legal_positions = board.availables
        current_state = np.ascontiguousarray(board.current_state().reshape(
                -1, 4, self.policy_value_net.board_width, self.policy_value_net.board_height))
        
        with torch.no_grad():
            log_act_probs, value = self.policy_value_net(
                    torch.from_numpy(current_state).float().to(self.device))
            act_probs = np.exp(log_act_probs.cpu().numpy().flatten())
            value = value.item()
            
        act_probs = zip(legal_positions, act_probs[legal_positions])
        return act_probs, value

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

            # Use PyTorch implementation for speed
            # best_policy = PolicyValueNetNumpy(self.width, self.height, policy_param)
            best_policy = PolicyValueNetPytorch(self.width, self.height, policy_param)
            
            # Reduce n_playout for faster web response.
            # PyTorch CPU is faster, so we can afford slightly more playouts than pure Numpy
            # Railway has better CPU than Render free tier usually.
            self.mcts_player = MCTSPlayer(best_policy.policy_value_fn, c_puct=5, n_playout=400)
            print("Model loaded successfully (PyTorch Backend).")
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
