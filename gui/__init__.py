import tkinter as tk
from tkinter import font
from typing import List, Type

from configs.gui_config import WINDOW_WIDTH_IN_PIXELS, WINDOW_HEIGHT_IN_PIXELS
from .real_time_display import RealTimeDisplay
from .simulator import SimulatorPage


class _GUI(tk.Tk):
    def __init__(self, pages_to_register: List[Type['tk.Frame']], *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self._set_window_size()

        font.nametofont('TkDefaultFont').configure(family='roboto')

        self.frames = {}
        root_container = self._create_root_container()
        self._register_pages(root_container, pages_to_register)

    def _set_window_size(self):
        # centers the window
        window_top_offset = int(self.winfo_screenheight() / 2 - WINDOW_HEIGHT_IN_PIXELS / 1.8)
        window_left_offset = int(self.winfo_screenwidth() / 2 - WINDOW_WIDTH_IN_PIXELS / 2)

        self.geometry(f'{WINDOW_WIDTH_IN_PIXELS}x{WINDOW_HEIGHT_IN_PIXELS}+{window_left_offset}+{window_top_offset}')

    def _create_root_container(self):
        root_container = tk.Frame(self)
        root_container.pack(side="top", fill="both", expand=True)
        root_container.grid_rowconfigure(0, weight=1)
        root_container.grid_columnconfigure(0, weight=1)

        return root_container

    def _register_pages(self, container, page_list):
        for page in page_list:
            frame = page(container)
            frame.grid(row=0, column=0, sticky='NSEW')

            self.frames[page] = frame

    def set_main_page(self, page_reference):
        if page_reference not in self.frames:
            raise KeyError('Page not available in simulator! Register the page first.')

        self.frames[page_reference].tkraise()

    def get_page(self, page_reference):
        if page_reference not in self.frames:
            raise KeyError('Page not available in simulator! Register the page first.')

        return self.frames[page_reference]


class SimulatorGUI(_GUI):
    def __init__(self, *args, **kwargs):
        list_of_pages = [SimulatorPage]

        super().__init__(list_of_pages, *args, **kwargs)

        self.set_main_page(SimulatorPage)


class RealTimeGUI(_GUI):
    def __init__(self, *args, **kwargs):
        list_of_pages = [RealTimeDisplay]

        super().__init__(list_of_pages, *args, **kwargs)

        self.set_main_page(RealTimeDisplay)

        self.display_widgets = self.get_page(RealTimeDisplay)
