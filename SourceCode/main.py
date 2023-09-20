import tkinter as tk
from tkinter import Button, Entry, StringVar, Label, IntVar, Radiobutton, messagebox, Listbox
import numpy as np

import copy
import os
import pickle as pickle    
from PIL import ImageTk, Image
from interface import Game, HumanPlayer, QPlayer, RandomPlayer, THandPlayer
from Models import easy, monte_carlo_prediction, sarsa, q_learning


def game_start(master,row,column,win,level):

    global policy
    
    r = row.get()
    c = column.get()
    w = win.get()
    mode_value = mode.get()
    mode_value_player = mode_player.get()
    mode_value_player_0_1 = mode_player_0_1.get()
    number_win_value = number_win.get()

    if (int(r) < 3 or int(c) < 3 or int(w) < 3):
        messagebox.showerror('Error Parameters', 'Board must be at least 3x3 and Number of X must be at least 3')
        return
    if (int(w) > int(r) or int(w) > int(c)):
        messagebox.showerror('Error Parameters', 'Number of X must be smaller than row and column or equal to row or column')
        return
    #q_learning not stop player when player meet condition to win
    if mode_value == 0:
        policy = "Policies/policy_" + str(r) + "_" + str(c) + "_" + str(w) + "_" + "easy"
    #monte carlo
    elif mode_value == 1:
        policy = "Policies/policy_" + str(r) + "_" + str(c) + "_" + str(w) + "_" + "mc"
    #sarsa
    elif mode_value == 2:
        policy = "Policies/policy_" + str(r) + "_" + str(c) + "_" + str(w) + "_" + "sa"
    #q learning
    elif mode_value == 3:
        policy = "Policies/policy_" + str(r) + "_" + str(c) + "_" + str(w) + "_" + "ql"
            
    try:
        Q = pickle.load(open(policy, "rb"))
    except FileNotFoundError as e:
        res=messagebox.askquestion('Create New Policy', 'This policy does not exist. Do you want to create it?')
        if res == 'yes':
            if mode_value == 0:
                easy.Tic_Tac_Toe(int(r), int(c), int(w)) 
            elif mode_value == 1:
                monte_carlo_prediction.Tic_Tac_Toe(int(r), int(c), int(w)) 
            elif mode_value == 2:
                sarsa.Tic_Tac_Toe(int(r), int(c), int(w))
            elif mode_value == 3:
                q_learning.Tic_Tac_Toe(int(r), int(c), int(w))
            messagebox.showinfo('Train Model', 'Training is Successful')
            Q = pickle.load(open(policy, "rb"))
        else:
            return
   
    # Choose player - bot, bot - bot
    if mode_value_player == 0:
        # Choose player first
        if mode_value_player_0_1 == 0:
            player1 = HumanPlayer(mark="X")
            player2 = QPlayer(mark="O")
        # Choose bot first
        elif mode_value_player_0_1 == 1:
            player1 = QPlayer(mark="X")
            player2 = HumanPlayer(mark="O")
    elif mode_value_player == 1:
        player1 = QPlayer(mark="X")
        player2 = QPlayer(mark="O")

    master.destroy()
        
    tic_tac_toe_app = tk.Tk()
    #-----15/08/2023-----
    tic_tac_toe_app.title("Caro Game")
    tic_tac_toe_app.state('zoomed')
    tic_tac_toe_app.resizable(0, 0)
    #-----15/08/2023-----
  

    game = Game(tic_tac_toe_app, player1, player2, Q=Q, row=int(r), col=int(c), x_win=number_win_value, level = mode_value)
    game.play()

    tic_tac_toe_app.mainloop()

#-----15/08/2023-----
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        main_app.destroy()
#-----15/08/2023-----

