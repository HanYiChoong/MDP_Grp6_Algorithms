import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from algorithms.fastest_path_solver import AStarAlgorithm
from logger import print_error_log

_selection_values = ('Sample Arena', 'test')
_BASE_WIDTH_LEFT_SIDEBAR = 25  # Width of the widget that controls the width of the left sidebar
_BUTTON_INNER_PADDING_X = 5
_BUTTON_INNER_PADDING_Y = 10
_BASE_BUTTON_WIDTH = _BASE_WIDTH_LEFT_SIDEBAR + 3


def _command(message):
    # filler function
    print(f'hello {message}')


class LeftSidebar(tk.Frame):
    # Might not need this side bar in the future?
    # TODO: Create a function to load the map from disk. Return map
    def __init__(self, parent, selected_value_reference, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky='n', padx=10, pady=(10, 20))

        self._create_load_map_widget(container, selected_value_reference)

        ttk.Separator(self, orient='horizontal') \
            .grid(row=1, column=0, sticky='ew')

        log_container = tk.Frame(self)
        log_container.grid(row=2, column=0, sticky='sw', pady=(10, 0))

        self._create_log_area(log_container)

    def _create_load_map_widget(self, container, selected_value_reference):
        option_menu = ttk.OptionMenu(container,
                                     selected_value_reference,
                                     _selection_values[0],
                                     *_selection_values)

        option_menu.config(width=_BASE_WIDTH_LEFT_SIDEBAR)
        option_menu.grid(row=0, column=0, sticky='nw', pady=(0, 10), ipadx=5, ipady=5)

        load_map_button = tk.Button(container,
                                    text='Load Map',
                                    command=lambda: _command('123'))  # loads the map on the canvas

        load_map_button.config(width=_BASE_BUTTON_WIDTH)
        load_map_button.grid(row=2, column=0, sticky='nw', ipadx=_BUTTON_INNER_PADDING_X, ipady=_BUTTON_INNER_PADDING_Y)

    def _create_log_area(self, log_container):
        text_area = ScrolledText(log_container, height=37, width=_BASE_WIDTH_LEFT_SIDEBAR + 5)
        text_area.config(state='disabled')
        text_area.grid(row=0, column=0, sticky='n')


