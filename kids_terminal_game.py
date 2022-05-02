from typing import List, Optional, Tuple, Union

Playground = List[List[str]]


def new_playground(size: int) -> Playground:
    return [[" " for _ in range(size)] for _ in range(size)]


def init_playground(playground: Playground) -> None:
    half_index = len(playground) // 2
    playground[half_index - 1][half_index - 1] = "X"
    playground[half_index][half_index] = "X"
    playground[half_index][half_index - 1] = "O"
    playground[half_index - 1][half_index] = "O"


def get(playground: Playground, row: int, col: int) -> str:
    return playground[row][col]


def set_symbol(playground: Playground, row: int,
               col: int, symbol: str) -> None:
    playground[row][col] = symbol


def draw_header(length: int) -> None:
    print("     ", end="")
    for i in range(length):
        print("{:<4}".format(i), end="")
    print("")


def draw_line(length: int) -> None:
    print("   +", end="")
    for _ in range(length):
        print("---+", end="")
    print("")


def draw_values(length: int, char: str,
                playground: Playground, row_num: int) -> None:
    print(" {} |".format(char), end="")
    for i in range(length):
        print(" {} |".format(playground[row_num][i]), end="")
    print("")


def draw(playground: Playground) -> None:
    length = len(playground)
    draw_header(length)
    draw_line(length)
    char = ord('A')

    for i in range(length):
        draw_values(length, chr(char), playground, i)
        draw_line(length)
        char += 1


def valid_coordinates(playground: Playground, row: int, col: int) -> bool:
    return (0 <= row < len(playground)) and (0 <= col < len(playground))


def pick_enemy_symbol(symbol: str) -> str:
    symbols = ["X", "O"]
    symbols.remove(symbol)
    enemy_symbol = symbols[0]
    return enemy_symbol


def move_coordinates(row_move: int, col_move: int, course_row: int,
                     course_col: int, forward: bool) -> Tuple[int, int]:
    if forward:
        row_move += course_row
        col_move += course_col
    else:
        row_move -= course_row
        col_move -= course_col
    return row_move, col_move


def move_forward(playground: Playground, row_move: int, col_move: int,
                 course_row: int, course_col: int,
                 symbol: str) -> Tuple[int, int]:
    while valid_coordinates(playground, row_move + course_row,
                            col_move + course_col) \
            and playground[row_move][col_move] not in (" ", symbol):
        row_move, col_move = move_coordinates(row_move, col_move, course_row,
                                              course_col, forward=True)
    return row_move, col_move


def switch_stones(playground: Playground, row_move: int, col_move: int,
                  course_row: int, course_col: int, symbol: str, row: int,
                  col: int, enemy_symbol: str, switched_stones: int) -> int:
    while (row_move != row) or (col_move != col):
        row_move, col_move = move_coordinates(row_move, col_move, course_row,
                                              course_col, forward=False)
        if playground[row_move][col_move] == enemy_symbol:
            switched_stones += 1
        playground[row_move][col_move] = symbol
    return switched_stones


def make_play(playground: Playground, symbol: str, row: int, col: int,
              enemy_symbol: str, just_strategy: bool) \
        -> Optional[Union[int, bool]]:
    switched: int = 0
    directions: List[List[int]] = [[-1, -1], [0, -1], [1, -1], [-1, 0],
                                   [1, 0], [-1, 1], [0, 1], [1, 1]]

    for course_row, course_col in directions:
        row_move: int = row + course_row
        col_move: int = col + course_col
        if not valid_coordinates(playground, row_move, col_move) \
                or playground[row_move][col_move] != enemy_symbol:
            continue
        row_move, col_move = move_forward(playground, row_move, col_move,
                                          course_row, course_col, symbol)
        if playground[row_move][col_move] != symbol:
            continue
        if just_strategy:
            return True
        switched = switch_stones(playground, row_move, col_move,
                                 course_row, course_col, symbol, row, col,
                                 enemy_symbol, switched)
    if switched == 0:
        return None
    return switched


def play(playground: Playground, row: int,
         col: int, symbol: str) -> Optional[int]:
    if playground[row][col] != " ":
        return None
    enemy_symbol = pick_enemy_symbol(symbol)
    return make_play(playground, symbol, row, col,
                     enemy_symbol, just_strategy=False)


