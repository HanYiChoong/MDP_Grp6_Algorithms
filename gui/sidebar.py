import tkinter as tk
from threading import Thread
from tkinter import ttk

from algorithms.exploration import Exploration
from algorithms.fastest_path_solver import AStarAlgorithm
from algorithms.image_recognition_exploration import ImageRecognitionExploration
from configs.gui_config import SAMPLE_ARENA_OPTIONS
from utils.constants import ROBOT_START_POINT, ROBOT_END_POINT
from utils.enums import Direction
from utils.logger import print_error_log

_selection_values = SAMPLE_ARENA_OPTIONS
_BASE_WIDTH_SIDEBAR = 25
_BUTTON_INNER_PADDING_X = 5
_BUTTON_INNER_PADDING_Y = 10
_BASE_BUTTON_WIDTH = _BASE_WIDTH_SIDEBAR + 3
_TITLE_FONT = ('Roboto bold', 12)
_DEFAULT_ROBOT_SPEED = 2
_DEFAULT_COVERAGE_LIMIT = 100
_DEFAULT_COVERAGE_LABEL_TEXT = '0%'
_DEFAULT_TIME_LIMIT = '360'
_DEFAULT_TIME_LIMIT_LABEL_TEXT = '0:00s'
_BUTTON_ACTIVE_STATE = 'active'
_BUTTON_NORMAL_STATE = 'normal'
_BUTTON_DISABLED_STATE = 'disable'


