import tkinter as tk
from random import choice


class Bord:
    def __init__(self , root):
        self.root = root
        self.canvas = tk.Canvas(self.root , height=height , width=width-120 , bg='black')
        self.canvas.pack(side='right')
        self.timer_label = tk.Label(self.root, text="Time: 0s", fg="white", bg="black", font=("Arial", 14))
        self.timer_label.pack(pady=10)
        self.time = -1
        self.score_label = tk.Label(self.root, text="Score: 0", fg="white", bg="black", font=("Arial", 14))
        self.score_label.pack(pady=10)
        self.score = 0
        self.level_label = tk.Label(self.root, text="Level: 1", fg="white", bg="black", font=("Arial", 14))
        self.level_label.pack(pady=10)
        self.level = 1
        self.shapes = []
        self.speed = 300
        self.speed2 = 300
        self.falling_shape = self.create_shape()
        self.root.bind('<KeyPress>' , self.move)
        self.root.bind('<KeyRelease>' , self.release_down)
        self.run_id = None
        self.timer_id = None
        self.timer()
        self.run()
    def run(self):
        if not self.falling_shape.can_fall():
            self.is_line()
            if self.is_fail():
                self.root.unbind("<KeyPress>")
                self.root.unbind("<KeyRelease>")
                self.root.after_cancel(self.timer_id)
                self.root.after_cancel(self.run_id)
                self.draw()
                self.canvas.create_text(width*0.4, height/2, text="Game Over", fill="red", font=("Arial", 42, "bold"))
                self.restart_button = tk.Button(self.root, text="Restart", bg='green' , font=("Arial", 14, "bold"), command=run_game)
                self.restart_button.pack(pady=20)
                return
            self.falling_shape = self.create_shape()
        self.draw()
        self.falling_shape.fall()
        self.run_id = self.root.after(self.speed, self.run)

    def timer(self):
        self.time += 1
        self.timer_label.config(text=f'Time: {self.time}s')
        if self.time % 15 == 0 and self.time != 0:
            self.level += 1
            self.level_label.config(text=f'Level: {self.level}')
            self.speed2 = max(100 , self.speed2 - 30)
            if self.speed != 30:
                self.speed = max(100 , self.speed - 30)
        self.timer_id = self.root.after(1000 , self.timer)

    def draw(self):
        self.canvas.delete("all")
        for shape in self.shapes:
            for block in shape.blocks:
                self.canvas.create_rectangle(block.x , block.y , block.x+block.size , block.y+block.size , fill=block.shape.color)

    def create_shape(self):
        shape = choice([OShape , SShape , LShape , TShape , ZShape , JShape , IShape])
        shape = shape(self)
        self.shapes.append(shape)
        return shape
    
    def move(self , event):
        ev = event.keysym
        if ev == "Down":
            self.speed = 30
        elif ev == "Left" and self.falling_shape.can_move(ev):
            for block in self.falling_shape.blocks:
                block.x -= block.size
        elif ev == "Right" and self.falling_shape.can_move(ev):
            for block in self.falling_shape.blocks:
                block.x += block.size
        elif ev == "Up":
            if type(self.falling_shape) != OShape:
                self.falling_shape.rotate()
        self.draw()

    def release_down(self , event):
        if event.keysym == "Down":
            self.speed = self.speed2

    def is_line(self):
        lines_to_clear = []
        y_positions = [block.y for shape in self.shapes for block in shape.blocks]
        for y in range(height-block_size, -1, -block_size):
            if y_positions.count(y) == 12:
                lines_to_clear.append(y)

        if not lines_to_clear:
            return False

        lines_to_clear.sort()
        for y in reversed(lines_to_clear):
            for shape in self.shapes:
                shape.blocks = [block for block in shape.blocks if block.y != y]

        for y in lines_to_clear:
            for shape in self.shapes:
                for block in shape.blocks:
                    if block.y < y:
                        block.y += block.size
        self.score += len(lines_to_clear) * 10
        self.score_label.config(text=f'Score: {self.score}')

        return True

    def is_fail(self):
        for block in self.falling_shape.blocks:
            if block.y <= 0:
                return True
        return False

class Block:
    def __init__(self , x , y , shape):
        self.shape = shape
        self.x = x
        self.y = y
        self.size = block_size

