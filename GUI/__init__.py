from tkinter import *


class Window:
    _VERSION = "0.0"

    def __init__(self, root: Tk):
        self.root = root
        self._place_root()
        self.exists = True
        # self._place_frames()
        # self._place_textbox()

    def clean_up(self):
        import keyboard, mouse
        keyboard.unhook_all()
        mouse.unhook_all()
        sys.exit()

    def create(self):
        self.root.protocol("WM_DELETE_WINDOW", self.clean_up)
        self.root.mainloop()

    def _place_root(self):
        self.root.title("Mag Generator, v. " + self._VERSION)
        self.root.resizable(False, False)
        # self.root.state('zoomed')

    # def _place_frames(self):
    #     self.frames = [[Frame()] * 40 for _ in range(22)]
    #     # colors = ['black', 'white']
    #     for i in range(22):
    #         for j in range(40):
    #             self.frames[i][j] = Frame(self.root, background='lightblue', height=20, width=20)
    #             self.frames[i][j].grid(row=i, column=j, sticky=N + S + E + W)
    #             self.frames[i][j].bind("<Button-1>", lambda event: self.frames[i][j].focus_set())
    #             self.root.grid_columnconfigure(j, weight=1)
    #             self.root.grid_rowconfigure(i, weight=1)
    #
    # def _place_textbox(self):
    #     self.frames[1][22] = Frame(self.root, background='bisque', bd=5)
    #     self.frames[1][22].grid(column=22, row=1, sticky=N + S + E + W, columnspan=8, rowspan=8)
    #     self.text = Text(self.frames[1][22], wrap=WORD, width=12, height=12)
    #     self.text.pack(fill=BOTH, expand=True)

# https://miro.medium.com/max/1400/1*DrO7NyijnQeNeRveZ8pf8g.gif
