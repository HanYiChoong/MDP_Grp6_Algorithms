import tkinter as tk

from map import Map
from .arena import Arena
from .sidebar import LogMessageSidebar


class RealTimeDisplay(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        map_reference = Map()
        robot = None

        self.arena = Arena(self, robot=robot, map_reference=map_reference)
        self.arena.grid(row=0, column=0, sticky='ns')

        self.log_area = LogMessageSidebar(self)
        self.log_area.grid(row=0, column=1, sticky='nese')
