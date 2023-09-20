import tkinter as tk
from tkinter import StringVar, messagebox

import numpy as np
import copy
import pickle as pickle    
from collections import defaultdict
import os

class Game:
    def __init__(self, master, player1, player2, Q={}, row=9, col=9, x_win=5, level=-1):

        global label
        global pause_var
        global stop_var
        global reset_var
        global res
        

        pause_var = StringVar()
        stop_var = StringVar()
        reset_var = StringVar()
        res = ""
        
        
        #-----15/08/2023-----
        # get width of screen game
        master.update()
        width_of_master = master.winfo_width()
        
        # get middle of screen by width
        m_width = width_of_master/2
        #-----15/08/2023-----

        self.master = master
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.other_player = player2
        self.empty_text = ""
        self.row = row
        self.col = col
        self.x_win = x_win

        self.board = Board(row, col, x_win)

        #-----14/08/2023-----
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        #-----14/08/2023-----

        #----- 15/08/2023-----
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        # Add scrollbar x and y to frame
        def onFrameConfigure(canvas):
            # Reset the scroll region to encompass the inner frame
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas = tk.Canvas(self.master, borderwidth=0)
        frame = tk.Frame(canvas)
        # Horizontal and vertical scrollbars
        hsb = tk.Scrollbar(self.master, orient="horizontal", command=canvas.xview)
        vsb = tk.Scrollbar(self.master, orient="vertical", command=canvas.yview)
        canvas.configure(xscrollcommand=hsb.set)
        canvas.configure(yscrollcommand=vsb.set)

        hsb.grid(column=0, row=1, sticky='new')
        vsb.grid(column=0, row=0, sticky='nse')
        canvas.grid(column=0, row=0, sticky='nsew')
        canvas.create_window((m_width,0), window=frame, anchor="center")

        frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))
        
        frame1 = tk.Frame(frame)
        frame2 = tk.Frame(frame)
        frame3 = tk.Frame(frame)

        frame1.grid(row=0, column=0)
        frame2.grid(row=1, column=0)
        frame3.grid(row=2, column=0)

        #----- 15/08/2023 -----
       
        check_identity = type(self.player1).__name__
        if check_identity == "QPlayer":
            label = tk.Label(frame1, text= self.current_player.mark + "'s Turn")
        elif check_identity == "HumanPlayer":
            label = tk.Label(frame1, text= "Your Turn")
        else:
            label = tk.Label(frame1, text= self.current_player.mark + "'s Turn")
        
        label.config(pady=10, font=("Arial", 20))
        label.grid(row=0, column=0)

        self.buttons = [[0 for _ in range(row)] for _ in range(col)]
        for i in range(row):
            for j in range(col):
                self.buttons[i][j] = tk.Button(frame2, height=3, width=5, text=self.empty_text, font=("Arial", 10), command=lambda i=i, j=j: self.callback(self.buttons[i][j]))
                self.buttons[i][j].grid(row=i, column=j)

        #----- 15/08/2023 -----
        if (isinstance(self.player1, QPlayer) and isinstance(self.player2, QPlayer)):
            if self.row <= 7 and self.col <= 7:
                self.next_button = tk.Button(frame3,text="Next Move", command=self.click_next, font=("Arial", 15), bg="green", fg="white")
                self.next_button.grid(row=row, pady=15)

                self.reset_button = tk.Button(frame3,text="Reset", command=self.reset, font=("Arial", 15))
                self.reset_button.grid(row=row+1)
            
                self.backtomenu_button = tk.Button(frame3,text="Back To Menu", command=self.back_to_menu, font=("Arial", 15), bg="black", fg="white")
                self.backtomenu_button.grid(row=row+2, pady=15)
            else:
                self.next_button = tk.Button(frame3,text="Next Move", command=self.click_next, font=("Arial", 15), bg="green", fg="white")
                self.next_button.grid(row=row, column = 0, pady=15, padx=5)

                self.reset_button = tk.Button(frame3,text="Reset", command=self.reset, font=("Arial", 15))
                self.reset_button.grid(row=row, column = 1, pady=15, padx=5)
            
                self.backtomenu_button = tk.Button(frame3,text="Back To Menu", command=self.back_to_menu, font=("Arial", 15), bg="black", fg="white")
                self.backtomenu_button.grid(row=row, column = 2, pady=15, padx=5)
        else:
            if self.row <= 7 and self.col <= 7:
                self.reset_button = tk.Button(frame3,text="Reset", command=self.reset, font=("Arial", 15))
                self.reset_button.grid(row=row, pady=15)
                
                self.backtomenu_button = tk.Button(frame3,text="Back To Menu", command=self.back_to_menu, font=("Arial", 15), bg="black", fg="white")
                self.backtomenu_button.grid(row=row+1)
            else:
                self.reset_button = tk.Button(frame3,text="Reset", command=self.reset, font=("Arial", 15))
                self.reset_button.grid(row=row, column = 0, pady=15, padx=5)
                
                self.backtomenu_button = tk.Button(frame3,text="Back To Menu", command=self.back_to_menu, font=("Arial", 15), bg="black", fg="white")
                self.backtomenu_button.grid(row=row, column = 1, pady=15, padx=5)
        #----- 15/08/2023 -----
       
        self.Q = Q
        self.alpha = 0.2
        self.gamma = 0.9
        self.mode = level
        
        self.share_Q_with_players()
        self.prev_sa_human = []
        #Player vs bot: s, s_, a, r
        self.save_s = ["", "", 0, 0]

    def share_Q_with_players(self): 
        if self.mode == 2 or self.mode == 3:
            if isinstance(self.player1, QPlayer) and isinstance(self.player2, QPlayer):  
                copy_Q = copy.deepcopy(self.Q)
                self.player1.Q = copy_Q    
                self.player2.Q = copy_Q     
            else:  
                if isinstance(self.player1, QPlayer):
                    self.player1.Q = copy.deepcopy(self.Q)
                if isinstance(self.player2, QPlayer):
                    self.player2.Q = copy.deepcopy(self.Q)
        else:
            if isinstance(self.player1, QPlayer):
                self.player1.Q = self.Q
            if isinstance(self.player2, QPlayer):
                self.player2.Q = self.Q
    def callback(self, button):
        if self.board.over():
            pass                
        else:
            if isinstance(self.current_player, HumanPlayer) and isinstance(self.other_player, HumanPlayer):
                if self.empty(button):
                    move = self.get_move(button)
                    self.handle_move(move)
            elif isinstance(self.current_player, HumanPlayer) and isinstance(self.other_player, ComputerPlayer):
                global res
                if isinstance(self.player1, ComputerPlayer):
                    prev_state = self.prev_sa_human[0]
                    prev_action = self.prev_sa_human[1]
                    reward = self.board.get_reward(prev_action)[0]
                    if self.empty(button):
                        human_move = self.get_move(button)
                        self.handle_move(human_move)
                        if not self.board.over():   
                            new_state = copy.deepcopy(self.board)           
                            self.new_action = self.player1.get_move(self.board)
                            self.update_Q(prev_state, new_state, prev_action, self.new_action, reward, self.board.available_moves())
                            self.prev_sa_human[0] = new_state
                            self.prev_sa_human[1] = self.new_action
                            self.handle_move(self.new_action)
                    if self.board.over():
                        reward = self.board.get_reward(human_move)[0]
                        self.update_Q(prev_state, None, prev_action, None, reward, None)

                        
                        res = messagebox.askquestion("Save Policy", "Do you want to save this policy?")
                        if res == 'yes':
                            if self.mode == 2:
                                fw = open('Policies/policy_' + str(self.row) + '_' + str(self.col) + '_' + str(self.x_win) + '_sa', 'wb')
                                pickle.dump(self.Q, fw)
                                fw.close()
                            elif self.mode == 3:
                                fw = open('Policies/policy_' + str(self.row) + '_' + str(self.col) + '_' + str(self.x_win) + '_ql', 'wb')
                                pickle.dump(self.Q, fw)
                                fw.close()
                            messagebox.showinfo("Save Policy", "Policy has been saved!")
                else:
                    if self.empty(button):
                        human_move = self.get_move(button)
                        self.handle_move(human_move)
                        if not self.board.over(): 
                            if self.save_s[0] == "":
                                self.save_s[0] = copy.deepcopy(self.board)
                            else:
                                self.save_s[1] = copy.deepcopy(self.board)
                            # check_first = len(self.prev_sa_human)
                            # if check_first == 0:
                            #     prev_state = copy.deepcopy(self.board)             
                            #     prev_action = self.player2.get_move(self.board)
                            #     self.prev_sa_human.append(prev_state)
                            #     self.prev_sa_human.append(prev_action)
                            # else:
                            #     prev_state = self.prev_sa_human[0]
                            #     prev_action = self.prev_sa_human[1]
                            # self.handle_move(prev_action)
                            # reward = self.board.get_reward(prev_action)[1]
                            # new_state = copy.deepcopy(self.board)           
                            # new_action = self.player2.get_move(self.board)
                            if(self.save_s[0] != "" and self.save_s[1] == ""):
                                prev_action = self.player2.get_move(self.board)
                                self.save_s[2] = prev_action
                                # take action and update board state
                                self.handle_move(prev_action)
                                self.save_s[3] = self.board.get_reward(prev_action)[1]

                            if(self.save_s[0] != "" and self.save_s[1] != ""):
                                new_action = self.player2.get_move(self.board)
                                # print("Preve S: ", self.save_s[0].grid)
                                # print("Prev A: ", self.save_s[2])
                                # print("New S: ", self.save_s[1].grid)
                                # print("New A: ", new_action)
                                # print("Reward: ", self.save_s[3])
                                self.update_Q(self.save_s[0], self.save_s[1], self.save_s[2], new_action, self.save_s[3], self.board.available_moves())
                                self.save_s[0] = self.save_s[1]
                                self.save_s[2] = new_action
                                self.handle_move(self.save_s[2])
                                self.save_s[3] = self.board.get_reward(self.save_s[2])[1]
                            
                            # self.update_Q(prev_state, new_state, prev_action, new_action, reward, self.board.available_moves())
                            # self.prev_sa_human[0] = new_state
                            # self.prev_sa_human[1] = new_action
                    if self.board.over():
                        # print("Preve S: ", self.save_s[0].grid)
                        # print("Prev A: ", self.save_s[2])
                        reward = self.board.get_reward((0,0))[1]
                        self.update_Q(self.save_s[0], None, self.save_s[2], None, reward, None)

                        res = messagebox.askquestion("Save Policy", "Do you want to save this policy?")
                        if res == 'yes':
                            if self.mode == 2:
                                fw = open('Policies/policy_' + str(self.row) + '_' + str(self.col) + '_' + str(self.x_win) + '_sa', 'wb')
                                pickle.dump(self.Q, fw)
                                fw.close()
                            elif self.mode == 3:
                                fw = open('Policies/policy_' + str(self.row) + '_' + str(self.col) + '_' + str(self.x_win) + '_ql', 'wb')
                                pickle.dump(self.Q, fw)
                                fw.close()
                            messagebox.showinfo("Save Policy", "Policy has been saved!")


    def empty(self, button):
        return button["text"] == self.empty_text

    def get_move(self, button):
        info = button.grid_info()
        move = (int(info["row"]), int(info["column"]))                
        return move

    def handle_move(self, move):
        i, j = move                                                     
        self.buttons[i][j].configure(text=self.current_player.mark)     
        self.board.place_mark(move, self.current_player.mark)          
        if self.board.over():
            self.declare_outcome()
        else:
            self.switch_players()
            
    #----- NEW ------
    def declare_outcome(self):
        if self.board.winner() is None:
            label.config(text="Cat's game.")
        elif self.board.winner() == 0:
            label.config(text="Tie!")
        else:
            if type(self.player1).__name__ == "QPlayer" and type(self.player2).__name__ == "QPlayer":
                if self.current_player == self.player1:
                    label.config(text=("Bot X won!"))
                else:
                    label.config(text=("Bot O won!"))
            elif type(self.current_player).__name__ == "QPlayer":
                label.config(text=("Bot won!"))
            elif type(self.current_player).__name__ == "HumanPlayer":
                label.config(text=("You won!"))
            else:
                label.config(text=("Bot won!"))
    #----------------

    def reset(self):
        
        if type(self.player1).__name__ == "QPlayer" and type(self.player2).__name__ == "QPlayer" and not self.board.over():
            
            pause_var.set("Reset")
            return
        else:
            global res
            #If the game is over, and user click reset button, and choose 'yes' in the popup save policy.
            #The program will load the new policy for the game.
            if res == 'yes':
                if self.mode == 2:
                    policy = "Policies/policy_" + str(self.row) + "_" + str(self.col) + "_" + str(self.x_win) + "_sa"
                    self.Q = pickle.load(open(policy, 'rb'))
                    self.share_Q_with_players()
                elif self.mode == 3:
                    policy = "Policies/policy_" + str(self.row) + "_" + str(self.col) + "_" + str(self.x_win) + "_ql"
                    self.Q = pickle.load(open(policy, 'rb'))
                    self.share_Q_with_players()

            label.config(text="Resetting...", font=("Arial", 20))
            for i in range(self.row):
                for j in range(self.col):
                    self.buttons[i][j].configure(text=self.empty_text)
            self.board = Board(self.row, self.col, self.x_win)
            self.current_player = self.player1
            self.other_player = self.player2

            if type(self.player1).__name__ == "QPlayer":
                label.config(text= self.current_player.mark + "'s Turn")
            elif type(self.player1).__name__ == "HumanPlayer":
                label.config(text= "Your Turn")
            
            # Set four variable to default value = ""
            pause_var.set("")
            stop_var.set("")
            reset_var.set("")
            res = ""

            self.play()    
    
    #-----15/08/2023-----
    def back_to_menu(self):
        if type(self.player1).__name__ == "QPlayer" and type(self.player2).__name__ == "QPlayer" and not self.board.over():
            pause_var.set("Back")
            return
        else:
            import main
            self.master.destroy()
            main.main_start()
   
    def click_next(self):
        pause_var.set(1)
    
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            if type(self.player1).__name__ == "QPlayer" and type(self.player2).__name__ == "QPlayer" and not self.board.over():
                pause_var.set("Quit")
                return
            else:
                self.master.destroy()
            
    def switch_players(self):
        
        if self.current_player == self.player1:
            self.current_player = self.player2
            self.other_player = self.player1
            
            check_identity = type(self.player2).__name__
            if check_identity == "QPlayer":
                label.config(text= self.current_player.mark + "'s Turn")
            elif check_identity == "HumanPlayer":
                label.config(text= "Your Turn")
            else:
                label.config(text= self.current_player.mark + "'s Turn")
            
        else:
            self.current_player = self.player1
            self.other_player = self.player2
            
            check_identity = type(self.player1).__name__
            if check_identity == "QPlayer":
                label.config(text= self.current_player.mark + "'s Turn")
            elif check_identity == "HumanPlayer":
                label.config(text= "Your Turn")
            else:
                label.config(text= self.current_player.mark + "'s Turn")
            

    def check_stop_program(self):
        # This case mean that if pause_var == "Quit" or pause_var == "Back" or pause_var == "Reset", this program will
        # set stop_var to "Q" or "B" or reset_var to "R" and return True
        # This make break the loop in function play().
        if pause_var.get() == "Quit" or pause_var.get() == "Back" or pause_var.get() == "Reset":
            # self.play_turn(self.current_player.get_move(self.board))
            # User click button "X" on window, stop_var will set to "Q" only once.
            if stop_var.get() != "Q" and pause_var.get() == "Quit":
                stop_var.set("Q")
                return True
            # User click button "Back To Menu", stop_var will set to "B" only once.
            elif stop_var.get() != "B" and pause_var.get() == "Back":
                stop_var.set("B")
                return True
            # User click button "Reset", reset_var will set to "R" only once.
            elif reset_var.get() != "R" and pause_var.get() == "Reset":
                reset_var.set("R")
                return True

    def play(self):
        if isinstance(self.player1, HumanPlayer) and isinstance(self.player2, HumanPlayer):
            pass       
        elif isinstance(self.player1, HumanPlayer) and isinstance(self.player2, ComputerPlayer):
            pass
        elif isinstance(self.player1, ComputerPlayer) and isinstance(self.player2, HumanPlayer):
            first_computer_move = self.player1.get_move(self.board) 
            self.prev_sa_human.append(copy.deepcopy(self.board)) 
            self.prev_sa_human.append(first_computer_move) 
            self.handle_move(first_computer_move)
        elif isinstance(self.player1, ComputerPlayer) and isinstance(self.player2, ComputerPlayer):
            prev_state_p2 = ""
            new_state_p2 = ""
            prev_state = copy.deepcopy(self.board)
            prev_action = self.player1.get_move(prev_state)
            while not self.board.over():
                # pause_var = 1, that mean program pause if pause_var == 1
                self.master.wait_variable(pause_var)
                # check if check_stop_program() return True
                # the loop will break
                # This check return true when user click "X" or "Back To Menu" or "Reset"
                if self.check_stop_program():
                    break
                # This process active through function "click_next"
                # The pause_var always set to 1, this make program always pause when loop after execute "play_turn".
                self.play_turn(prev_action)
                if prev_state_p2 == "":
                    prev_state_p2 = copy.deepcopy(self.board)
                else:
                    new_state_p2 = copy.deepcopy(self.board)
                reward_1 = self.board.get_reward(prev_action)[0]
                #print("Reward 1: ", reward_1)
                if self.board.over():
                    reward_2 = self.board.get_reward(prev_action)[1]
                    #print("Reward 2: ", reward_2)
                    break
                # pause_var = 1, that mean program pause if pause_var == 1
                self.master.wait_variable(pause_var)
                if self.check_stop_program():
                    break

                positions = self.board.available_moves()
                if(prev_state_p2 != "" and new_state_p2 == ""):
                    prev_action_p2 = self.player2.get_move(self.board)    # take action and update board state
                    self.play_turn(prev_action_p2)
                    reward_2 = self.board.get_reward(prev_action_p2)[1]
                    #print("Reward 2: ", reward_2)

                elif(prev_state_p2 != "" and new_state_p2 != ""):
                    new_action_p2 = self.player2.get_move(self.board)
                    self.update_Q(prev_state_p2, new_state_p2, prev_action_p2, new_action_p2, reward_2, positions)
                    prev_state_p2 = new_state_p2
                    prev_action_p2 = new_action_p2
                    self.play_turn(prev_action_p2)
                    reward_2 = self.board.get_reward(prev_action_p2)[1]
                    #print("Reward 2: ", reward_2)
                if self.board.over():
                    reward_1 = self.board.get_reward(prev_action_p2)[0]
                    #print("Reward 1: ", reward_1)
                    break
                new_state = copy.deepcopy(self.board)
                new_action = self.player1.get_move(new_state)
                #update for p1
                self.update_Q(prev_state, new_state, prev_action, new_action, reward_1, self.board.available_moves())
                prev_state = new_state
                prev_action = new_action
            
            #If the game is over
            if self.board.over():
                global res
                #Show messagebox when the game is over
                res = messagebox.askquestion('Save Policy', 'Do you want to save this policy?')
                #If yes, save the policy
                if res == 'yes':
                    self.update_Q(prev_state, None, prev_action, None, reward_1, None)
                    self.update_Q(prev_state_p2, None, prev_action_p2, None, reward_2, None)
                    if self.mode == 2:
                        fw = open('Policies/policy_' + str(self.row) + '_' + str(self.col) + '_' + str(self.x_win) + '_sa', 'wb')
                        pickle.dump(self.Q, fw)
                        fw.close()
                    elif self.mode == 3:
                        fw = open('Policies/policy_' + str(self.row) + '_' + str(self.col) + '_' + str(self.x_win) + '_ql', 'wb')
                        pickle.dump(self.Q, fw)
                        fw.close()
                    #When after complete save the policy, show messagebox
                    messagebox.showinfo('Save Policy', 'Policy has been saved!')
            
            #If the game is not over
            #And user click "X" or "Back To Menu" or "Reset"
            #The function check_stop_program() will set stop_var to "Q" or "B" or reset_var to "R"
            #In this case, policy will not be saved.
            else: 
                # stop_var = "Q", close window
                if stop_var.get() == "Q":
                    self.master.destroy()
                # stop_var = "B", close this window and call function "main_start" into main.py.
                elif stop_var.get() == "B":
                    import main
                    self.master.destroy()
                    main.main_start()
                # reset_var = "R", reset the game and call function "play" again.
                elif reset_var.get() == "R":
                    
                    label.config(text="Resetting...", font=("Arial", 20))
                    for i in range(self.row):
                        for j in range(self.col):
                            self.buttons[i][j].configure(text=self.empty_text)
                    self.board = Board(self.row, self.col, self.x_win)
                    self.current_player = self.player1
                    self.other_player = self.player2

                    if type(self.player1).__name__ == "QPlayer":
                        label.config(text= self.current_player.mark + "'s Turn")
                    elif type(self.player1).__name__ == "HumanPlayer":
                        label.config(text= "Your Turn")

                    # Set four variable to default value = ""
                    pause_var.set("")
                    stop_var.set("")
                    reset_var.set("")
                    res = ""

                    self.play()

    def play_turn(self, action):
        self.handle_move(action)

    def update_Q(self, s, s_, a, a_, r, positions):
        s = str(copy.deepcopy(s.grid).reshape(self.row*self.col))
        if self.mode == 2:
            if s_ is not None:
                s_ = str(copy.deepcopy(s_.grid).reshape(self.row*self.col))
                # update
                self.Q[a][s] += self.alpha*(r + self.gamma*self.Q[a_][s_] - self.Q[a][s])
            else:
                # terminal state update
                self.Q[a][s] += self.alpha*(r - self.Q[a][s])
        elif self.mode == 3:
            if s_ is not None:
                s_ = str(copy.deepcopy(s_.grid).reshape(self.row*self.col))
                Q_options = [self.Q[p][s_] for p in positions]
                # update
                self.Q[a][s] += self.alpha*(r + self.gamma*max(Q_options) - self.Q[a][s])
            else:
                # terminal state update
                #if self.other_player == self.player1:
                self.Q[a][s] += self.alpha*(r - self.Q[a][s])


