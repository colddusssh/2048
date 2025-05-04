import os
import sys
import time
import random
from collections import namedtuple
from colorama import init, Fore, Back, Style

# Инициализация colorama
init()

# Определяем структуру для хранения информации о блоке
Point = namedtuple('Point', ['x', 'y'])
Block = namedtuple('Block', ['shape', 'color'])

# Конфигурация игры
WIDTH = 10
HEIGHT = 20
EMPTY = ' '

# Цвета для блоков (используем colorama)
COLORS = {
    'cyan': Fore.CYAN,
    'blue': Fore.BLUE,
    'orange': Fore.YELLOW,
    'yellow': Fore.LIGHTYELLOW_EX,
    'green': Fore.GREEN,
    'purple': Fore.MAGENTA,
    'red': Fore.RED,
    'reset': Fore.RESET
}

# Фигуры тетрамино
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]]   # Z
]

# Цвета для фигур
SHAPE_COLORS = ['cyan', 'yellow', 'purple', 'orange', 'blue', 'green', 'red']

# Клавиши управления
if os.name == 'nt':
    import msvcrt
    KEY_MAPPING = {
        b'a': 'left',
        b'd': 'right',
        b's': 'down',
        b'w': 'rotate',
        b' ': 'drop',
        b'q': 'quit'
    }
else:
    import termios
    import tty
    KEY_MAPPING = {
        'a': 'left',
        'd': 'right',
        's': 'down',
        'w': 'rotate',
        ' ': 'drop',
        'q': 'quit'
    }

