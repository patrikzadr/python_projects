from typing import List
import tkinter as tk

# change hw2 below if your file name is different
import hw2 as student

# game parameters; feel free to change them
ROW_SIZE = 17
NEW_NUMBERS = [2, 2, 2, 4]  # unwinnable, try [2] instead

# False for basic, True for multi
MODE_MULTI = False

BORDER = 32
CELL_SIZE = 64
FONT = ('system', '16')


def draw(canvas: tk.Canvas, row: List[int]) -> None:
    canvas.delete("all")
    for i, tile in enumerate(row):
        left = CELL_SIZE * i + BORDER
        canvas.create_rectangle(left, BORDER,
                                left + CELL_SIZE, BORDER + CELL_SIZE)
        if tile != 0:
            canvas.create_text(left + CELL_SIZE // 2, BORDER + CELL_SIZE // 2,
                               text=str(tile), font=FONT)


def update(row: List[int], to_left: bool) -> None:
    if MODE_MULTI:
        result = student.slide_multi(row, to_left)
    else:
        result = student.slide_basic(row, to_left)

    if result:
        student.add_random(row, NEW_NUMBERS)


def update_and_draw(row: List[int], to_left: bool, canvas: tk.Canvas) -> None:
    update(row, to_left)
    draw(canvas, row)


def reset_and_draw(row: List[int], canvas: tk.Canvas) -> None:
    for i in range(ROW_SIZE):
        row[i] = 0
    student.add_random(row, NEW_NUMBERS)
    draw(canvas, row)


def main() -> None:
    root = tk.Tk()
    canvas = tk.Canvas(
        width=2 * BORDER + ROW_SIZE * CELL_SIZE,
        height=2 * BORDER + CELL_SIZE,
    )
    row = [0 for _ in range(ROW_SIZE)]
    reset_and_draw(row, canvas)

    canvas.bind_all("<Left>", lambda _: update_and_draw(row, True, canvas))
    canvas.bind_all("<Right>", lambda _: update_and_draw(row, False, canvas))
    canvas.bind_all("r", lambda _: reset_and_draw(row, canvas))
    canvas.bind_all("q", lambda _: root.destroy())

    canvas.pack()
    root.mainloop()


if __name__ == '__main__':
    main()
