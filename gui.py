import tkinter as tk
from tkinter import ttk

class GUI:
    def __init__(self):
        # Initial tkinter setup
        self.root = tk.Tk()
        self.root.title('Title goes here')
        #self.root.iconbitmap('icon.ico')
        
        # Constants
        self.MAX_PLAYERS = 4
        self.PLAYER_TYPES = ('Random', 'IS-MCTS', 'NFSP')

        self.create_gui()

        self.root.mainloop()

    def create_gui(s):
        # Main grid
        s.frame_leftside = ttk.Frame(s.root)
        s.frame_rightside = ttk.Frame(s.root)

        s.frame_leftside.grid(row=0, column=0)
        s.frame_rightside.grid(row=0, column=1)


        # Select no. of players (nop)
        s.frame_nop = ttk.Frame(s.frame_leftside)
        s.label_nop = ttk.Label(s.frame_nop, text='No of players:')
        s.stringvar_nop = tk.StringVar()
        s.spinbox_nop = ttk.Spinbox(s.frame_nop, from_=1, to=4, textvariable=s.stringvar_nop)

        s.frame_nop.grid(row=0, column=0, padx=5, pady=5)
        s.label_nop.grid(row=0, column=0, padx=5, pady=5)
        s.spinbox_nop.grid(row=0, column=1, padx=5, pady=5)
        
        
        # Select player types (pt)
        s.frame_pt = ttk.Frame(s.frame_leftside)
        s.frame_pt['padding'] = 5
        s.frame_pt.grid(row=1, column=0)

        s.label_pt = [None] * s.MAX_PLAYERS
        s.stringvar_pt = [None] * s.MAX_PLAYERS
        s.combobox_pt = [None] * s.MAX_PLAYERS
        for i in range (0, s.MAX_PLAYERS):
            s.label_pt[i] = ttk.Label(s.frame_pt, text=f'Player {str(i)}:')
            s.stringvar_pt[i] = tk.StringVar()
            s.combobox_pt[i] = ttk.Combobox(s.frame_pt, textvariable=s.stringvar_pt[i])
            s.combobox_pt[i]['values'] = s.PLAYER_TYPES

            s.label_pt[i].grid(row=i, column=0, padx=5, pady=5)
            s.combobox_pt[i].grid(row=i, column=1, padx=5, pady=5)


        # Game log (log)
        s.button_log = ttk.Button(s.frame_rightside, text='Start', command=s.start_game)
        s.text_log = tk.Text(s.frame_rightside, width=40, height=10)

        s.button_log.grid(row=0, column=0)
        s.text_log.grid(row=1, column=0)

    def start_game(self):
        self.button_log.configure(text='Stop')
        self.interrupt = False
        self.root.after(1000, lambda: self.test_text_log(0))
    
    def test_text_log(self, line_no):
        self.text_log.insert(str(line_no) + '.0', 'Hello world!\n')
        print('Text inserted')
        if line_no > 30:
            return
        self.root.after(1000, lambda: self.test_text_log(line_no + 1))        

gui = GUI()