class Tetris:
    def __init__(self):
        self.board = [[EMPTY for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.current_piece = None
        self.current_pos = None
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.next_piece = self._generate_piece()
        self._spawn_piece()
        
    def _generate_piece(self):
        shape_idx = random.randint(0, len(SHAPES) - 1)
        shape = SHAPES[shape_idx]
        color = SHAPE_COLORS[shape_idx]
        return Block(shape=shape, color=color)
    
    def _spawn_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = self._generate_piece()
        self.current_pos = Point(x=WIDTH // 2 - len(self.current_piece.shape[0]) // 2, y=0)
        
        # Проверка на проигрыш
        if self._check_collision(self.current_pos):
            self.game_over = True
    
    def _check_collision(self, pos):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    board_x = pos.x + x
                    board_y = pos.y + y
                    
                    if (board_x < 0 or board_x >= WIDTH or 
                        board_y >= HEIGHT or 
                        (board_y >= 0 and self.board[board_y][board_x] != EMPTY)):
                        return True
        return False
    
    def _rotate_piece(self):
        # Транспонирование матрицы с последующим обращением строк (поворот на 90 градусов)
        rotated = [list(row) for row in zip(*self.current_piece.shape[::-1])]
        old_shape = self.current_piece.shape
        self.current_piece = Block(shape=rotated, color=self.current_piece.color)
        
        if self._check_collision(self.current_pos):
            self.current_piece = Block(shape=old_shape, color=self.current_piece.color)
            return False
        return True
    
    def _move(self, dx, dy):
        new_pos = Point(x=self.current_pos.x + dx, y=self.current_pos.y + dy)
        
        if not self._check_collision(new_pos):
            self.current_pos = new_pos
            return True
        return False
    
    def _merge_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    board_y = self.current_pos.y + y
                    board_x = self.current_pos.x + x
                    if 0 <= board_y < HEIGHT and 0 <= board_x < WIDTH:
                        self.board[board_y][board_x] = self.current_piece.color
    
    def _clear_lines(self):
        new_board = [row for row in self.board if any(cell == EMPTY for cell in row)]
        lines_cleared = HEIGHT - len(new_board)
        
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            self.score += [100, 300, 500, 800][min(lines_cleared - 1, 3)] * self.level
            self.level = self.lines_cleared // 10 + 1
            
            # Добавляем новые пустые строки вверх
            for _ in range(lines_cleared):
                new_board.insert(0, [EMPTY for _ in range(WIDTH)])
            
            self.board = new_board
    
    def update(self, action):
        if self.game_over:
            return False
        
        moved = False
        
        if action == 'left':
            moved = self._move(-1, 0)
        elif action == 'right':
            moved = self._move(1, 0)
        elif action == 'down':
            moved = self._move(0, 1)
        elif action == 'rotate':
            moved = self._rotate_piece()
        elif action == 'drop':
            while self._move(0, 1):
                moved = True
            self._merge_piece()
            self._clear_lines()
            self._spawn_piece()
            return True
        
        # Автоматическое падение
        if not moved and action == 'down':
            self._merge_piece()
            self._clear_lines()
            self._spawn_piece()
        
        return moved
    
    def draw(self):
        # Очистка экрана
        print('\033[H\033[J', end='')
        
        # Рисуем границы и игровое поле
        board_copy = [row.copy() for row in self.board]
        
        # Добавляем текущую фигуру на копию доски для отрисовки
        if not self.game_over:
            for y, row in enumerate(self.current_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        board_y = self.current_pos.y + y
                        board_x = self.current_pos.x + x
                        if 0 <= board_y < HEIGHT and 0 <= board_x < WIDTH:
                            board_copy[board_y][board_x] = self.current_piece.color
        
        # Верхняя граница
        print('+' + '-' * (WIDTH * 2 + 1) + '+')
        
        # Игровое поле
        for y, row in enumerate(board_copy):
            line = '| '
            for cell in row:
                if cell in COLORS:
                    line += COLORS[cell] + '■' + Fore.RESET + ' '
                else:
                    line += EMPTY + ' '
            line += '|'
            
            # Отображение следующей фигуры справа от поля
            if y == 1:
                line += '   Next:'
            elif 2 <= y < 2 + len(self.next_piece.shape):
                next_line = '   '
                for x in range(4):
                    if (y - 2 < len(self.next_piece.shape) and 
                        x < len(self.next_piece.shape[0]) and 
                        self.next_piece.shape[y - 2][x]):
                        next_line += COLORS[self.next_piece.color] + '■' + Fore.RESET + ' '
                    else:
                        next_line += '  '
                line += next_line
            
            print(line)
        
        # Нижняя граница
        print('+' + '-' * (WIDTH * 2 + 1) + '+')
        
        # Информация о игре
        print(f"Score: {self.score} | Level: {self.level} | Lines: {self.lines_cleared}")
        print("Controls: A - left, D - right, S - down, W - rotate, SPACE - drop, Q - quit")
        
        if self.game_over:
            print("\nGAME OVER!")
            print(f"Final Score: {self.score}")

def get_key():
    if os.name == 'nt':
        # Windows (msvcrt)
        if msvcrt.kbhit():
            key = msvcrt.getch().lower()
            return KEY_MAPPING.get(key, None)
    else:
        # Linux/Mac (termios, tty)
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1).lower()
            if ch in KEY_MAPPING:
                return KEY_MAPPING[ch]
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return None

def main():
    game = Tetris()
    last_drop_time = time.time()
    drop_interval = 1.0  # Начальный интервал падения (уменьшается с уровнем)
    
    print('\033[H\033[J', end='')  # Очистка экрана
    print("Тетрис - готовы начать? (Нажмите любую клавишу управления)")
    
    while not game.game_over:
        current_time = time.time()
        
        # Обработка ввода
        action = get_key()
        if action == 'quit':
            break
        
        if action is not None:
            game.update(action)
            game.draw()
        
        # Автоматическое падение
        if current_time - last_drop_time > drop_interval / game.level:
            game.update('down')
            game.draw()
            last_drop_time = current_time
        
        time.sleep(0.01)
    
    # Ожидание перед выходом
    if game.game_over:
        time.sleep(3)

if __name__ == "__main__":
    main()