def main_start():

    global mode
    global mode_player
    global number_win
    global main_app

    main_app = tk.Tk()
    main_app.title("Menu")

    # -----15/08/2023-----
    # Full screen but not hide taskbar
    main_app.state('zoomed')
    # Block size of window
    main_app.resizable(0, 0)
    # -----15/08/2023-----

    #-----15/08/2023-----
    # Show messagebox after click X in window through function on_closing
    main_app.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Set content in frame have position center
    main_app.grid_columnconfigure(0, weight=1)
    main_app.grid_rowconfigure(0, weight=1)

    # Create frame for label Caro Game and image.
    frame_main = tk.Frame(main_app)
    frame_main.grid(row=0, column=0)
    #-----15/08/2023-----
    
    main_label = Label(frame_main, text="Caro Game")
    main_label.config(font=("Arial", 30))
    main_label.grid(row=0, column=1, pady=10)
    
    #Put image to frame
    img = ImageTk.PhotoImage(Image.open("CaroVN.jpg").resize((250, 250)))
    img_label = Label(frame_main, image=img)
    img_label.grid(row=1, column=1)

    # Create frame for content.
    frame_content = tk.Frame()
    frame_content.grid()

    # Create label and entry for row, column and win.
    row_label = Label(frame_content, text="Enter Row:")
    row_label.config(font=("Arial", 15))
    row_label.grid(row=2, column=0, padx=10, pady=10)

    row_string = StringVar(frame_content, '9')
    row_entry = Entry(frame_content, textvariable=row_string, width=5, font=("Arial", 15))
    row_entry.grid(row=2, column=1)
    row = Entry(frame_content, textvariable=row_string)

    column_label = Label(frame_content, text="Enter Column:")
    column_label.config(font=("Arial", 15))
    column_label.grid(row=3, column=0, padx=10, pady=10)

    column_string = StringVar(frame_content, '9')
    column_entry = Entry(frame_content, textvariable=column_string, width=5, font=("Arial", 15))
    column_entry.grid(row=3, column=1)
    column = Entry(frame_content, textvariable=column_string)

    # win_label = Label(frame_content, text="Enter Number of X:")
    # win_label.config(font=("Arial", 15))
    # win_label.grid(row=4, column=0, padx=10, pady=10)

    # win_string = StringVar(frame_content, '3')
    # win_entry = Entry(frame_content, textvariable=win_string, width=5, font=("Arial", 15))
    # win_entry.grid(row=4, column=1)
    # win = Entry(frame_content, textvariable=win_string)

    number_win = IntVar()
    number_win.set(5)
    number_win_label = Label(frame_content, text="Choose Number of X:")
    number_win_label.config(font=("Arial", 15))
    number_win_label.grid(row=4, column=0, padx=10, pady=10)

    number_win_0 = Radiobutton(frame_content, text="3", variable=number_win, value=3, font=("Arial", 15))
    number_win_0.grid(row=4, column=1, padx=10, pady=10)

    number_win_1 = Radiobutton(frame_content, text="5", variable=number_win, value=5, font=("Arial", 15))
    number_win_1.grid(row=4, column=2, padx=10, pady=10)


    # global listbox_policy
    # global previous_selected
    # global value_listbox_policy

    # # Check click item in listbox
    # previous_selected = None
    # # Store value of listbox after click item in listbox
    # value_listbox_policy = None
    
    # # Create listbox for policy
    # listbox_label = Label(frame_content, text="Choose Policy Was Created")
    # listbox_label.config(font=("Arial", 15))
    # listbox_label.grid(row=2, column=2, pady=5, padx=10)
    # listbox_policy = Listbox(frame_content, font=("Arial", 10))

    # Bind event for listbox
    # ListboxSelect that mean selected item in listbox
    # Double-Button-1 that mean double click (click again at same position) in listbox
    # selected_item and deselected_item are functions
    # listbox_policy.bind("<<ListboxSelect>>", selected_item)
    # listbox_policy.bind("<Double-Button-1>" , deselected_item)
    # listbox_policy.grid(row= 3, column=2, rowspan = 2)
    
    # i = 0
    # # Scan all policies in Policies folder
    # # Add all policies to listbox
    # policies = os.listdir('Policies')
    # for policy in policies:
    #     listbox_policy.insert(i, policy)
    #     i=i+1

    # Create frame for radio button.
    frame_radio_button = tk.Frame()
    frame_radio_button.grid()

    # Create radio button for level.
    mode = IntVar()
    mode.set(0)
    mode_label = Label(frame_radio_button, text="Choose Level:")
    mode_label.config(font=("Arial", 15))
    mode_label.grid(row=5, column=0, padx=10, pady=10)

    mode_0 = Radiobutton(frame_radio_button, text="1", variable=mode, value=0, font=("Arial", 15))
    mode_0.grid(row=5, column=1, padx=10, pady=10)

    mode_1 = Radiobutton(frame_radio_button, text="2", variable=mode, value=1, font=("Arial", 15))
    mode_1.grid(row=5, column=2, padx=10, pady=10)

    mode_2 = Radiobutton(frame_radio_button, text="3", variable=mode, value=2, font=("Arial", 15))
    mode_2.grid(row=5, column=3, padx=10, pady=10)

    mode_3 = Radiobutton(frame_radio_button, text="4", variable=mode, value=3, font=("Arial", 15))
    mode_3.grid(row=5, column=4, padx=10, pady=10)

    # Create frame for radio button player.
    frame_radio_button_player = tk.Frame()
    frame_radio_button_player.grid()

    # Create radio button for mode (label).
    mode_player = IntVar()
    mode_player.set(0)
    mode_player_label = Label(frame_radio_button_player, text="Choose Mode:")
    mode_player_label.config(font=("Arial", 15))
    mode_player_label.grid(row=6, column=0, padx=10, pady=10)

    # This is variable for checking to rebuild (remove and build again)
    # frame_radio_button_player_0_1
    # and frame_btn
    # block_mode_0 for player - bot
    # block_mode_1 for bot - bot
    global block_mode_0
    global block_mode_1
    block_mode_0 = 1
    block_mode_1 = 1

    # Create radio button for mode (button).

    mode_player_0 = Radiobutton(frame_radio_button_player, text="Player - Bot", variable=mode_player, value=0, font=("Arial", 15), command= lambda which_mode = 0: check_mode_player(which_mode))
    mode_player_0.grid(row=6, column=1, padx=10, pady=10)
    
    mode_player_1 = Radiobutton(frame_radio_button_player, text="Bot - Bot", variable=mode_player, value=1, font=("Arial", 15), command= lambda which_mode = 1: check_mode_player(which_mode))
    mode_player_1.grid(row=6, column=2, padx=10, pady=10)
    
    # All global variables below for using in check_mode_player
    global frame_radio_button_player_0_1
    global mode_player_0_1
    global frame_btn

    # Create frame for radio button player-bot.
    frame_radio_button_player_0_1 = tk.Frame()
    frame_radio_button_player_0_1.grid()

    # Create radio button for player-bot.
    mode_player_0_1 = IntVar()
    mode_player_0_1.set(0)
    mode_player_0_1_label = Label(frame_radio_button_player_0_1, text="Who First:")
    mode_player_0_1_label.config(font=("Arial", 15))
    mode_player_0_1_label.grid(row=7, column=0, padx=10, pady=10)

    mode_player_0_1_0 = Radiobutton(frame_radio_button_player_0_1, text="Player", variable=mode_player_0_1, value=0, font=("Arial", 15))
    mode_player_0_1_0.grid(row=7, column=1, padx=10, pady=10)
    mode_player_0_1_1 = Radiobutton(frame_radio_button_player_0_1, text="Bot", variable=mode_player_0_1, value=1, font=("Arial", 15))
    mode_player_0_1_1.grid(row=7, column=2, padx=10, pady=10)

    # Create frame for button confirm.
    frame_btn = tk.Frame()
    frame_btn.grid()

    # Create button confirm.
    buttonConfirm = Button(frame_btn , text = "START", command = lambda main_app=main_app, row=row, column=column, number_win=number_win, level=mode: game_start(main_app,row,column, number_win, level), bg="green", fg='white', font=("Arial", 15))
    buttonConfirm.grid(row=8, column=0, pady=20)

    def check_mode_player(which_mode): 
        global frame_radio_button_player_0_1
        global frame_btn
        global block_mode_0
        global block_mode_1
        global mode_player_0_1
        # Remove frames
        frame_radio_button_player_0_1.destroy()
        frame_btn.destroy()
        # Select player-bot, show frame label "Who Fisrt:"
        if which_mode == 0:
            # With block_mode_0 == 1, this case for initialize for player-bot
            if block_mode_0 == 1:
                
                # Create frame for radio button player-bot.
                frame_radio_button_player_0_1 = tk.Frame()
                frame_radio_button_player_0_1.grid()
                # Create radio button for player-bot.
                mode_player_0_1 = IntVar()
                mode_player_0_1.set(0)
                mode_player_0_1_label = Label(frame_radio_button_player_0_1, text="Who First:")
                mode_player_0_1_label.config(font=("Arial", 15))
                mode_player_0_1_label.grid(row=7, column=0, padx=10, pady=10)

                mode_player_0_1_0 = Radiobutton(frame_radio_button_player_0_1, text="Player", variable=mode_player_0_1, value=0, font=("Arial", 15))
                mode_player_0_1_0.grid(row=7, column=1, padx=10, pady=10)
                mode_player_0_1_1 = Radiobutton(frame_radio_button_player_0_1, text="Bot", variable=mode_player_0_1, value=1, font=("Arial", 15))
                mode_player_0_1_1.grid(row=7, column=2, padx=10, pady=10)

                # Create frame for button confirm.
                frame_btn = tk.Frame()
                frame_btn.grid()
                # Create button confirm.
                buttonConfirm = Button(frame_btn , text = "START", command = lambda main_app=main_app, row=row, column=column, number_win=number_win, level=mode: game_start(main_app,row,column, number_win, level), bg="green", fg='white', font=("Arial", 15))
                buttonConfirm.grid(row=8, column=0, pady=20)
                block_mode_0 = 2

            # With block_mode_1 == 3 or block_mode_1 == 1, this case for select bot-bot and after that select player-bot
            # or select player-bot and after that continue select player-bot while bot-bot not intialize.
            elif block_mode_1 == 3 or block_mode_1 == 1:
                # Remove frame_btn
                frame_btn.destroy()

                # Create frame for radio button player-bot.
                frame_radio_button_player_0_1 = tk.Frame()
                frame_radio_button_player_0_1.grid()

                # Create radio button for player-bot.
                mode_player_0_1 = IntVar()
                mode_player_0_1.set(0)
                mode_player_0_1_label = Label(frame_radio_button_player_0_1, text="Who First:")
                mode_player_0_1_label.config(font=("Arial", 15))
                mode_player_0_1_label.grid(row=7, column=0, padx=10, pady=10)

                mode_player_0_1_0 = Radiobutton(frame_radio_button_player_0_1, text="Player", variable=mode_player_0_1, value=0, font=("Arial", 15))
                mode_player_0_1_0.grid(row=7, column=1, padx=10, pady=10)
                mode_player_0_1_1 = Radiobutton(frame_radio_button_player_0_1, text="Bot", variable=mode_player_0_1, value=1, font=("Arial", 15))
                mode_player_0_1_1.grid(row=7, column=2, padx=10, pady=10)

                frame_btn = tk.Frame()
                frame_btn.grid()
                buttonConfirm = Button(frame_btn , text = "START", command = lambda main_app=main_app, row=row, column=column, number_win=number_win, level=mode: game_start(main_app,row,column, number_win, level), bg="green", fg='white', font=("Arial", 15))
                buttonConfirm.grid(row=8, column=0, pady=20)
                block_mode_0 = 2

        
        #Select bot-bot, detroy frame label "Who Fisrt:"
        elif which_mode == 1:
            # With block_mode_1 == 1, this case for intialize for bot-bot
            if block_mode_1 == 1:
                frame_btn = tk.Frame()
                frame_btn.grid()
                buttonConfirm = Button(frame_btn , text = "START", command = lambda main_app=main_app, row=row, column=column, number_win=number_win, level=mode: game_start(main_app,row,column, number_win, level), bg="green", fg='white', font=("Arial", 15))
                buttonConfirm.grid(row=7, column=0, pady=20)
                block_mode_1 = 3
            # With block_mode_0 == 2 or block_mode_0 == 1, this case for select player-bot and after that select bot-bot
            # or select bot-bot and after that continue select bot-bot while player-bot not intialize
            elif block_mode_0 == 2 or block_mode_0 == 1:
                # Remove frame_radio_button_player_0_1
                frame_radio_button_player_0_1.destroy()
                # Remove frame_btn
                frame_btn.destroy()

                # Create frame for button confirm.
                frame_btn = tk.Frame()
                frame_btn.grid()

                # Create button confirm.
                buttonConfirm = Button(frame_btn , text = "START", command = lambda main_app=main_app, row=row, column=column, number_win=number_win, level=mode: game_start(main_app,row,column, number_win, level), bg="green", fg='white', font=("Arial", 15))
                buttonConfirm.grid(row=7, column=0, pady=20)

                block_mode_1 = 3


    

    main_app.mainloop()


if __name__ == "__main__":
    main_start()


# row = int(input("Nhập số dòng: "))
# col = int(input("Nhập số cột: "))
# x_win = int(input("Nhập số lượng quân thắng: "))