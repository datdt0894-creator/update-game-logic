import time
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

    def step(self, ai_algorithm):
        if self.game_over:
            return

        start_time = time.time()

        head = self.snake.head()
        body = self.snake.body

        # 1. Tìm đường tới food
        path, visited = ai_algorithm.get_path(head, self.food.position, body, self.grid_size)
        self.current_path = path
        self.visited_nodes = visited

        next_head = None

        # 2. Ưu tiên ăn nếu AN TOÀN
        if path and len(path) > 0:
            if self._is_safe_path(path):
                next_head = path[0]
            else:
                # Không an toàn → tìm đường sống
                next_head = self._survival_move(ai_algorithm)
        else:
            # Không có đường → sinh tồn
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
        else:
            self.snake.shrink()

    # =========================
    # 🔥 CORE AI LOGIC
    # =========================

    def _is_safe_path(self, path):
        """Check: ăn xong có còn đường sống không"""
        temp_body = self.snake.body.copy()

        for step in path:
            temp_body.insert(0, step)
            temp_body.pop()

        tail = temp_body[-1]

        from ai.bfs import BFS
        bfs = BFS()

        new_path, _ = bfs.get_path(temp_body[0], tail, temp_body, self.grid_size)

        return new_path is not None and len(new_path) > 0

    def _survival_move(self, ai_algorithm):
        """
        Logic sinh tồn nâng cao:
        1. Follow tail
        2. Nếu không được → chọn ô có nhiều không gian nhất
        """

        move = self._follow_tail(ai_algorithm)
        if move:
            return move

        return self._get_best_safe_move()

    def _follow_tail(self, ai_algorithm):
        """Đi theo đuôi để không bị kẹt"""
        head = self.snake.head()
        tail = self.snake.body[-1]

        path, _ = ai_algorithm.get_path(head, tail, self.snake.body, self.grid_size)

        if path and len(path) > 0:
            return path[0]

        return None

    def _get_best_safe_move(self):
        """
        Chọn bước có KHÔNG GIAN LỚN NHẤT (flood fill)
        """
        head = self.snake.head()
        best_move = None
        max_space = -1

        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            nx, ny = head[0] + dx, head[1] + dy

            if not self._is_valid(nx, ny):
                continue

            space = self._flood_fill((nx, ny))

            if space > max_space:
                max_space = space
                best_move = (nx, ny)

        return best_move

    def _flood_fill(self, start):
        """Đếm số ô trống có thể đi (rất quan trọng)"""
        stack = [start]
        visited = set()
        body = set(self.snake.body)

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

    def _is_valid(self, x, y):
        return (
            0 <= x < self.grid_size and
            0 <= y < self.grid_size and
            (x, y) not in self.snake.body[:-1]
        )