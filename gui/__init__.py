import tkinter as tk
from tkinter import font

from .simulator import SimulatorPage
from configs.gui_config import WINDOW_WIDTH_IN_PIXELS, WINDOW_HEIGHT_IN_PIXELS

_page_class_reference_list = [SimulatorPage]


class GUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # centers the window
        window_top_offset = int(self.winfo_screenheight() / 2 - WINDOW_HEIGHT_IN_PIXELS / 1.8)
        window_left_offset = int(self.winfo_screenwidth() / 2 - WINDOW_WIDTH_IN_PIXELS / 2)
        self.geometry(f'{WINDOW_WIDTH_IN_PIXELS}x{WINDOW_HEIGHT_IN_PIXELS}+{window_left_offset}+{window_top_offset}')

        self.frames = {}
        self._setup_pages()

        font.nametofont('TkDefaultFont').configure(family='roboto')

        self.frames[SimulatorPage].tkraise()

    def _setup_pages(self):
        root_container = tk.Frame(self)
        root_container.pack(side="top", fill="both", expand=True)
        root_container.grid_rowconfigure(0, weight=1)
        root_container.grid_columnconfigure(0, weight=1)

        self._register_pages(root_container)

    def _register_pages(self, container):
        for page in _page_class_reference_list:
            frame = page(container)
            frame.grid(row=0, column=0, sticky='NSEW')

            self.frames[page] = frame
