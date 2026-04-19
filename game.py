import time
import random
from snake import Snake
from food import Food

class GameLogic:
    def __init__(self, grid_size=20):
        self.grid_size = grid_size
        self.reset()

    def reset(self):
        self.snake = Snake((self.grid_size//2, self.grid_size//2))
        self.food = Food(self.grid_size)
        self.food.respawn(self.snake.body)

        self.score = 0
        self.steps = 0
        self.game_over = False

        self.current_path = []
        self.visited_nodes = []
        self.last_step_time = 0

        # 🔥 loop detect
        self.prev_heads = []
        self.loop_count = 0

    # =========================
    # MAIN STEP
    # =========================
    def step(self, ai_algorithm):
        if self.game_over:
            return

        start_time = time.time()

        head = self.snake.head()
        body = self.snake.body

        path, visited = ai_algorithm.get_path(
            head, self.food.position, body, self.grid_size
        )

        self.current_path = path
        self.visited_nodes = visited

        next_head = None

        # 🔥 detect loop
        self._update_loop_state(head)

        # =========================
        # LOGIC CHÍNH
        # =========================

        if path and len(path) > 0:

            # ✅ bình thường → ăn nếu an toàn
            if self._is_safe_path(path):
                next_head = path[0]

            else:
                # 🔥 nếu loop quá nhiều → ăn liều
                if self.loop_count > 10:
                    next_head = path[0]
                else:
                    next_head = self._survival_move(ai_algorithm)

        else:
            next_head = self._survival_move(ai_algorithm)

        self.last_step_time = time.time() - start_time

        if not next_head:
            self.game_over = True
            return

        self.snake.move(next_head)
        self.steps += 1

        if next_head == self.food.position:
            self.score += 10
            self.food.respawn(self.snake.body)

            # 🔥 reset loop khi ăn được
            self.loop_count = 0
            self.prev_heads.clear()

        else:
            self.snake.shrink()

    # =========================
    # LOOP DETECT
    # =========================
    def _update_loop_state(self, head):
        self.prev_heads.append(head)

        if len(self.prev_heads) > 30:
            self.prev_heads.pop(0)

        # đếm số lần lặp
        if self.prev_heads.count(head) > 3:
            self.loop_count += 1
        else:
            self.loop_count = max(0, self.loop_count - 1)

    # =========================
    # SAFE CHECK
    # =========================
    def _is_safe_path(self, path):
        temp_body = self.snake.body.copy()

        for step in path:
            temp_body.insert(0, step)
            if step != self.food.position:
                temp_body.pop()

        head = temp_body[0]
        tail = temp_body[-1]

        from ai.bfs import BFS
        bfs = BFS()

        path_to_tail, _ = bfs.get_path(
            head, tail, temp_body, self.grid_size
        )

        return path_to_tail is not None and len(path_to_tail) > 0

    # =========================
    # SURVIVAL
    # =========================
    def _survival_move(self, ai_algorithm):

        if len(self.snake.body) < (self.grid_size * self.grid_size) * 0.4:
            move = self._follow_tail(ai_algorithm)
            if move:
                return move

        return self._best_space_move()

    def _follow_tail(self, ai_algorithm):
        head = self.snake.head()
        tail = self.snake.body[-1]

        path, _ = ai_algorithm.get_path(
            head, tail, self.snake.body, self.grid_size
        )

        if path and len(path) > 0:
            return path[0]

        return None

    # =========================
    # SPACE CONTROL
    # =========================
    def _best_space_move(self):
        head = self.snake.head()
        best_move = None
        max_space = -1

        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = head[0] + dx, head[1] + dy

            if not self._is_valid(nx, ny):
                continue

            temp_body = self.snake.body.copy()
            temp_body.insert(0, (nx, ny))
            temp_body.pop()

            space = self._flood_fill((nx, ny), temp_body)

            if space > max_space:
                max_space = space
                best_move = (nx, ny)

        return best_move

    def _flood_fill(self, start, body):
        stack = [start]
        visited = set()
        body = set(body)

        count = 0

        while stack:
            x, y = stack.pop()

            if (x, y) in visited or (x, y) in body:
                continue

            if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
                continue

            visited.add((x, y))
            count += 1

            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                stack.append((x+dx, y+dy))

        return count

    # =========================
    # VALID MOVE
    # =========================
    def _is_valid(self, x, y):
        return (
            0 <= x < self.grid_size and
            0 <= y < self.grid_size and
            (x, y) not in self.snake.body[:-1]
        )