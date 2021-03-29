import tkinter as tk
from tkinter import font
from typing import List, Type, Union

from configs.gui_config import WINDOW_WIDTH_IN_PIXELS, WINDOW_HEIGHT_IN_PIXELS
from .real_time_display import RealTimeDisplay
from .simulator import SimulatorPage


class _GUI(tk.Tk):
    def __init__(self, pages_to_register: List[Type['tk.Frame']], *args, **kwargs):
        """
        Initialises the Graphical user interface of the arena and the robot

        :param pages_to_register: List of windows to display in the GUI
        :param args: Tkinter specific arguments
        :param kwargs: Tkinter specific keyword arguments
        """
        tk.Tk.__init__(self, *args, **kwargs)

        self._set_window_size()

        font.nametofont('TkDefaultFont').configure(family='roboto')

        self.frames = {}
        root_container = self._create_root_container()
        self._register_pages(root_container, pages_to_register)

    def _set_window_size(self) -> None:
        """
        Centers and sets the GUI window size
        """
        window_top_offset = int(self.winfo_screenheight() / 2 - WINDOW_HEIGHT_IN_PIXELS / 1.8)
        window_left_offset = int(self.winfo_screenwidth() / 2 - WINDOW_WIDTH_IN_PIXELS / 2)

        self.geometry(f'{WINDOW_WIDTH_IN_PIXELS}x{WINDOW_HEIGHT_IN_PIXELS}+{window_left_offset}+{window_top_offset}')

    def _create_root_container(self) -> 'tk.Frame':
        """
        Creates the root container to house Tkinter widgets

        :return: The initialised root container
        """
        root_container = tk.Frame(self)
        root_container.pack(side="top", fill="both", expand=True)
        root_container.grid_rowconfigure(0, weight=1)
        root_container.grid_columnconfigure(0, weight=1)

        return root_container

    def _register_pages(self, container: 'tk.Frame', page_list: list) -> None:
        """
        Registers all windows required for the GUI

        :param container: The container to house the pages
        :param page_list: List of pages to register
        """
        for page_object in page_list:
            frame = page_object(container)
            frame.grid(row=0, column=0, sticky='NSEW')

            self.frames[page_object] = frame

    def set_main_page(self, page_reference: Union[Type['SimulatorPage'], Type['RealTimeDisplay']]) -> None:
        """
        Sets the main page of the GUI

        :param page_reference: The page to set as the main page
        """
        if page_reference not in self.frames:
            raise KeyError('Page not available in simulator! Register the page first.')

        self.frames[page_reference].tkraise()

    def get_page(self, page_reference: Type['tk.Frame']) -> 'tk.Frame':
        """
        Returns the page reference stored in memory

        :param page_reference: The page to query
        :return: The queried page stored in memory
        """
        if page_reference not in self.frames:
            raise KeyError('Page not available in simulator! Register the page first.')

        return self.frames[page_reference]


class SimulatorGUI(_GUI):
    def __init__(self, *args, **kwargs):
        """
        Initialises a simulator GUI to test and visualise the algorithms implemented

        :param args: Tkinter specific arguments
        :param kwargs: Tkinter specific keyword arguments
        """
        list_of_pages = [SimulatorPage]

        super().__init__(list_of_pages, *args, **kwargs)

        self.set_main_page(SimulatorPage)


class RealTimeGUI(_GUI):
    def __init__(self, *args, **kwargs):
        """
        Initialises a GUI for the actual run

        :param page_reference: The page to query
        :return: The queried page stored in memory
        """
        list_of_pages = [RealTimeDisplay]

        super().__init__(list_of_pages, *args, **kwargs)

        self.set_main_page(RealTimeDisplay)

        self.display_widgets = self.get_page(RealTimeDisplay)