class Board:
    def __init__(self, row, col, x_win):
        self.grid = np.zeros((row, col))
        self.row = row
        self.col = col
        self.x_win = x_win
        self.penal = 1 if self.x_win == 3 else 2

    def winner(self):
        for i in range(self.row):
            for j in range(self.col):
                if j + self.x_win <= self.col:
                    if sum(self.grid[i, j:j + self.x_win]) == self.x_win:
                        return "X"
                    if sum(self.grid[i, j:j + self.x_win]) == -self.x_win:
                        return "O"

        # col
        for i in range(self.col):
            for j in range(self.row):
                if j + self.x_win <= self.row:
                    if sum(self.grid[j:j + self.x_win, i]) == self.x_win:
                        return "X"
                    if sum(self.grid[j:j + self.x_win, i]) == -self.x_win:
                        return "O"

        # # diagonal
        for r in range(self.row):
            for c in range(self.col):
                if r + self.x_win - 1 < self.row and c + self.x_win - 1 < self.col:
                    ldiagRight = []
                    for i in range(self.x_win):
                        ldiagRight.append((r + i, c + i))
                    # Xét điểm
                    diag_sum1 = sum([self.grid[dr[0]][dr[1]] for dr in ldiagRight])
                    if diag_sum1 == self.x_win:
                        return "X"
                    if diag_sum1 == -self.x_win:
                        return "O"

        for r in range(self.row):
            for c in range(self.col):
                if r + self.x_win - 1 < self.row and c - self.x_win + 1 >= 0:
                    ldiagLeft = []
                    for i in range(self.x_win):
                        ldiagLeft.append((r + i, c - i))
                    # print(ldiagLeft)
                    # Xét điểm
                    diag_sum2 = sum([self.grid[dl[0]][dl[1]] for dl in ldiagLeft])
                    if diag_sum2 == self.x_win:
                        return "X"
                    if diag_sum2 == -self.x_win:
                        return "O"

        # tie
        # no available positions
        if not np.any(self.grid == 0):
            return 0
        # not end
        return None
    
    def get_reward(self, act):
        result = self.winner()
        if result == "X":
            return 1, -1
        elif result == "O":
            return -1, 1
        elif not np.any(self.grid == 0):
            return 0, 0
        else:
            #Thêm reward -1 nếu máy không chặn khi đối thủ được x-1 con liên tục
            num_check_1 = self.x_win - self.penal
            num_check_2 = -self.x_win + self.penal
            flag_2x = False
            flag_2o = False
            #row
            for i in range(self.row):
                for j in range(self.col - self.x_win + 1):
                    win_board = self.grid[i, j:j + self.x_win]
                    sum_win_board = sum(win_board)
                    #if self.x_win == 5:
                    if sum_win_board == 2 and -1 not in win_board:
                        if act[0] == i and act[1] in range(j, j + self.x_win) and self.grid[act[0], act[1]] == 1:
                            flag_2x = True
                            #return 0.1, 0
                        if self.x_win == 3:
                            return 0, -1
                    ##
                    elif sum_win_board >= num_check_1 and -1 not in win_board:
                        if act[0] == i and act[1] in range(j, j + self.x_win) and self.grid[act[0], act[1]] == 1:
                            if sum_win_board == 3:
                                return 0.5, -0.5
                            return 0.8, -0.8
                        if sum_win_board == 4:
                            return 0, -0.8
                    #if self.x_win == 5:
                    elif sum_win_board == -2 and 1 not in win_board:
                        if act[0] == i and act[1] in range(j, j + self.x_win) and self.grid[act[0], act[1]] == -1:
                            flag_2o = True
                            #return 0, 0.1
                        if self.x_win == 3:
                            return -1, 0
                    ##
                    elif sum_win_board <= num_check_2 and 1 not in win_board:
                        if act[0] == i and act[1] in range(j, j + self.x_win) and self.grid[act[0], act[1]] == -1:
                            if sum_win_board == -3:
                                return -0.5, 0.5
                            return -0.8, 0.8
                        if sum_win_board == -4:
                            return -0.8, 0
          #col
            for i in range(self.col):
                for j in range(self.row - self.x_win + 1):
                    win_board = self.grid[j:j + self.x_win, i]
                    sum_win_board = sum(win_board)
                    #if self.x_win == 5:
                    if sum_win_board == 2 and -1 not in win_board:
                        if act[1] == i and act[0] in range(j, j + self.x_win) and self.grid[act[0], act[1]] == 1:
                            flag_2x = True
                        if self.x_win == 3:
                            return 0, -1
                    ##
                    elif sum_win_board >= num_check_1 and -1 not in win_board:
                        if act[1] == i and act[0] in range(j, j + self.x_win) and self.grid[act[0], act[1]] == 1:
                            if sum_win_board == 3:
                                return 0.5, -0.5
                            return 0.8, -0.8
                        if sum_win_board == 4:
                            return 0, -0.8
                    #if self.x_win == 5:
                    elif sum_win_board == -2 and 1 not in win_board:
                        if act[1] == i and act[0] in range(j, j + self.x_win) and self.grid[act[0], act[1]] == -1:
                            flag_2o = True
                        if self.x_win == 3:
                            return -1, 0
                    ##
                    elif sum_win_board <= num_check_2 and 1 not in win_board:
                        if act[1] == i and act[0] in range(j, j + self.x_win) and self.grid[act[0], act[1]] == -1:
                            if sum_win_board == -3:
                                return -0.5, 0.5
                            return -0.8, 0.8
                        if sum_win_board == -4:
                            return -0.8, 0
          #diagonal
            for r in range(self.row):
                for c in range(self.col):
                    if r + self.x_win - 1 < self.row and c + self.x_win - 1 < self.col:
                        ldiagRight = []
                        for i in range(self.x_win):
                            ldiagRight.append((r + i, c + i))
                        # print(ldiagRight)
                        # Xét điểm
                        win_board = [self.grid[dr[0]][dr[1]] for dr in ldiagRight]
                        diag_sum1 = sum(win_board)
                        #if self.x_win == 5:
                        if diag_sum1 == 2 and -1 not in win_board:
                            if act in ldiagRight and self.grid[act[0], act[1]] == 1:
                                flag_2x = True
                            if self.x_win == 3:
                                return 0, -1
                        ##
                        elif diag_sum1 >= num_check_1 and -1 not in win_board:
                            if act in ldiagRight and self.grid[act[0], act[1]] == 1:
                                if diag_sum1 == 3:
                                    return 0.5, -0.5
                                return 0.8, -0.8
                            if diag_sum1 == 4:
                                return 0, -0.8
                        #if self.x_win == 5:
                        elif diag_sum1 == -2 and 1 not in win_board:
                            if act in ldiagRight and self.grid[act[0], act[1]] == -1:
                                flag_2o = True
                            if self.x_win == 3:
                                return -1, 0
                        ##
                        elif diag_sum1 <= num_check_2 and 1 not in win_board:
                            if act in ldiagRight and self.grid[act[0], act[1]] == -1:
                                if diag_sum1 == -3:
                                    return -0.5, 0.5
                                return -0.8, 0.8
                            if diag_sum1 == -4:
                                return -0.8, 0

            for r in range(self.row):
                for c in range(self.col):
                    if r + self.x_win - 1 < self.row and c - self.x_win + 1 >= 0:
                        ldiagLeft = []
                        for i in range(self.x_win):
                            ldiagLeft.append((r + i, c - i))
                        win_board = [self.grid[dl[0]][dl[1]] for dl in ldiagLeft]
                        diag_sum2 = sum(win_board)
                        #if self.x_win == 5:
                        if diag_sum2 == 2 and -1 not in win_board:
                            if act in ldiagLeft and self.grid[act[0], act[1]] == 1:
                                flag_2x = True
                            if self.x_win == 3:
                                return 0, -1
                        ##
                        elif diag_sum2 >= num_check_1 and -1 not in win_board:
                            if act in ldiagLeft and self.grid[act[0], act[1]] == 1:
                                if diag_sum2 == 3:
                                    return 0.5, -0.5
                                return 0.8, -0.8
                            if diag_sum2 == 4:
                                return 0, -0.8
                        #if self.x_win == 5:
                        elif diag_sum2 == -2 and 1 not in win_board:
                            if act in ldiagLeft and self.grid[act[0], act[1]] == -1:
                                flag_2o = True
                            if self.x_win == 3:
                                return -1, 0
                        ##
                        elif diag_sum2 <= num_check_2 and 1 not in win_board:
                            if act in ldiagLeft and self.grid[act[0], act[1]] == -1:
                                if diag_sum2 == -3:
                                    return -0.5, 0.5
                                return -0.8, 0.8
                            if diag_sum2 == -4:
                                return -0.8, 0
            if flag_2x:
                return 0.1, 0
            elif flag_2o:
                return 0, 0.1
            return 0, 0

    def over(self):             
        return (not np.any(self.grid == 0)) or (self.winner() is not None)

    def place_mark(self, move, mark):       
        num = Board.mark2num(mark)
        self.grid[tuple(move)] = num

    @staticmethod
    def mark2num(mark):         
        d = {"X": 1, "O": -1}
        return d[mark]

    def available_moves(self):
        return [(i,j) for i in range(self.row) for j in range(self.col) if self.grid[i][j] == 0]

    def get_next_board(self, move, mark):
        next_board = copy.deepcopy(self)
        next_board.place_mark(move, mark)
        return next_board

    def make_key(self, mark):          
        fill_value = self.row*self.col
        filled_grid = copy.deepcopy(self.grid)
        np.place(filled_grid, self.filled_grid == 0, fill_value)
        return "".join(map(str, (list(map(int, filled_grid.flatten()))))) + mark


