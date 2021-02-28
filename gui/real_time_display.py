import tkinter as tk

from .arena import Arena
from .sidebar import LogMessageSidebar


class RealTimeDisplay(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.arena = Arena(self)
        self.arena.grid(row=0, column=0, sticky='ns')

        self.log_area = LogMessageSidebar(self)
        self.log_area.grid(row=0, column=1, sticky='nese')
