import random
import time
import os

try:
    from colorama import init, Fore, Back, Style
    
except Exception:
    from libs.colorama import init, Fore, Back, Style


init()

Back.GRAY = "\033[48;5;243m"  
Back.LIGHT_GRAY = "\033[48;5;247m"
Back.CORAL = "\033[48;5;203m"
Back.PURPLE = "\033[48;5;93m"
Back.ORANGE = "\033[48;5;208m"
Back.CORAL = "\033[48;5;209m"

colors = {
    0: Back.GRAY,
    2: Back.RED,
    4: Back.GREEN,
    8: Back.YELLOW,
    16: Back.BLUE,
    32: Back.MAGENTA,
    64: Back.CYAN,
    128: Back.LIGHT_GRAY,
    256: Back.CORAL,
    512: Back.PURPLE,
    1024: Back.ORANGE,
    2048: Back.CORAL
    }

SIZE = 4

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def f(num):
    if num == 0:
        return "."
    return str(num)

def newGame():
    global score
    
    board = [[0] * SIZE for i in range(SIZE)]
    score = 0
    addNewTile(board)
    addNewTile(board)
    return board

def addNewTile(board):
    empty = [(i, j) for i in range(SIZE) for j in range(SIZE) if board[i][j] == 0]
    if not empty:
        return
    i, j = random.choice(empty)
    board[i][j] = 4 if random.randint(0, 9) == 0 else 2

def printBoard(board):
    clear()
    
    print(f"{Style.BRIGHT}{'2048'.ljust(7 * SIZE - len(f'{score} pts'))}{score} pts")
    print()
    
    for row in board:
        
        for num in row:
            currColor = colors.get(num, Back.WHITE)
            print(f"{currColor}{' ' * 7}{Style.RESET_ALL}", end = "")
        print()
        
        for num in row:
            currColor = colors.get(num, Back.WHITE)
            print(f"{currColor}{f(num).center(7)}{Style.RESET_ALL}", end = "")
        print()
            
        for num in row:
            currColor = colors.get(num, Back.WHITE)
            print(f"{currColor}{' ' * 7}{Style.RESET_ALL}", end = "")
        print()
    print()
    print("        ←,↑,→,↓ or q")

def leftSlide(row):
    global score
    
    newRow = [i for i in row if i != 0]
    for i in range(len(newRow) - 1):
        if newRow[i] == newRow[i + 1]:
            newRow[i] *= 2
            score += newRow[i]
            newRow[i + 1] = 0
    newRow = [i for i in newRow if i != 0]
    return newRow + [0] * (len(row) - len(newRow))

def moveLeft(board):
    moved = False
    newBoard = []

    for row in board:
        newRow = leftSlide(row)
        
        if newRow != row:
            moved = True
            
        newBoard.append(newRow)
        
    return newBoard, moved

def moveRight(board):
    reversedBoard = [list(reversed(row)) for row in board]
    newBoard, moved = moveLeft(reversedBoard)
    newBoard = [list(reversed(row)) for row in newBoard]
    return newBoard, moved

def transpose(board):
    return [list(row) for row in zip(*board)]

def moveUp(board):
    transposed = transpose(board)
    newBoard, moved = moveLeft(transposed)
    newBoard = transpose(newBoard)
    return newBoard, moved

def moveDown(board):
    transposed = transpose(board)
    newBoard, moved = moveRight(transposed)
    newBoard = transpose(newBoard)
    return newBoard, moved

def checkWin(board):
    return any(2048 in row for row in board)

def getKey():
    if os.name == 'nt':  # Windows
        import msvcrt
        while True:
            key = msvcrt.getch()
            if key == b'q':
                return 'q'
            elif key == b'H':
                return 'up'
            elif key == b'P':
                return 'down'
            elif key == b'K':
                return 'left'
            elif key == b'M':
                return 'right'
    else:  # Linux/Mac
        import sys
        import tty
        import termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ch == '\x1b': 
                ch = sys.stdin.read(1)
                if ch == '[':
                    ch = sys.stdin.read(1)
                    if ch == 'A':
                        return 'up'
                    elif ch == 'B':
                        return 'down'
                    elif ch == 'C':
                        return 'right'
                    elif ch == 'D':
                        return 'left'
            elif ch == 'q':
                return 'q'
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None

def canMove(board):
    for i in range(SIZE):
        for j in range(SIZE):
            if board[i][j] == 0:
                return True
            if i < SIZE-1 and board[i][j] == board[i+1][j]:
                return True
            if j < SIZE-1 and board[i][j] == board[i][j+1]:
                return True
    return False

def main():
    board = newGame()
    printBoard(board)
    
    while True:
        key = getKey()
        
        moved = False
        
        if key == 'up':
            board, moved = moveUp(board)
        elif key == 'down':
            board, moved = moveDown(board)
        elif key == 'left':
            board, moved = moveLeft(board)
        elif key == 'right':
            board, moved = moveRight(board)
        elif key == 'q':
            print(f"{Fore.YELLOW}{Style.BRIGHT}You left the game.")
            break
        
        if moved:
            addNewTile(board)
            printBoard(board)
            if checkWin(board):
                print(f"{Fore.GREEN}{Style.BRIGHT}Winner winner chicken dinner!")
                break
            if not canMove(board):
                print(f"{Fore.RED}{Style.BRIGHT}GAME OVER")
                break

if __name__ == "__main__":
    main()