def strategy(playground: Playground, symbol: str) -> Optional[Tuple[int, int]]:
    enemy_symbol = pick_enemy_symbol(symbol)
    for row in range(len(playground)):
        for col in range(len(playground[row])):
            if playground[row][col] != " ":
                continue
            if make_play(playground, symbol, row, col,
                         enemy_symbol, just_strategy=True):
                return row, col
    return None


def count(playground: Playground) -> Tuple[int, int]:
    x_stones = 0
    o_stones = 0
    for row in playground:
        x_stones += row.count("X")
        o_stones += row.count("O")
    return x_stones, o_stones


def asks_for_starter() -> bool:
    start = input("DO YOU WANT TO START FIRST? [Y]/[N]: \n")
    if start.upper() == "Y":
        return True
    if start.upper() == "N":
        return False
    print("\n[WRONG CHOICE, TRY AGAIN]")
    return asks_for_starter()


def pick_symbol() -> Tuple[str, str]:
    symbol = input("PICK YOUR SYMBOL [X]/[O]: \n")
    symbol = symbol.upper()
    if symbol not in ("X", "O"):
        print("\n[WRONG SYMBOL, TRY AGAIN]")
        return pick_symbol()
    return symbol, pick_enemy_symbol(symbol)


def pick_coordinates(playground: Playground) -> Tuple[int, int]:
    print("\n[BOTH ROW AND COLLUM ARE NUMBERED FROM 0]")
    row = input("PICK NUMBER OF ROW YOU WANT TO PLAY ON: \n")
    col = input("PICK NUMBER OF COLLUM YOU WANT TO PLAY ON: \n")
    if not (row.isdecimal() and col.isdecimal()):
        print("\n[WRONG FORMAT OF COORDINATES, TRY AGAIN]")
        return pick_coordinates(playground)
    num_row = int(row)
    num_col = int(col)

    if not valid_coordinates(playground, num_row, num_col):
        print("\n[COORDINATES NOT ON PLAYGROUND, TRY AGAIN]")
        return pick_coordinates(playground)
    return num_row, num_col


def print_results(playground: Playground) -> None:
    x, o = count(playground)
    if x > o:
        print("PLAYER X WON")
    elif x < o:
        print("PLAYER O WON")
    else:
        print("DRAW")


def player_play(playground: Playground, symbol: str,
                enemy_turn: bool) -> Optional[bool]:
    draw(playground)
    row, col = pick_coordinates(playground)
    if play(playground, row, col, symbol) is None:
        print("\n[INVALID MOVE TRY AGAIN]\n")
        return pick_and_play(playground, symbol, enemy_turn)
    play(playground, row, col, symbol)
    return None


def enemy_play(playground: Playground, symbol: str) -> None:
    draw(playground)
    row_and_col = strategy(playground, symbol)
    if row_and_col is not None:
        row, col = row_and_col
        play(playground, row, col, symbol)


def end_of_the_game(playground: Playground, num_x: int, num_o: int) -> None:
    print("\n\nEND OF THE GAME")
    print("NUMBER OF STONES X:{} O:{}".format(num_x, num_o))
    print_results(playground)
    print("FINAL PLAYGROUND\n")
    draw(playground)


def pick_and_play(playground: Playground, symbol: str,
                  enemy_turn: bool) -> bool:
    num_x, num_o = count(playground)
    if (num_x + num_o) == len(playground) ** 2:
        end_of_the_game(playground, num_x, num_o)
        return False
    print("\nNUMBER OF STONES X:{} O:{}\n".format(num_x, num_o))

    if strategy(playground, symbol) is None:
        print("SKIPPING ROUND, NOWHERE TO PLAY")
        return True
    if enemy_turn:
        enemy_play(playground, symbol)
    else:
        player_play(playground, symbol, enemy_turn)
    return True


def game(size: int) -> None:
    print("\n    {}\n".format("*** REVERSI ***"))
    field = new_playground(size)
    init_playground(field)
    symbol, enemy_symbol = pick_symbol()
    next_turn = True

    if asks_for_starter():
        while next_turn:
            next_turn = (pick_and_play(field, symbol, enemy_turn=False) and
                         pick_and_play(field, enemy_symbol, enemy_turn=True))
    else:
        while next_turn:
            next_turn = (pick_and_play(field, enemy_symbol, enemy_turn=True)
                         and pick_and_play(field, symbol, enemy_turn=False))

