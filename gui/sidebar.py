import tkinter as tk
from tkinter import ttk

from algorithms.fastest_path_solver import AStarAlgorithm
from utils.enums import Direction
from utils.logger import print_error_log
from utils.constants import ROBOT_START_POINT, ROBOT_END_POINT

_selection_values = ('sample_arena_0',
                     'sample_arena_1',
                     'sample_arena_2',
                     'sample_arena_3',
                     'sample_arena_4',
                     'sample_arena_5')
_BASE_WIDTH_SIDEBAR = 25
_BUTTON_INNER_PADDING_X = 5
_BUTTON_INNER_PADDING_Y = 10
_BASE_BUTTON_WIDTH = _BASE_WIDTH_SIDEBAR + 3
_TITLE_FONT = ('Roboto bold', 12)


class Sidebar(tk.Frame):
    def __init__(self, parent, arena_widget, selected_value_reference, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.arena_widget = arena_widget
        self.a_star_solver = AStarAlgorithm(self.arena_widget.arena_map)

        self._waypoint_x_input = tk.StringVar()
        self._waypoint_y_input = tk.StringVar()
        self.way_point = None
        self._show_waypoint_input = False
        self.waypoint_container = None

        self._coverage_limit_input = tk.IntVar()
        self._time_limit_input = tk.StringVar()
        self._show_exploration_input = False
        self.exploration_settings_container = None
        self.use_image_rec = False

        self._robot_speed_input = tk.IntVar()
        self.algorithm_is_running = False

        map_container = tk.Frame(self)
        map_container.grid(row=0, column=0, sticky='n', padx=10, pady=(10, 20))
        self._create_load_map_widget(map_container, selected_value_reference)

        algorithms_container = tk.Frame(self)
        algorithms_container.grid(row=1, column=0, sticky='n', padx=21, pady=(10, 0))
        self._create_algo_buttons_widget(algorithms_container)

        # Set robot speed widget
        robot_speed_container = tk.Frame(self)
        robot_speed_container.grid(row=2, column=0, sticky='n', pady=(30, 0))
        self._create_robot_speed_widget(robot_speed_container)

        reset_button = tk.Button(self, text='Reset', command=self.reset_map)
        reset_button.grid(row=3,
                          column=0,
                          sticky='n',
                          padx=21,
                          pady=(100, 0),
                          ipadx=_BUTTON_INNER_PADDING_X * 17 + 3,
                          ipady=_BUTTON_INNER_PADDING_Y)

    def _create_load_map_widget(self, container, selected_value_reference):
        title_label = tk.Label(container, text='Choose Map:', font=_TITLE_FONT)
        title_label.grid(row=0, column=0, sticky='w', pady=5)

        option_menu = ttk.OptionMenu(container,
                                     selected_value_reference,
                                     _selection_values[0],
                                     *_selection_values)

        option_menu.config(width=_BASE_WIDTH_SIDEBAR)
        option_menu.grid(row=1, column=0, sticky='nw', padx=(0, 10), pady=(0, 10), ipadx=5, ipady=12)

        load_map_button = tk.Button(container,
                                    text='Load Map',
                                    command=lambda: self.arena_widget.load_map_from_disk(
                                        selected_value_reference.get(), self.a_star_solver))

        load_map_button.config(width=_BASE_BUTTON_WIDTH)
        load_map_button.grid(row=1, column=1, sticky='nw', ipadx=_BUTTON_INNER_PADDING_X, ipady=_BUTTON_INNER_PADDING_Y)

    def _create_algo_buttons_widget(self, container):
        title_label = tk.Label(container, text='Algorithms:', font=_TITLE_FONT)
        title_label.grid(row=0, column=0, sticky='w', pady=5)

        self._create_exploration_widget(container)
        self._create_fastest_path_widget(container)

    def _create_exploration_widget(self, container):
        exploration_button = tk.Button(container,
                                       text='Exploration',
                                       command=self._toggle_exploration_input_container_visibility)

        exploration_button.config(width=_BASE_BUTTON_WIDTH)
        exploration_button.grid(row=1,
                                column=0,
                                sticky='n',
                                padx=(0, 10),
                                pady=(0, 10),
                                ipadx=_BUTTON_INNER_PADDING_X,
                                ipady=_BUTTON_INNER_PADDING_Y)

        self.exploration_settings_container = tk.Frame(container)
        self._create_exploration_settings_widget()

    def _create_exploration_settings_widget(self):
        frame_label = tk.Label(self.exploration_settings_container, text='Exploration Settings:')
        frame_label.grid(row=0, column=0, sticky='w', pady=(0, 3))

        # checkbox to use exploration img
        checkbox = tk.Checkbutton(self.exploration_settings_container,
                                  text='Include Image Recognition',
                                  variable=self.use_image_rec,
                                  onvalue=True,
                                  offvalue=False)
        checkbox.grid(row=1, column=0, sticky='w')

        coverage_label = tk.Label(self.exploration_settings_container, text='Coverage:')
        coverage_label.grid(row=2, column=0, sticky='w', pady=5)
        coverage_progress_label = tk.Label(self.exploration_settings_container, text='0')  # replace with value from exp
        coverage_progress_label.grid(row=2, column=0, sticky='w', padx=(105, 0), pady=5)

        time_label = tk.Label(self.exploration_settings_container, text='Time:')
        time_label.grid(row=3, column=0, sticky='w', pady=5)
        time_progress_label = tk.Label(self.exploration_settings_container, text='00:00')  # replace with value from exp
        time_progress_label.grid(row=3, column=0, sticky='w', padx=(105, 0), pady=5)

        coverage_limit_label = tk.Label(self.exploration_settings_container, text='Coverage Limit:')
        coverage_limit_label.grid(row=4, column=0, sticky='w', pady=5)
        coverage_limit_input = tk.Entry(self.exploration_settings_container,
                                        textvariable=self._coverage_limit_input,
                                        width=15)
        self._coverage_limit_input.set(100)
        coverage_limit_input.grid(row=4, column=0, sticky='w', padx=(110, 20), pady=5)

        time_limit_label = tk.Label(self.exploration_settings_container, text='Time Limit:')
        time_limit_label.grid(row=5, column=0, sticky='w', pady=5)
        time_limit_input = tk.Entry(self.exploration_settings_container,
                                    textvariable=self._time_limit_input,
                                    width=15)
        self._time_limit_input.set('360')
        time_limit_input.grid(row=5, column=0, sticky='w', padx=(110, 0), pady=5)

        start_exploration_button = tk.Button(self.exploration_settings_container,
                                             text='Start Exploration',
                                             command=self._start_exploration)
        start_exploration_button.grid(row=6,
                                      column=0,
                                      sticky='ew',
                                      padx=(0, 10),
                                      pady=(20, 0),
                                      ipady=_BUTTON_INNER_PADDING_Y)

    def _toggle_exploration_input_container_visibility(self):
        if self._show_exploration_input:
            self.exploration_settings_container.grid_remove()
            self._show_exploration_input = False

            return

        self.exploration_settings_container.grid(row=2, column=0, sticky='n')  # add visibility toggle
        self._show_exploration_input = True

    def _start_exploration(self):
        pass

    def _create_fastest_path_widget(self, algorithms_container):
        fastest_path_button = tk.Button(algorithms_container,
                                        text='Fastest Path',
                                        command=self._toggle_waypoint_input_container_visibility)
        fastest_path_button.config(width=_BASE_BUTTON_WIDTH)
        fastest_path_button.grid(row=1,
                                 column=1,
                                 sticky='n',
                                 pady=(0, 10),
                                 ipadx=_BUTTON_INNER_PADDING_X,
                                 ipady=_BUTTON_INNER_PADDING_Y)

        self.waypoint_container = tk.Frame(algorithms_container)
        self._create_input_waypoint_widget()

    def _create_input_waypoint_widget(self):
        # Set row and column in the simulator in toggle method
        frame_label = tk.Label(self.waypoint_container, text='Enter waypoint')
        frame_label.grid(row=0, column=0, sticky='w', pady=(0, 3))

        x_label = tk.Label(self.waypoint_container, text='x:')
        x_label.grid(row=1, column=0, sticky='w')

        x_input_box = tk.Entry(self.waypoint_container, textvariable=self._waypoint_x_input)
        x_input_box.grid(row=1, column=0, sticky='w', padx=(25, 0), pady=(0, 5))

        y_label = tk.Label(self.waypoint_container, text='y:')
        y_label.grid(row=2, column=0, sticky='w', pady=10)

        y_input_box = tk.Entry(self.waypoint_container, textvariable=self._waypoint_y_input)
        y_input_box.grid(row=2, column=0, sticky='w', padx=(25, 0), pady=(5, 15))

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
        if self._show_waypoint_input:
            self.waypoint_container.grid_remove()
            self._show_waypoint_input = False

            return

        self.waypoint_container.grid(row=2, column=1, sticky='n')
        self._show_waypoint_input = True

    def _run_fastest_path_algorithm(self):
        if not self.way_point or self.algorithm_is_running:
            return

        start_point = ROBOT_START_POINT
        end_point = ROBOT_END_POINT

        path = self.a_star_solver.run_algorithm(start_point, self.way_point, end_point, Direction.NORTH)

        if not path:
            print_error_log('No fastest path found!')
            return

        self._display_result_on_canvas(path)
        self.algorithm_is_running = False

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

        action = path.pop(0)
        self.arena_widget.update_cell_on_map(action)
        self.arena_widget.after(100, self._display_result_on_canvas, path)

    def _create_robot_speed_widget(self, robot_speed_container):
        robot_speed_label = tk.Label(robot_speed_container, text='Robot Speed:')
        robot_speed_label.grid(row=0, column=0, sticky='w', padx=(0, 20))

        speed_input = tk.Entry(robot_speed_container,
                               textvariable=self._robot_speed_input,
                               width=15)
        speed_input.grid(row=0, column=1, sticky='w', padx=(0, 20))
        self._robot_speed_input.set(2)

        update_robot_speed_button = tk.Button(robot_speed_container,
                                              text='Update Speed')
        update_robot_speed_button.grid(row=0,
                                       column=2,
                                       sticky='ew',
                                       ipadx=_BUTTON_INNER_PADDING_X * 12,
                                       ipady=_BUTTON_INNER_PADDING_Y)

    def reset_map(self):
        self.arena_widget.reset_map()
        self._waypoint_x_input.set('')
        self._waypoint_y_input.set('')
