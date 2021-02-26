import tkinter as tk

from .arena import Arena
from .sidebar import Sidebar


class SimulatorPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        # Define any variables required to communicate between widgets here.
        # Variables must be bound to this class

        self.map_selection_value = tk.StringVar(self)

        arena = Arena(self)
        arena.grid(row=0, column=1, sticky='ns')

        right_sidebar = Sidebar(self, arena, self.map_selection_value)
        right_sidebar.grid(row=0, column=2, sticky='nese')