class Player(object):
    def __init__(self, mark):
        self.mark = mark

    @property
    def opponent_mark(self):
        if self.mark == 'X':
            return 'O'
        elif self.mark == 'O':
            return 'X'
        else:
            print("The player's mark must be either 'X' or 'O'.")


class HumanPlayer(Player):
    pass


class ComputerPlayer(Player):
    pass


class RandomPlayer(ComputerPlayer):
    @staticmethod
    def get_move(board):
        moves = board.available_moves()
        if moves:   
            return moves[np.random.choice(len(moves))]    


class THandPlayer(ComputerPlayer):
    def __init__(self, mark):
        super(THandPlayer, self).__init__(mark=mark)

    def get_move(self, board):
        moves = board.available_moves()
        if moves:
            for move in moves:
                if THandPlayer.next_move_winner(board, move, self.mark):
                    return move
                elif THandPlayer.next_move_winner(board, move, self.opponent_mark):
                    return move
            else:
                return RandomPlayer.get_move(board)

    @staticmethod
    def next_move_winner(board, move, mark):
        return board.get_next_board(move, mark).winner() == mark


class QPlayer(ComputerPlayer):
    def __init__(self, mark, Q={}):
        super(QPlayer, self).__init__(mark=mark)
        self.Q = Q

    def get_move(self, board):
        global action
        positions = board.available_moves()
        for p in positions:
            if self.Q.get(p) is None:
                self.Q[p] = defaultdict(int)
        reshape_board = copy.deepcopy(board.grid)
        curr_board = str(reshape_board.reshape(board.row*board.col)) 
        values = np.array([self.Q[p][curr_board] for p in positions])
        ix_max = np.where(values == np.max(values))[0]
        if len(ix_max) > 1:
            ix_select = np.random.choice(ix_max, 1)[0]
        else:
            ix_select = ix_max[0]
        action = positions[ix_select]
        #print(action)
        print(action, values[ix_select])
        return action