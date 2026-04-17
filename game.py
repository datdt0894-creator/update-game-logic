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

        # 2. Nếu có path → kiểm tra an toàn
        if path and len(path) > 0:
            if self._is_safe_path(path):
                next_head = path[0]
            else:
                next_head = self._follow_tail(ai_algorithm)
        else:
            # Không có đường → đi theo đuôi
            next_head = self._follow_tail(ai_algorithm)

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
    # 🔥 SMART LOGIC
    # =========================

    def _is_safe_path(self, path):
        """
        Giả lập đi theo path tới food,
        sau đó kiểm tra còn đường tới đuôi không
        """
        temp_body = self.snake.body.copy()

        for step in path:
            temp_body.insert(0, step)
            temp_body.pop()

        tail = temp_body[-1]

        from ai.bfs import BFS
        bfs = BFS()

        new_path, _ = bfs.get_path(temp_body[0], tail, temp_body, self.grid_size)

        return new_path is not None and len(new_path) > 0

    def _follow_tail(self, ai_algorithm):
        """
        Khi không an toàn → đi theo đuôi để sống lâu
        """
        head = self.snake.head()
        tail = self.snake.body[-1]

        path, _ = ai_algorithm.get_path(head, tail, self.snake.body, self.grid_size)

        if path and len(path) > 0:
            return path[0]

        return self._get_fallback_move()

    def _get_fallback_move(self):
        """
        Fallback cuối cùng: chọn ô có nhiều không gian nhất
        """
        head = self.snake.head()
        best_move = None
        max_free_spaces = -1

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = head[0] + dx, head[1] + dy

            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and (nx, ny) not in self.snake.body[:-1]:
                
                free_spaces = 0
                for ddx, ddy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nnx, nny = nx + ddx, ny + ddy
                    if 0 <= nnx < self.grid_size and 0 <= nny < self.grid_size and (nnx, nny) not in self.snake.body:
                        free_spaces += 1

                if free_spaces > max_free_spaces:
                    max_free_spaces = free_spaces
                    best_move = (nx, ny)

        return best_move