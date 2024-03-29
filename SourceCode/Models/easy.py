# -*- coding: utf-8 -*-
"""Q_learning.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ygF6VBbomuceveK2KT-r3vh8t64kN-SX
"""

#----- 15/08/2023 -----
import tkinter as tk
from tkinter import ttk
#----- 15/08/2023 -----
import numpy as np
import pickle
import os
import copy
from collections import defaultdict
#----- 15/08/2023 -----
import time
#----- 15/08/2023 -----
from itertools import chain

class State:
    def __init__(self, p1, p2):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.p1 = p1
        self.p2 = p2
        self.isEnd = False
        self.boardHash = None
        # init p1 plays first
        self.playerSymbol = 1

    def getHash(self):
        self.boardHash = str(self.board.reshape(BOARD_COLS * BOARD_ROWS))
        return self.boardHash

    def winner(self):
        # row
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS - NUMBERTOWIN + 1):
                win_board = sum(self.board[i, j:j + NUMBERTOWIN])
                if win_board == NUMBERTOWIN:
                    self.isEnd = True
                    return 1
                if win_board == -NUMBERTOWIN:
                    self.isEnd = True
                    return -1

        # col
        for i in range(BOARD_COLS):
            for j in range(BOARD_ROWS - NUMBERTOWIN + 1):
                win_board = sum(self.board[j:j + NUMBERTOWIN, i])
                if win_board == NUMBERTOWIN:
                    self.isEnd = True
                    return 1
                if win_board == -NUMBERTOWIN:
                    self.isEnd = True
                    return -1

        # # diagonal
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if r + NUMBERTOWIN - 1 < BOARD_ROWS and c + NUMBERTOWIN - 1 < BOARD_COLS:
                    ldiagRight = []
                    for i in range(NUMBERTOWIN):
                        ldiagRight.append((r + i, c + i))
                    # print(ldiagRight)
                    # Xét điểm
                    diag_sum1 = sum([self.board[dr[0]][dr[1]] for dr in ldiagRight])
                    if diag_sum1 == NUMBERTOWIN:
                        self.isEnd = True
                        return 1
                    if diag_sum1 == -NUMBERTOWIN:
                        self.isEnd = True
                        return -1

        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                if r + NUMBERTOWIN - 1 < BOARD_ROWS and c - NUMBERTOWIN + 1 >= 0:
                    ldiagLeft = []
                    for i in range(NUMBERTOWIN):
                        ldiagLeft.append((r + i, c - i))
                    # print(ldiagLeft)
                    # Xét điểm
                    diag_sum2 = sum([self.board[dl[0]][dl[1]] for dl in ldiagLeft])
                    if diag_sum2 == NUMBERTOWIN:
                        self.isEnd = True
                        return 1
                    if diag_sum2 == -NUMBERTOWIN:
                        self.isEnd = True
                        return -1

        # tie
        # no available positions
        if len(self.availablePositions()) == 0:
            self.isEnd = True
            return 0
        # not end
        self.isEnd = False
        return None


    def availablePositions(self):
        positions = []
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if self.board[i, j] == 0:
                    positions.append((i, j))  # need to be tuple
        return positions

    def updateState(self, position):
        self.board[position] = self.playerSymbol
        # switch to another player
        self.playerSymbol = -1 if self.playerSymbol == 1 else 1

    # only when game ends
    def get_reward(self):
        result = self.winner()
        if result == 1:
            return 1, -1
        elif result == -1:
            return -1, 1
        else:
            return 0, 0

    # board reset
    def reset(self):
        self.board = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.boardHash = None
        self.isEnd = False
        self.playerSymbol = 1

    def play(self, rounds=100):
         # -----15/08/2023-----
        popup = tk.Toplevel()
        tk.Label(popup, text="Model Being Trained", font=("Arial", 16)).grid(row=0,column=0)
        percent_label = tk.Label(popup, text="0%", font=("Arial", 16))
        percent_label.grid(row=1, column=0)

        progress = 0
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(popup, variable=progress_var, maximum=100, length = 500)
            
        progress_bar.grid(row=2, column=0)
        popup.pack_slaves()
        progress_step = float(100.0/rounds)
        popup.grab_set()
        for i in range(rounds):
            popup.update()
            progress += progress_step
            percent_label.config(text=str(int(progress)) + "%")
            progress_var.set(progress)
        # -----15/08/2023-----
            prev_state = self.getHash()
            prev_state_p2 = ""
            new_state_p2 = ""
            positions = self.availablePositions()
            prev_action = self.p1.chooseAction(positions, self.board)
            while not self.isEnd:
                # Player 1
                # take action and update board state
                self.updateState(prev_action)
                board_hash = self.getHash()
                if prev_state_p2 == "":
                    prev_state_p2 = board_hash
                else:
                    new_state_p2 = board_hash
                reward_1 = self.get_reward()[0]
                # check board status if it is ended
                win = self.winner()
                if win is not None:
                    # ended with p1 either win or draw
                    reward_2 = self.get_reward()[1]
                    self.reset()
                    break

                else:
                    # Player 2
                    positions = self.availablePositions()
                    if(prev_state_p2 != "" and new_state_p2 == ""):
                        prev_action_p2 = self.p2.chooseAction(positions, self.board)
                        self.updateState(prev_action_p2)
                        reward_2 = self.get_reward()[1]

                    if(prev_state_p2 != "" and new_state_p2 != ""):
                        new_action_p2 = self.p2.chooseAction(positions, self.board)
                        self.p2.update(prev_state_p2, new_state_p2, prev_action_p2, new_action_p2, reward_2, self.availablePositions())
                        prev_state_p2 = new_state_p2
                        prev_action_p2 = new_action_p2
                        self.updateState(prev_action_p2)
                        reward_2 = self.get_reward()[1]
                    win = self.winner()
                    if win is not None:
                        # ended with p2 either win or draw
                        reward_1 = self.get_reward()[0]
                        self.reset()
                        break
                new_state = self.getHash()
                new_action = self.p1.chooseAction(self.availablePositions(), self.board)
                self.p1.update(prev_state, new_state, prev_action, new_action, reward_1, self.availablePositions())
                prev_state = new_state
                prev_action = new_action
            self.p1.update(prev_state, None, prev_action, None, reward_1, self.availablePositions())
            self.p2.update(prev_state_p2, None, prev_action_p2, None, reward_2, self.availablePositions())
        # -----15/08/2023-----
        time.sleep(0.5)
        popup.grab_release()
        popup.destroy()
        # -----15/08/2023-----

