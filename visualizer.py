"""
Pygame Visualizer Module
========================
This module provides a graphical interface for the maze using pygame.

Key Features:
- Colorful grid display
- Animation support for path visualization
- Step-by-step algorithm state display
- Comparison dashboard
- Supports BFS, DFS, A*, and ACO
"""

import pygame
import time
import math

# Colors (RGB)
COLORS = {
    'background': (30, 30, 40),
    'empty': (60, 60, 80),
    'wall': (20, 20, 30),
    'start': (50, 205, 50),
    'exit': (255, 215, 0),
    'agent': (0, 150, 255),
    'enemy': (255, 60, 60),
    'path': (100, 200, 100),
    'explored': (80, 80, 120),
    'exploring': (150, 100, 200),
    'frontier': (255, 200, 100),
    'current': (255, 100, 255),
    'grid_line': (40, 40, 55),
    'text': (255, 255, 255),
    'bfs_path': (100, 180, 255),
    'dfs_path': (255, 180, 100),
    'astar_path': (100, 255, 150),
    'aco_path': (220, 120, 255),
    'panel_bg': (40, 40, 55),
    'panel_bg_2': (35, 35, 50),
    'panel_border': (60, 60, 80),
}


CELL_SIZE = 60
MARGIN = 2


class MazeVisualizer:
    """
    Pygame-based visualizer for the maze.
    """

    def __init__(self, maze, title="Maze Solver"):
        pygame.init()
        pygame.font.init()

        self.maze = maze

        self.width = maze.cols * CELL_SIZE + 240
        self.height = maze.rows * CELL_SIZE + 220

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(title)

        self.title_font = pygame.font.SysFont('arial', 28)
        self.info_font = pygame.font.SysFont('arial', 18)
        self.small_font = pygame.font.SysFont('arial', 14)

        self.agent_pos = maze.start
        self.enemy_pos = None
        self.path = []
        self.explored = set()

        self.stats = {
            'algorithm': 'None',
            'path_length': 0,
            'nodes_explored': 0,
            'status': 'Ready',
            'optimal_length': None,
        }

        self.comparison_results = None

        self.algo_step = None
        self.frontier_cells = []
        self.current_cell = None

        self.original_grid = [row[:] for row in maze.grid]
        self.walls_removed = False

        self.clock = pygame.time.Clock()

    def get_cell_rect(self, row, col):
        x = col * CELL_SIZE + MARGIN
        y = row * CELL_SIZE + 50 + MARGIN
        return pygame.Rect(x, y, CELL_SIZE - 2 * MARGIN, CELL_SIZE - 2 * MARGIN)

    def draw_cell(self, row, col, color, border_radius=5):
        rect = self.get_cell_rect(row, col)
        pygame.draw.rect(self.screen, color, rect, border_radius=border_radius)

    def draw_circle_in_cell(self, row, col, color, radius_ratio=0.35):
        rect = self.get_cell_rect(row, col)
        center = rect.center
        radius = int(CELL_SIZE * radius_ratio)
        pygame.draw.circle(self.screen, color, center, radius)
        highlight_pos = (center[0] - radius // 3, center[1] - radius // 3)
        pygame.draw.circle(self.screen, (255, 255, 255), highlight_pos, max(2, radius // 4))

    def draw_maze(self):
        from maze import WALL, START, EXIT

        for row in range(self.maze.rows):
            for col in range(self.maze.cols):
                cell_type = self.maze.grid[row][col]
                pos = (row, col)

                if self.current_cell and pos == self.current_cell:
                    color = COLORS['current']
                elif pos in self.frontier_cells:
                    color = COLORS['frontier']
                elif cell_type == WALL:
                    color = COLORS['wall']
                elif cell_type == START:
                    color = COLORS['start']
                elif cell_type == EXIT:
                    color = COLORS['exit']
                elif pos in self.explored:
                    color = COLORS['explored']
                else:
                    color = COLORS['empty']

                self.draw_cell(row, col, color)

                if cell_type == START:
                    self._draw_cell_label(row, col, "S")
                elif cell_type == EXIT:
                    self._draw_cell_label(row, col, "E")

                if pos in self.frontier_cells and cell_type not in (START, EXIT):
                    self._draw_cell_label(row, col, "?")

    def _draw_cell_label(self, row, col, text):
        rect = self.get_cell_rect(row, col)
        label = self.small_font.render(text, True, (0, 0, 0))
        label_rect = label.get_rect(topleft=(rect.left + 5, rect.top + 5))
        self.screen.blit(label, label_rect)

    def draw_path(self):
        for pos in self.path:
            if pos != self.maze.start and pos not in self.maze.exits:
                self.draw_cell(pos[0], pos[1], COLORS['path'])

    def draw_agent(self):
        if self.agent_pos:
            self.draw_circle_in_cell(self.agent_pos[0], self.agent_pos[1], COLORS['agent'])

    def draw_enemy(self):
        if self.enemy_pos:
            self.draw_circle_in_cell(self.enemy_pos[0], self.enemy_pos[1], COLORS['enemy'], radius_ratio=0.3)

    def draw_title(self):
        title = self.title_font.render("Maze Solver - Search Algorithms", True, COLORS['text'])
        title_rect = title.get_rect(midtop=(self.maze.cols * CELL_SIZE // 2, 10))
        self.screen.blit(title, title_rect)

    def draw_info_panel(self):
        panel_x = self.maze.cols * CELL_SIZE + 20
        panel_y = 60

        panel_rect = pygame.Rect(panel_x - 10, panel_y - 10, 200, 330)
        pygame.draw.rect(self.screen, COLORS['panel_bg'], panel_rect, border_radius=10)

        path_display = f"Path Length: {self.stats['path_length']}"
        if self.stats.get('optimal_length') is not None and self.stats['path_length'] > 0:
            opt = self.stats['optimal_length']
            if self.stats['path_length'] == opt:
                path_display += " (Optimal)"
            else:
                diff = self.stats['path_length'] - opt
                path_display += f" (+{diff})"

        lines = [
            f"Algorithm: {self.stats['algorithm']}",
            f"Status: {self.stats['status']}",
            "",
            path_display,
            f"Nodes Explored: {self.stats['nodes_explored']}",
            "",
            "Controls:",
            "  1/2/3/4 - BFS/DFS/A*/ACO",
            "  Shift+1/2/3/4 - Step Mode",
            "  C - Compare | N - New",
            "  W - Walls | R - Reset",
            "  Q - Quit",
        ]

        for i, line in enumerate(lines):
            text = self.info_font.render(line, True, COLORS['text'])
            self.screen.blit(text, (panel_x, panel_y + i * 25))

        legend_y = panel_y + len(lines) * 25 + 15
        self._draw_legend(panel_x, legend_y)

    def _draw_legend(self, x, y):
        legend_items = [
            (COLORS['start'], "Start"),
            (COLORS['exit'], "Exit"),
            (COLORS['agent'], "Agent"),
            (COLORS['path'], "Path"),
            (COLORS['frontier'], "Frontier"),
            (COLORS['current'], "Current"),
        ]

        for i, (color, label) in enumerate(legend_items):
            rect = pygame.Rect(x, y + i * 22, 15, 15)
            pygame.draw.rect(self.screen, color, rect, border_radius=3)
            text = self.small_font.render(label, True, COLORS['text'])
            self.screen.blit(text, (x + 22, y + i * 22))

    def set_comparison_results(self, results):
        self.comparison_results = results

    def set_algorithm_step(self, step):
        self.algo_step = step
        if step:
            self.current_cell = step.current_pos
            self.frontier_cells = step.frontier if step.frontier else []
            self.explored = step.explored if step.explored else set()
            self.path = step.path_so_far if step.path_so_far else []
            self.stats['nodes_explored'] = len(self.explored)
            self.stats['path_length'] = len(self.path) - 1 if self.path else 0
        else:
            self.current_cell = None
            self.frontier_cells = []

    def draw_algorithm_state(self):
        if not self.algo_step:
            return

        step = self.algo_step

        panel_x = 20
        panel_y = self.maze.rows * CELL_SIZE + 55
        panel_width = self.maze.cols * CELL_SIZE - 20
        panel_height = 140

        panel_rect = pygame.Rect(panel_x - 10, panel_y - 5, panel_width, panel_height)
        pygame.draw.rect(self.screen, COLORS['panel_bg_2'], panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, (80, 80, 120), panel_rect, width=2, border_radius=8)

        algo = self.stats.get('algorithm', 'BFS')

        if 'BFS' in algo:
            data_struct = 'QUEUE'
            struct_color = (100, 180, 255)
            pop_side = 'FRONT'
            push_side = 'BACK'
        elif 'DFS' in algo:
            data_struct = 'STACK'
            struct_color = (255, 180, 100)
            pop_side = 'TOP'
            push_side = 'TOP'
        elif 'A*' in algo:
            data_struct = 'PRIORITY QUEUE'
            struct_color = (100, 255, 150)
            pop_side = 'MIN f(n)'
            push_side = 'BY f(n)'
        else:
            data_struct = 'ANT FRONTIER / CANDIDATES'
            struct_color = COLORS['aco_path']
            pop_side = 'PROBABILISTIC'
            push_side = 'PHEROMONE-GUIDED'

        title = f"Step {step.step_num}: {algo} using {data_struct}"
        title_surface = self.info_font.render(title, True, struct_color)
        self.screen.blit(title_surface, (panel_x, panel_y))

        action_colors = {
            'start': (100, 255, 100),
            'pop': (255, 200, 100),
            'push': (100, 200, 255),
            'goal': (255, 215, 0),
            'fail': (255, 100, 100),
            'iteration': COLORS['aco_path'],
            'iteration_done': (200, 160, 255),
            'ant_start': (160, 200, 255),
            'move': (220, 180, 255),
            'ant_goal': (255, 215, 0),
            'ant_fail': (255, 120, 120),
            'dead_end': (255, 120, 120),
        }
        action_color = action_colors.get(step.action, COLORS['text'])
        msg_surface = self.small_font.render(step.message, True, action_color)
        self.screen.blit(msg_surface, (panel_x, panel_y + 25))

        curr_text = f"Current: {step.current_pos}" if step.current_pos else "Current: None"
        curr_surface = self.small_font.render(curr_text, True, COLORS['current'])
        self.screen.blit(curr_surface, (panel_x, panel_y + 45))

        ds_y = panel_y + 65
        ds_label = f"{data_struct}:"
        ds_surface = self.small_font.render(ds_label, True, (180, 180, 180))
        self.screen.blit(ds_surface, (panel_x, ds_y))

        box_y = ds_y + 18
        box_size = 28
        box_margin = 3
        max_boxes = min(12, len(step.frontier) if step.frontier else 0)

        if 'STACK' in data_struct:
            bracket_text = "TOP→" if step.frontier else "[empty]"
        elif 'ANT' in data_struct:
            bracket_text = "Choices→" if step.frontier else "[none]"
        else:
            bracket_text = f"[{pop_side}→" if step.frontier else "[empty]"

        bracket_surface = self.small_font.render(bracket_text, True, struct_color)
        self.screen.blit(bracket_surface, (panel_x, box_y + 5))

        start_x = panel_x + 60

        for i in range(max_boxes):
            pos = step.frontier[i] if i < len(step.frontier) else None
            if pos:
                box_rect = pygame.Rect(
                    start_x + i * (box_size + box_margin),
                    box_y,
                    box_size,
                    box_size
                )
                if i == 0:
                    pygame.draw.rect(self.screen, COLORS['current'], box_rect, border_radius=4)
                else:
                    pygame.draw.rect(self.screen, struct_color, box_rect, border_radius=4)

                pygame.draw.rect(self.screen, (255, 255, 255), box_rect, width=1, border_radius=4)

                pos_text = f"{pos[0]},{pos[1]}"
                pos_surface = self.small_font.render(pos_text, True, (0, 0, 0))
                text_rect = pos_surface.get_rect(center=box_rect.center)
                self.screen.blit(pos_surface, text_rect)

        if step.frontier and len(step.frontier) > max_boxes:
            more_text = f"...+{len(step.frontier) - max_boxes} more"
            more_surface = self.small_font.render(more_text, True, (150, 150, 150))
            self.screen.blit(
                more_surface,
                (start_x + max_boxes * (box_size + box_margin) + 5, box_y + 5)
            )

        stats_y = box_y + box_size + 8
        stats_text = (
            f"Explored: {len(step.explored)} | "
            f"Frontier/Choices: {len(step.frontier) if step.frontier else 0} | "
            f"Path so far: {len(step.path_so_far) - 1 if step.path_so_far else 0} steps"
        )
        stats_surface = self.small_font.render(stats_text, True, (150, 150, 150))
        self.screen.blit(stats_surface, (panel_x, stats_y))

        legend_y = stats_y + 18
        legend_items = [
            (COLORS['current'], "Current"),
            (COLORS['frontier'], "Frontier/Choices"),
            (COLORS['explored'], "Explored"),
        ]
        legend_x = panel_x
        for color, label in legend_items:
            pygame.draw.rect(self.screen, color, (legend_x, legend_y, 12, 12), border_radius=2)
            label_surface = self.small_font.render(label, True, (150, 150, 150))
            self.screen.blit(label_surface, (legend_x + 16, legend_y - 2))
            legend_x += 120

    def draw_comparison_panel(self):
        if not self.comparison_results:
            return

        panel_x = 20
        panel_y = self.maze.rows * CELL_SIZE + 55
        panel_width = self.maze.cols * CELL_SIZE - 20
        panel_height = 145

        panel_rect = pygame.Rect(panel_x - 10, panel_y - 10, panel_width, panel_height)
        pygame.draw.rect(self.screen, COLORS['panel_bg_2'], panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLORS['panel_border'], panel_rect, width=2, border_radius=8)

        title = self.info_font.render("ALGORITHM COMPARISON", True, (255, 215, 0))
        title_rect = title.get_rect(midtop=(panel_x + panel_width // 2 - 10, panel_y - 5))
        self.screen.blit(title, title_rect)

        headers = [
            "Algorithm",
            "Path",
            "Nodes",
            "Time",
            "Score",
        ]
        col_widths = [90, 70, 85, 85, 70]
        header_y = panel_y + 25

        header_rect = pygame.Rect(panel_x - 5, header_y - 5, sum(col_widths) + 20, 24)
        pygame.draw.rect(self.screen, (50, 50, 70), header_rect, border_radius=4)

        x = panel_x
        for i, header in enumerate(headers):
            text = self.small_font.render(header, True, (180, 180, 200))
            self.screen.blit(text, (x, header_y))
            x += col_widths[i]

        algo_info = {
            'BFS': {'color': COLORS['bfs_path']},
            'DFS': {'color': COLORS['dfs_path']},
            'A*': {'color': COLORS['astar_path']},
            'ACO': {'color': COLORS['aco_path']},
        }

        successful = {k: v for k, v in self.comparison_results.items() if v['success']}
        if successful:
            best_path = min(v['path_length'] for v in successful.values())
            best_nodes = min(v['nodes_expanded'] for v in successful.values())
            best_time = min(v['time_ms'] for v in successful.values())
            best_reward = max(v.get('reward', 0) for v in successful.values())
        else:
            best_path = best_nodes = best_time = best_reward = 0

        row_y = header_y + 28
        display_order = ['BFS', 'DFS', 'A*', 'ACO']

        for algo_name in display_order:
            if algo_name not in self.comparison_results:
                continue

            data = self.comparison_results[algo_name]
            info = algo_info.get(algo_name, {'color': (150, 150, 150)})

            row_rect = pygame.Rect(panel_x - 5, row_y - 3, sum(col_widths) + 20, 22)
            row_bg = (*info['color'][:3], 30)
            surface = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
            surface.fill(row_bg)
            self.screen.blit(surface, row_rect.topleft)
            pygame.draw.rect(self.screen, (*info['color'][:3], 100), row_rect, width=1, border_radius=3)

            x = panel_x
            pygame.draw.circle(self.screen, info['color'], (x + 5, row_y + 7), 4)
            text = self.small_font.render(algo_name, True, info['color'])
            self.screen.blit(text, (x + 14, row_y))
            x += col_widths[0]

            if data['success']:
                is_best_path = data['path_length'] == best_path
                path_color = (0, 255, 100) if is_best_path else COLORS['text']
                path_str = f"{data['path_length']}" + (" *" if is_best_path else "")
                text = self.small_font.render(path_str, True, path_color)
                self.screen.blit(text, (x, row_y))
                x += col_widths[1]

                is_best_nodes = data['nodes_expanded'] == best_nodes
                nodes_color = (0, 255, 100) if is_best_nodes else COLORS['text']
                nodes_str = f"{data['nodes_expanded']}" + (" *" if is_best_nodes else "")
                text = self.small_font.render(nodes_str, True, nodes_color)
                self.screen.blit(text, (x, row_y))
                x += col_widths[2]

                is_best_time = abs(data['time_ms'] - best_time) < 0.01
                time_color = (0, 255, 100) if is_best_time else COLORS['text']
                time_str = f"{data['time_ms']:.2f}ms" + (" *" if is_best_time else "")
                text = self.small_font.render(time_str, True, time_color)
                self.screen.blit(text, (x, row_y))
                x += col_widths[3]

                reward = data.get('reward', 0)
                is_best_reward = reward == best_reward and reward > 0
                reward_color = (0, 255, 100) if is_best_reward else COLORS['text']
                reward_str = f"{reward:.0f}" + (" *" if is_best_reward else "")
                text = self.small_font.render(reward_str, True, reward_color)
                self.screen.blit(text, (x, row_y))
            else:
                fail_text = self.small_font.render("FAILED - No path", True, (255, 80, 80))
                self.screen.blit(fail_text, (x, row_y))

            row_y += 24

        if successful:
            row_y += 5
            winner = max(successful.items(), key=lambda x: x[1].get('reward', 0))[0]
            winner_info = algo_info.get(winner, {'color': (255, 255, 255)})

            winner_text = f"WINNER: {winner}"
            winner_surface = self.info_font.render(winner_text, True, winner_info['color'])

            trophy_x = panel_x
            pygame.draw.polygon(self.screen, (255, 215, 0), [
                (trophy_x + 5, row_y + 2),
                (trophy_x + 15, row_y + 2),
                (trophy_x + 13, row_y + 10),
                (trophy_x + 7, row_y + 10),
            ])
            pygame.draw.rect(self.screen, (255, 215, 0), (trophy_x + 8, row_y + 10, 4, 4))

            self.screen.blit(winner_surface, (trophy_x + 22, row_y))

            reason = []
            winner_data = successful[winner]
            if winner_data['path_length'] == best_path:
                reason.append("shortest path")
            if winner_data['nodes_expanded'] == best_nodes:
                reason.append("fewest nodes")
            if winner_data.get('reward', 0) == best_reward:
                reason.append("best score")

            if reason:
                reason_text = f"({', '.join(reason)})"
                reason_surface = self.small_font.render(reason_text, True, (150, 150, 150))
                self.screen.blit(reason_surface, (trophy_x + 130, row_y + 3))

    def update(self):
        self.screen.fill(COLORS['background'])

        self.draw_title()
        self.draw_maze()
        self.draw_path()
        self.draw_enemy()
        self.draw_agent()
        self.draw_info_panel()

        if self.algo_step:
            self.draw_algorithm_state()
        elif self.comparison_results:
            self.draw_comparison_panel()

        pygame.display.flip()
        self.clock.tick(60)

    def handle_events(self):
        """
        Returns:
            str or None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'q'
            elif event.type == pygame.KEYDOWN:
                mods = pygame.key.get_mods()
                shift_held = mods & pygame.KMOD_SHIFT

                if event.key == pygame.K_1:
                    return '!' if shift_held else '1'
                elif event.key == pygame.K_2:
                    return '@' if shift_held else '2'
                elif event.key == pygame.K_3:
                    return '#' if shift_held else '3'
                elif event.key == pygame.K_4:
                    return '$' if shift_held else '4'
                elif event.key == pygame.K_r:
                    return 'r'
                elif event.key == pygame.K_q:
                    return 'q'
                elif event.key == pygame.K_c:
                    return 'c'
                elif event.key == pygame.K_n:
                    return 'n'
                elif event.key == pygame.K_w:
                    return 'w'
                elif event.key == pygame.K_SPACE:
                    return ' '
                elif event.key == pygame.K_f:
                    return 'f'
                elif event.key == pygame.K_s:
                    return 's'
        return None

    def set_agent_position(self, pos):
        self.agent_pos = pos

    def set_enemy_position(self, pos):
        self.enemy_pos = pos

    def set_path(self, path):
        self.path = path if path else []
        self.stats['path_length'] = len(self.path) - 1 if self.path else 0

    def add_explored(self, pos):
        self.explored.add(pos)
        self.stats['nodes_explored'] = len(self.explored)

    def set_explored(self, explored_set):
        self.explored = set(explored_set) if explored_set else set()
        self.stats['nodes_explored'] = len(self.explored)

    def reset(self):
        self.agent_pos = self.maze.start
        self.enemy_pos = None
        self.path = []
        self.explored = set()
        self.stats = {
            'algorithm': 'None',
            'path_length': 0,
            'nodes_explored': 0,
            'status': 'Ready',
            'optimal_length': None,
        }
        self.comparison_results = None
        self.algo_step = None
        self.frontier_cells = []
        self.current_cell = None

    def toggle_walls(self):
        from maze import WALL, EMPTY

        if self.walls_removed:
            self.maze.grid = [row[:] for row in self.original_grid]
            self.walls_removed = False
            return "Walls: ON"
        else:
            for r in range(self.maze.rows):
                for c in range(self.maze.cols):
                    if self.maze.grid[r][c] == WALL:
                        self.maze.grid[r][c] = EMPTY
            self.walls_removed = True
            return "Walls: OFF"

    def animate_path(self, path, delay=0.1, enemy=None):
        for t, pos in enumerate(path):
            event = self.handle_events()
            if event == 'q':
                return
            elif event == 'r':
                return

            self.set_agent_position(pos)

            if enemy:
                self.set_enemy_position(enemy.get_position(t))

            self.update()
            time.sleep(delay)

    def animate_exploration(self, explored_positions, delay=0.02):
        explored_list = list(explored_positions)
        current_explored = set()

        for pos in explored_list:
            event = self.handle_events()
            if event in ('q', 'r'):
                return False

            current_explored.add(pos)
            self.explored = current_explored
            self.stats['nodes_explored'] = len(current_explored)
            self.update()
            time.sleep(delay)

        return True

    def animate_path_drawing(self, path, delay=0.05, color=None):
        for i in range(len(path)):
            event = self.handle_events()
            if event in ('q', 'r'):
                return False

            self.path = path[:i + 1]
            self.update()
            time.sleep(delay)

        return True

    def draw_multiple_paths(self, paths_dict):
        algo_colors = {
            'BFS': COLORS['bfs_path'],
            'DFS': COLORS['dfs_path'],
            'A*': COLORS['astar_path'],
            'ACO': COLORS['aco_path'],
        }

        for algo_name, path in paths_dict.items():
            if not path:
                continue

            color = algo_colors.get(algo_name, COLORS['path'])
            offset = {'BFS': -4, 'DFS': -1, 'A*': 2, 'ACO': 5}.get(algo_name, 0)

            for pos in path:
                if pos != self.maze.start and pos not in self.maze.exits:
                    rect = self.get_cell_rect(pos[0], pos[1])
                    path_rect = pygame.Rect(
                        rect.left + 10 + offset,
                        rect.top + 10 + offset,
                        max(8, rect.width - 22),
                        max(8, rect.height - 22)
                    )
                    pygame.draw.rect(self.screen, color, path_rect, border_radius=8)

    def pulse_cell(self, row, col, color, pulses=3, duration=0.3):
        frames = 20
        for _pulse in range(pulses):
            for frame in range(frames):
                intensity = (math.sin(frame / frames * math.pi * 2) + 1) / 2
                pulse_color = tuple(
                    int(c + (255 - c) * intensity * 0.5) for c in color[:3]
                )
                self.draw_cell(row, col, pulse_color)
                pygame.display.flip()
                time.sleep(duration / (pulses * frames))

    def close(self):
        pygame.quit()


if __name__ == "__main__":
        from maze import Maze

        maze = Maze()
        viz = MazeVisualizer(maze)

        test_path = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4)]

        print("Maze Visualizer Test")
        print("Press 1, 2, 3, 4 to select algorithm")
        print("Press R to reset, Q to quit")

        running = True
        while running:
            key = viz.handle_events()

            if key == 'q':
                running = False
            elif key == 'r':
                viz.reset()
            elif key == '1':
                viz.stats['algorithm'] = 'BFS'
                viz.stats['status'] = 'Running...'
                viz.set_path(test_path)
                viz.set_explored({(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)})
                viz.animate_path(test_path, delay=0.2)
                viz.stats['status'] = 'Complete'
            elif key == '4':
                viz.stats['algorithm'] = 'ACO'
                viz.stats['status'] = 'Running...'
                viz.set_path(test_path)
                viz.set_explored({(0, 0), (0, 1), (1, 2), (2, 2), (2, 3)})
                viz.animate_path(test_path, delay=0.2)
                viz.stats['status'] = 'Complete'

            viz.update()

        viz.close()