class Sidebar(tk.Frame):
    def __init__(self, parent, arena_widget, selected_value_reference, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)

        self.running_thread = None

        self.arena_widget = arena_widget
        self.exploration_algorithm = None
        self.fastest_path_solver = AStarAlgorithm(self.arena_widget.arena_map)

        self._waypoint_x_input: 'tk.StringVar' = tk.StringVar()
        self._waypoint_y_input: 'tk.StringVar' = tk.StringVar()
        self.way_point = None
        self._show_waypoint_input = False
        self.waypoint_container = None

        self.coverage_progress_label = None
        self._coverage_limit_input: 'tk.IntVar' = tk.IntVar()
        self.time_elapsed_label = None
        self._time_limit_input: 'tk.StringVar' = tk.StringVar()
        self._show_exploration_input = False
        self.exploration_settings_container = None
        self.use_image_rec: 'tk.BooleanVar' = tk.BooleanVar()
        self.stop_exploration_button = None
        self.reset_map_button = None

        self._robot_speed_input: 'tk.IntVar' = tk.IntVar()
        self._robot_speed_input.set(_DEFAULT_ROBOT_SPEED)
        self._convert_speed_to_canvas_repaint_delay_in_ms()

        map_container = tk.Frame(self)
        map_container.grid(row=0, column=0, sticky='n', padx=10, pady=(10, 20))
        self._create_load_map_widget(map_container, selected_value_reference)

        algorithms_container = tk.Frame(self)
        algorithms_container.grid(row=1, column=0, sticky='n', padx=21, pady=(10, 0))
        self._create_algo_buttons_widget(algorithms_container)

        robot_speed_container = tk.Frame(self)
        robot_speed_container.grid(row=2, column=0, sticky='n', pady=(30, 0))
        self._create_robot_speed_widget(robot_speed_container)

        self.log_message_text = tk.Label(self, text='', font=_TITLE_FONT)
        self.log_message_text.grid(row=3, column=0, sticky='n', pady=(50, 0))

        reset_container = tk.Frame(self)
        reset_container.grid(row=4, column=0, sticky='n')
        self._create_reset_map_container(reset_container)

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
                                    command=lambda: self._load_map_from_disk_to_arena(selected_value_reference))

        load_map_button.config(width=_BASE_BUTTON_WIDTH)
        load_map_button.grid(row=1, column=1, sticky='nw', ipadx=_BUTTON_INNER_PADDING_X, ipady=_BUTTON_INNER_PADDING_Y)

    def _load_map_from_disk_to_arena(self, selected_value_reference):
        generated_arena = self.arena_widget.load_map_from_disk(selected_value_reference.get())

        self.fastest_path_solver.arena = generated_arena

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
        # Set row and column in the simulator in toggle method
        frame_label = tk.Label(self.exploration_settings_container, text='Exploration Settings:')
        frame_label.grid(row=0, column=0, sticky='w', pady=(0, 3))

        checkbox = tk.Checkbutton(self.exploration_settings_container,
                                  text='Include Image Recognition',
                                  variable=self.use_image_rec,
                                  onvalue=True,
                                  offvalue=False)
        checkbox.grid(row=1, column=0, sticky='w')

        coverage_label = tk.Label(self.exploration_settings_container, text='Coverage:')
        coverage_label.grid(row=2, column=0, sticky='w', pady=5)
        self.coverage_progress_label = tk.Label(self.exploration_settings_container, text=_DEFAULT_COVERAGE_LABEL_TEXT)
        self.coverage_progress_label.grid(row=2, column=0, sticky='w', padx=(105, 0), pady=5)

        time_label = tk.Label(self.exploration_settings_container, text='Time elapsed:')
        time_label.grid(row=3, column=0, sticky='w', pady=5)
        self.time_elapsed_label = tk.Label(self.exploration_settings_container, text=_DEFAULT_TIME_LIMIT_LABEL_TEXT)
        self.time_elapsed_label.grid(row=3, column=0, sticky='w', padx=(105, 0), pady=5)

        coverage_limit_label = tk.Label(self.exploration_settings_container, text='Coverage Limit:')
        coverage_limit_label.grid(row=4, column=0, sticky='w', pady=5)
        coverage_limit_input = tk.Entry(self.exploration_settings_container,
                                        textvariable=self._coverage_limit_input,
                                        width=15)
        self._coverage_limit_input.set(_DEFAULT_COVERAGE_LIMIT)
        coverage_limit_input.grid(row=4, column=0, sticky='w', padx=(110, 20), pady=5)

        time_limit_label = tk.Label(self.exploration_settings_container, text='Time Limit:')
        time_limit_label.grid(row=5, column=0, sticky='w', pady=5)
        time_limit_input = tk.Entry(self.exploration_settings_container,
                                    textvariable=self._time_limit_input,
                                    width=15)
        self._time_limit_input.set(_DEFAULT_TIME_LIMIT)
        time_limit_input.grid(row=5, column=0, sticky='w', padx=(110, 0), pady=5)

        start_exploration_button = tk.Button(self.exploration_settings_container,
                                             text='Start Exploration',
                                             command=lambda: self.run_thread(self._start_exploration))
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

        self.exploration_settings_container.grid(row=2, column=0, sticky='n')
        self._show_exploration_input = True

    def _start_exploration(self):
        # add a check for any exploration running in another thread, add check for fastest path also
        exploration_map = self.arena_widget.map_reference.explored_map
        obstacle_map = self.arena_widget.map_reference.obstacle_map

        self.arena_widget.set_unexplored_arena_map()

        coverage_set = self._coverage_limit_input.get() / 100
        time_limit_set = float(self._time_limit_input.get())

        self.arena_widget.robot.on_move = self._update_robot_position_and_exploration_status_on_map

        exploration_algorithm_chosen = ImageRecognitionExploration if self.use_image_rec.get() else Exploration
        self.exploration_algorithm = exploration_algorithm_chosen(self.arena_widget.robot,
                                                                  exploration_map,
                                                                  obstacle_map,
                                                                  self._mark_sensed_area_as_explored,
                                                                  coverage_limit=coverage_set,
                                                                  time_limit=time_limit_set)

        self._set_button_state(self.stop_exploration_button, _BUTTON_ACTIVE_STATE)
        self._set_button_state(self.reset_map_button, _BUTTON_DISABLED_STATE)

        self.exploration_algorithm.start_exploration()
        self.arena_widget.map_reference.reset_exploration_maps()

        self._set_button_state(self.stop_exploration_button, _BUTTON_DISABLED_STATE)
        self._set_button_state(self.reset_map_button, _BUTTON_ACTIVE_STATE)

    def _update_robot_position_and_exploration_status_on_map(self, _):
        canvas_repaint_delay = self.arena_widget.canvas_repaint_delay_in_ms
        self.arena_widget.after(canvas_repaint_delay, self.arena_widget.update_robot_position_on_map)

        current_coverage = self.exploration_algorithm.coverage * 100
        self.update_coverage_progress_label_message(f'{current_coverage: .2f}%')

        elapsed_time = self.exploration_algorithm.time_elapsed
        self.update_time_elapsed_label_message(f'{elapsed_time // 60: .0f}:{elapsed_time % 60: .3f}s')

    def _mark_sensed_area_as_explored(self, point):
        canvas_repaint_delay = self.arena_widget.canvas_repaint_delay_in_ms
        self.arena_widget.after(canvas_repaint_delay, self.arena_widget.mark_sensed_area_as_explored_on_map, point)

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
        frame_label = tk.Label(self.waypoint_container, text='Enter waypoint:')
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
        if not self.way_point or self._exploration_is_running():
            print('exploration is running')
            return

        start_point = ROBOT_START_POINT
        end_point = ROBOT_END_POINT

        path = self.fastest_path_solver.run_algorithm(start_point, self.way_point, end_point, Direction.NORTH)

        if not path:
            print_error_log('No fastest path found!')
            return

        self._display_fastest_path_result_on_canvas(path)

    def _set_waypoint_on_arena(self):
        if self._waypoint_x_input.get() == '' or self._waypoint_y_input.get() == '':
            self.set_log_output_message('Enter way point!')
            return

        self.way_point = [int(self._waypoint_x_input.get()), int(self._waypoint_y_input.get())]

        if self.fastest_path_solver.is_not_within_range_with_virtual_wall(self.way_point):
            self.set_log_output_message('Not within valid range or point is on obstacle or virtual wall')
            return

        self.arena_widget.set_way_point(self.way_point)

    def _display_fastest_path_result_on_canvas(self, path):
        if len(path) <= 0:
            return

        action = path.pop(0)
        self.arena_widget.update_cell_on_map(action)

        canvas_repaint_delay = self.arena_widget.canvas_repaint_delay_in_ms
        self.arena_widget.after(canvas_repaint_delay, self._display_fastest_path_result_on_canvas, path)

    def _create_robot_speed_widget(self, robot_speed_container):
        robot_speed_label = tk.Label(robot_speed_container, text='Robot Speed:')
        robot_speed_label.grid(row=0, column=0, sticky='w', padx=(0, 20))

        speed_input = tk.Entry(robot_speed_container,
                               textvariable=self._robot_speed_input,
                               width=15)
        speed_input.grid(row=0, column=1, sticky='w', padx=(0, 20))

        update_robot_speed_button = tk.Button(robot_speed_container,
                                              text='Update movement speed',
                                              command=self._convert_speed_to_canvas_repaint_delay_in_ms)
        update_robot_speed_button.grid(row=0,
                                       column=2,
                                       sticky='ew',
                                       ipadx=_BUTTON_INNER_PADDING_X * 12,
                                       ipady=_BUTTON_INNER_PADDING_Y)

    def _create_reset_map_container(self, container):
        self.stop_exploration_button = tk.Button(container,
                                                 text='Stop Exploration',
                                                 command=self.stop_exploration_algorithm)
        self.stop_exploration_button.grid(row=0,
                                          column=0,
                                          sticky='n',
                                          padx=(0, 10),
                                          pady=(30, 0),
                                          ipadx=_BUTTON_INNER_PADDING_X * 13,
                                          ipady=_BUTTON_INNER_PADDING_Y)
        self._set_button_state(self.stop_exploration_button, _BUTTON_DISABLED_STATE)

        self.reset_map_button = tk.Button(container, text='Reset Map', command=self.reset_map)
        self.reset_map_button.grid(row=0,
                                   column=1,
                                   sticky='n',
                                   pady=(30, 0),
                                   ipadx=_BUTTON_INNER_PADDING_X * 15,
                                   ipady=_BUTTON_INNER_PADDING_Y)

    def _set_button_state(self, button_reference, state):
        if state != _BUTTON_ACTIVE_STATE and state != _BUTTON_DISABLED_STATE and state != _BUTTON_NORMAL_STATE:
            return

        button_reference.config(state=state)

    def _convert_speed_to_canvas_repaint_delay_in_ms(self):
        speed = self._robot_speed_input.get()

        if not (0 < speed <= 20) or not speed:
            return

        self.arena_widget.canvas_repaint_delay_in_ms = int(1 / speed * 1000)
        self.arena_widget.robot.sleep_interval = speed

    def set_log_output_message(self, message):
        self.log_message_text.config(text=message, fg='red')
        self.log_message_text.update()

    def update_coverage_progress_label_message(self, coverage_progress):
        self.coverage_progress_label.config(text=coverage_progress)
        self.coverage_progress_label.update()

    def update_time_elapsed_label_message(self, time_elapsed):
        self.time_elapsed_label.config(text=time_elapsed)
        self.time_elapsed_label.update()

    def run_thread(self, method):
        if self._exploration_is_running():
            return

        self.running_thread = Thread(target=method, daemon=True)
        self.running_thread.start()

    def _exploration_is_running(self):
        return self.running_thread is not None and self.running_thread.is_alive()

    def stop_exploration_algorithm(self):
        if not self.exploration_algorithm:
            return

        self.exploration_algorithm.is_running = False

    def reset_map(self):
        self.arena_widget.reset_map()
        self._waypoint_x_input.set('')
        self._waypoint_y_input.set('')
        self.set_log_output_message('')

        self._coverage_limit_input.set(_DEFAULT_COVERAGE_LIMIT)
        self.update_coverage_progress_label_message(_DEFAULT_COVERAGE_LABEL_TEXT)
        self._time_limit_input.set(_DEFAULT_TIME_LIMIT)
        self.update_time_elapsed_label_message(_DEFAULT_TIME_LIMIT_LABEL_TEXT)

        self._set_button_state(self.stop_exploration_button, _BUTTON_DISABLED_STATE)