class Shape:
    def __init__(self , bord , color):
        self.bord = bord
        self.blocks = []
        self.color = color
    def fall(self):
        for block in self.blocks:
            block.y += block.size
    def can_fall(self):
        for self_block in self.blocks:
            for other_shape in self.bord.shapes[:-1]:
                for other_block in other_shape.blocks:
                    if self_block.x == other_block.x and self_block.y == other_block.y - other_block.size:
                        return False
        for block in self.blocks:
            if block.y == height-block_size:
                return False
        return True
    def can_move(self , r_l):
        for self_block in self.blocks:
            for other_shape in self.bord.shapes[:-1]:
                for other_block in other_shape.blocks:
                    if r_l == "Left" and self_block.y == other_block.y and self_block.x == other_block.x + other_block.size:
                        return False
                    elif r_l == "Right" and self_block.y == other_block.y and self_block.x == other_block.x - other_block.size:
                        return False
            if r_l == 'Left' and self_block.x == 0:
                return False
            elif r_l == 'Right' and self_block.x == width-block_size-120:
                return False        
        return True

    def rotate(self):
        center = self.blocks[0]
        new_positions = []

        for block in self.blocks:
            relative_x = block.x - center.x
            relative_y = block.y - center.y
            new_x = center.x - relative_y 
            new_y = center.y + relative_x 

            if new_x < 0 or new_x >= width-120 or new_y >= height:
                return
            
            for shape in self.bord.shapes:
                if shape != self:
                    for other_block in shape.blocks:
                        if new_x == other_block.x and new_y == other_block.y:
                            return

            new_positions.append((new_x, new_y))

        for i, block in enumerate(self.blocks):
            block.x, block.y = new_positions[i]

class OShape(Shape):
    def __init__(self, bord , color = 'gray'):
        super().__init__(bord , color)
        self.blocks = [Block(5*block_size , -2*block_size , self) , Block(6*block_size , -2*block_size , self) , Block(5*block_size , -block_size , self) , Block(6*block_size , -block_size , self)]
        
class SShape(Shape):
    def __init__(self, bord , color = 'blue'):
        super().__init__(bord , color)
        self.blocks = [Block(6*block_size , -2*block_size , self) , Block(5*block_size , -2*block_size , self) , Block(4*block_size , -block_size , self) , Block(5*block_size , -block_size , self)]

class LShape(Shape):
    def __init__(self, bord , color = 'green'):
        super().__init__(bord , color)
        self.blocks = [Block(4*block_size , -block_size , self) , Block(5*block_size , -block_size , self) , Block(4*block_size , -2*block_size , self) , Block(4*block_size , -3*block_size , self)]

class ZShape(Shape):
    def __init__(self, bord, color='yellow'):
        super().__init__(bord, color)
        self.blocks = [Block(6*block_size, -2*block_size, self) , Block(5*block_size, -2*block_size, self) , Block(6*block_size, -block_size, self) , Block(7*block_size, -block_size, self) ]

class TShape(Shape):
    def __init__(self, bord, color='purple'):
        super().__init__(bord, color)
        self.blocks = [Block(5*block_size, -block_size, self),Block(5*block_size, -2*block_size, self) , Block(4*block_size, -block_size, self) , Block(6*block_size, -block_size, self)]

class IShape(Shape):
    def __init__(self, bord, color='cyan'):
        super().__init__(bord, color)
        self.blocks = [Block(5*block_size, -2*block_size, self) , Block(5*block_size, -block_size, self) , Block(5*block_size, -3*block_size, self) , Block(5*block_size, -4*block_size, self)]

class JShape(Shape):
    def __init__(self, bord, color='orange'):
        super().__init__(bord, color)
        self.blocks = [Block(5*block_size, -block_size, self) , Block(4*block_size, -block_size, self) , Block(5*block_size, -2*block_size, self) , Block(5*block_size, -3*block_size, self)]

root = tk.Tk()
root.title('Tetris')
block_size = root.winfo_screenheight() // 30
height = block_size * 20
width = int(120 + (12 * block_size))
root.geometry(f'{width}x{height}')
root.resizable(False , False)
def run_game():
    for widget in root.winfo_children():
        widget.destroy()
    Bord(root)
run_game()
root.mainloop()
