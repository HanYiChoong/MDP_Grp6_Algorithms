import tkinter as tk

from .arena import Arena
from .sidebars import LeftSidebar, RightSidebar


class SimulatorPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        # Define any variables required to communicate between widgets here.
        # Variables must be bound to this class

        self.map_selection_value = tk.StringVar(self)

        left_sidebar = LeftSidebar(self, self.map_selection_value)
        left_sidebar.grid(row=0, column=0, sticky='nwsw')

        arena = Arena(self)
        arena.grid(row=0, column=1, sticky='ns')

        right_sidebar = RightSidebar(self, arena)
        right_sidebar.grid(row=0, column=2, sticky='nese')