class RightSidebar(tk.Frame):
    # TODO: Get the reference of the map from the arena canvas and function to update canvas item
    def __init__(self, parent, arena_widget, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.arena_widget = arena_widget
        self.a_star_solver = AStarAlgorithm(self.arena_widget.arena_map)

        self._waypoint_x_input = tk.StringVar()
        self._waypoint_y_input = tk.StringVar()
        self.way_point = None
        self._waypoint_input_must_be_hidden = False

        algorithms_container = tk.Frame(self)
        algorithms_container.grid(row=0, column=0, sticky='n', padx=21, pady=(10, 0))

        self._create_algo_buttons_widget(algorithms_container)

        self.waypoint_container = tk.Frame(self,
                                           # highlightbackground='green',
                                           # highlightthickness=1
                                           )

        self._create_input_waypoint_widget()

        reset_button = tk.Button(self, text='Reset', command=self.reset_map)
        reset_button.grid(row=2,
                          column=0,
                          sticky='n',
                          padx=21,
                          pady=(100, 0),
                          ipadx=_BUTTON_INNER_PADDING_X * 17 + 3,
                          ipady=_BUTTON_INNER_PADDING_Y)

    def _create_algo_buttons_widget(self, algorithms_container):
        exploration_button = tk.Button(algorithms_container, text='Exploration')
        exploration_button.config(width=_BASE_BUTTON_WIDTH)
        exploration_button.grid(row=0,
                                column=0,
                                sticky='n',
                                pady=(0, 10),
                                ipadx=_BUTTON_INNER_PADDING_X,
                                ipady=_BUTTON_INNER_PADDING_Y)

        image_recognition_button = tk.Button(algorithms_container, text='Image Recognition')
        image_recognition_button.config(width=_BASE_BUTTON_WIDTH)
        image_recognition_button.grid(row=1,
                                      column=0,
                                      sticky='n',
                                      pady=(0, 10),
                                      ipadx=_BUTTON_INNER_PADDING_X,
                                      ipady=_BUTTON_INNER_PADDING_Y)

        fastest_path_button = tk.Button(algorithms_container,
                                        text='Fastest Path',
                                        command=self._toggle_waypoint_input_container_visibility)
        fastest_path_button.config(width=_BASE_BUTTON_WIDTH)
        fastest_path_button.grid(row=2,
                                 column=0,
                                 sticky='n',
                                 pady=(0, 10),
                                 ipadx=_BUTTON_INNER_PADDING_X,
                                 ipady=_BUTTON_INNER_PADDING_Y)

    def _create_input_waypoint_widget(self):
        frame_label = tk.Label(self.waypoint_container, text='Enter waypoint')
        frame_label.grid(row=0, column=0, sticky='w', pady=(0, 3))

        x_label = tk.Label(self.waypoint_container, text='x:')
        x_label.grid(row=1, column=0, sticky='w')

        x_input_box = tk.Entry(self.waypoint_container, textvariable=self._waypoint_x_input)
        x_input_box.grid(row=1, column=0, sticky='w', padx=(25, 0), pady=(0, 5))

        y_label = tk.Label(self.waypoint_container, text='y:')
        y_label.grid(row=2, column=0, sticky='w')

        y_input_box = tk.Entry(self.waypoint_container, textvariable=self._waypoint_y_input)
        y_input_box.grid(row=2, column=0, sticky='w', padx=(25, 0), pady=(0, 15))

        submit_button = tk.Button(self.waypoint_container,
                                  text='Set Waypoint',
                                  command=self._set_waypoint_on_arena)
        submit_button.grid(row=3,
                           column=0,
                           sticky='n',
                           ipadx=_BUTTON_INNER_PADDING_X,
                           ipady=_BUTTON_INNER_PADDING_Y)

        start_button = tk.Button(self.waypoint_container,
                                 text='Start',
                                 command=self._run_fastest_path_algorithm)
        start_button.grid(row=3,
                          column=1,
                          sticky='n',
                          ipadx=_BUTTON_INNER_PADDING_X + 10,
                          ipady=_BUTTON_INNER_PADDING_Y)

    def _toggle_waypoint_input_container_visibility(self):
        if self._waypoint_input_must_be_hidden:
            self.waypoint_container.grid_remove()
            self._waypoint_input_must_be_hidden = False

            return

        self.waypoint_container.grid(row=1, column=0, sticky='n')
        self._waypoint_input_must_be_hidden = True

    def _run_fastest_path_algorithm(self):
        if not self.way_point:
            return

        start_point = [18, 1]
        end_point = [1, 13]

        path = self.a_star_solver.run_algorithm(start_point, self.way_point, end_point, 0, False)

        if not path:
            print_error_log('No fastest path found!')
            return

        self._display_result_on_canvas(path)

    def _set_waypoint_on_arena(self):
        if self._waypoint_x_input.get() == '' or self._waypoint_y_input.get() == '':
            print_error_log('Enter way point!')
            return

        self.way_point = [int(self._waypoint_x_input.get()), int(self._waypoint_y_input.get())]

        if self.a_star_solver.is_not_within_range_with_virtual_wall(self.way_point):
            print_error_log('Not within valid range or point is on obstacle or virtual wall')
            return

        self.arena_widget.set_way_point(self.way_point)

    def _display_result_on_canvas(self, path):
        if len(path) <= 0:
            return

        t = path.pop(0)
        self.arena_widget.update_cell_on_map(t)
        self.arena_widget.after(100, self._display_result_on_canvas, path)

    def reset_map(self):
        self.arena_widget.reset_map()
        self._waypoint_x_input.set('')
        self._waypoint_y_input.set('')
