import tkinter as tk

from map import Map
from robot import SimulatorBot
from utils.constants import ROBOT_START_POINT
from utils.enums import Direction
from .arena import Arena
from .sidebar import Sidebar


class SimulatorPage(tk.Frame):
    def __init__(self, parent, **kwargs):
        """
        Initialises the main container for the GUI widgets

        :param parent: The root container of the GUI window
        :param kwargs: Tkinter specific keyword arguments
        """
        tk.Frame.__init__(self, parent, **kwargs)

        # Define any variables required to communicate between widgets here.

        self.map_selection_value = tk.StringVar(self)
        map_reference = Map()

        robot_reference = SimulatorBot(ROBOT_START_POINT,
                                       map_reference.sample_arena,
                                       Direction.EAST)

        arena = Arena(self, robot=robot_reference, map_reference=map_reference)
        arena.grid(row=0, column=1, sticky='ns')

        right_sidebar = Sidebar(self, arena, self.map_selection_value)
        right_sidebar.grid(row=0, column=2, sticky='nese')