class Player:
    def __init__(self, name, exp_rate=0.01):
        self.name = name
        self.alpha = 0.2
        self.exp_rate = exp_rate
        self.gamma = 0.9
        self.states_value = {}  
        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                p = (i, j)
                if self.states_value.get(p) is None:
                    self.states_value[p] = defaultdict(int)

    @staticmethod
    def getHash(board):
        boardHash = str(board.reshape(BOARD_COLS * BOARD_ROWS))
        return boardHash

    # e-greedy
    def chooseAction(self, positions, current_board):
        global action
        randValue = np.random.random()
        if randValue > self.exp_rate:
            board = current_board.copy()
            curr_board = self.getHash(board)
            values = np.array([self.states_value[p][curr_board] for p in positions])
            ix_max = np.where(values == np.max(values))[0]
            if len(ix_max) > 1:
                ix_select = np.random.choice(ix_max, 1)[0]
            else:
                ix_select = ix_max[0]
            action = positions[ix_select]    
        else:
            # take random action
            idx = np.random.choice(len(positions))
            action = positions[idx]

        return action

    def update(self, s, s_, a, a_, r, positions):
        if s_ is not None:
            Q_options = [self.states_value[p][s_] for p in positions]
            # update
            self.states_value[a][s] += self.alpha*(r + self.gamma*max(Q_options) - self.states_value[a][s])
        else:
            # terminal state update
            self.states_value[a][s] += self.alpha*(r - self.states_value[a][s])


def Tic_Tac_Toe(n, m, x):
    if x > m and x > n:
        print()
        print("Invalid x !!! Please Enter Again !!!")
        print()
        return

    global BOARD_ROWS
    global BOARD_COLS
    global NUMBERTOWIN

    BOARD_ROWS = n
    BOARD_COLS = m
    NUMBERTOWIN = x

    p1 = Player("p1")
    p2 = Player("p2")
    st = State(p1, p2)
    print("training...")
    st.play(10000)
    po1 = p1.states_value
    po2 = p2.states_value
    p = {}
    for k, v in chain(po1.items(), po2.items()):
        if p.get(k) is None:
            p[k] = defaultdict(int)
        for kv, vv in v.items():
            p[k][kv] = vv
    fw = open('Policies/policy_' + str(n) + '_' + str(m) + '_' + str(x) + '_easy', 'wb')
    pickle.dump(p, fw)
    fw.close()


