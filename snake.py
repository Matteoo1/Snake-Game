import tkinter as tk
import random
from abc import ABC, abstractmethod

class Snake:
    def __init__(self, game_width, game_height):
        self.body = [(0, 0), (0, 1), (0, 2)]
        self.direction = "Right"
        self.next_direction = self.direction
        self.growing = False
        self.speed = 100 
        self.game_width = game_width
        self.game_height = game_height

    def move(self):
        self.direction = self.next_direction
        x, y = self.body[0]
        if self.direction == "Right":
            new_head = ((x + 1) % self.game_width, y)
        elif self.direction == "Left":
            new_head = ((x - 1) % self.game_width, y)
        elif self.direction == "Up":
            new_head = (x, (y - 1) % self.game_height)
        elif self.direction == "Down":
            new_head = (x, (y + 1) % self.game_height)

        self.body = [new_head] + self.body[:-1]

        if self.growing:
            self.body.append(self.body[-1])
            self.growing = False

    def grow(self):
        self.growing = True

    def shrink(self):
        if len(self.body) > 3:
            self.body.pop()

    def speed_up(self):
        min_speed = 70 
        if self.speed > min_speed:
            self.speed -= 5
        else:
            self.speed = min_speed

    def change_direction(self, new_direction):
        opposite_directions = {"Right": "Left", "Left": "Right", "Up": "Down", "Down": "Up"}
        if new_direction != opposite_directions[self.direction]:
            self.next_direction = new_direction

    def get_head_position(self):
        return self.body[0]

    def collision_with_self(self):
        return self.get_head_position() in self.body[1:]

class Food:
    def __init__(self, x, y):
        self.position = (x, y)
        self.color = "red"  # defualt color for normal food


    def effect(self, snake):
        snake.grow()

    def respawn(self, max_x, max_y):
        self.position = (random.randint(0, max_x), random.randint(0, max_y))

class SpecialFood(Food):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "green"  # uniqe color for special food

    def effect(self, snake):
        snake.grow()
        snake.speed_up()

class PoisonousFood(Food):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "purple"  # uniqe color for poison food

    def effect(self, snake):
        snake.shrink()


class Obstacle(ABC):
    def __init__(self, x, y):
        self.position = (x, y)

    @abstractmethod
    def effect(self, snake):
        pass

class Wall(Obstacle):
    def effect(self, snake):
        snake.game_over()

class BreakableWall(Wall):
    def effect(self, snake):
        pass  # nothing happen, snake continue moving

class SnakeGame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.width = 20
        self.height = 20
        self.cell_size = 20
        self.snake = Snake(self.width, self.height)
        self.food = Food(random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        self.obstacles = [Wall(5, 5), BreakableWall(10, 10)]  
        self.move_obstacles()  # start the first placment of obstacle

        self.init_ui()

    def move_obstacles(self):
        for obstacle in self.obstacles:
            new_x = random.randint(0, self.width - 1)
            new_y = random.randint(0, self.height - 1)
            obstacle.position = (new_x, new_y)

        self.after(4000, self.move_obstacles)  # Schedule next relocation after 4000 ms (4 seconds)



    def init_ui(self):
        # Set the window title and pack the frame
        self.master.title("Snake Game")
        self.pack()

        # Create and pack the canvas where the game will be drawn
        self.canvas = tk.Canvas(self, width=self.width*self.cell_size, height=self.height*self.cell_size, borderwidth=0, highlightthickness=0, bg="white")
        self.canvas.pack()

        # Start the game loop
        self.start_game()

    def start_game(self):
        # Begin the game by updating game state and enabling keyboard input
        self.update_game()
        self.canvas.focus_set()  # Focus set to canvas to capture key events
        self.canvas.bind("<Key>", self.on_key_press)  # Bind keyboard events to handle snake direction

    def update_game(self):
        # Move the snake based on current direction
        self.snake.move()
        head_x, head_y = self.snake.get_head_position()

        # Check for collisions with itself
        if self.snake.collision_with_self():
            self.game_over()  # End game if collision occurs
            return

        # Check if snake's head is on the food item
        if (head_x, head_y) == self.food.position:
            self.food.effect(self.snake)  # Trigger the food's effect on the snake
            # Randomly select a new type of food and respawn it
            food_type = random.choice([Food, SpecialFood, PoisonousFood])
            self.food = food_type(random.randint(0, self.width - 1), random.randint(0, self.height - 1))

        # Check for collisions with obstacles
        for obstacle in self.obstacles:
            if (head_x, head_y) == obstacle.position:
                obstacle.effect(self.snake)  # Apply obstacle's effect if collision occurs

        # Redraw the game components on the canvas
        self.draw()
        # Schedule the next game update based on the current speed of the snake
        self.after(self.snake.speed, self.update_game)


    def draw(self):
        # Clear previous drawings of snake, food, and obstacles from the canvas
        self.canvas.delete("snake")
        self.canvas.delete("food")
        self.canvas.delete("obstacle")

        # Draw each segment of the snake's body on the canvas
        for x, y in self.snake.body:
            self.canvas.create_rectangle(x * self.cell_size, y * self.cell_size, (x + 1) * self.cell_size, (y + 1) * self.cell_size, fill="blue", tags="snake")
        
        # Draw the food item at its current position
        fx, fy = self.food.position
        self.canvas.create_rectangle(fx * self.cell_size, fy * self.cell_size, (fx + 1) * self.cell_size, (fy + 1) * self.cell_size, fill=self.food.color, tags="food")

        # Draw obstacles at their positions
        for obstacle in self.obstacles:
            ox, oy = obstacle.position
            self.canvas.create_rectangle(ox * self.cell_size, oy * self.cell_size, (ox + 1) * self.cell_size, (oy + 1) * self.cell_size, fill="grey", tags="obstacle")

    def on_key_press(self, event):
        # Handle key presses for controlling the snake's direction
        key_press = event.keysym
        if key_press in ["Up", "Down", "Left", "Right"]:
            self.snake.change_direction(key_press)

    def game_over(self):
        # Display a 'Game Over' message in the middle of the canvas
        self.canvas.create_text(self.width * self.cell_size / 2, self.height * self.cell_size / 2, text="Game Over", font=('Arial', 20), fill="red")

def main():
    # Initialize the main application window and start the game
    root = tk.Tk()
    game = SnakeGame(master=root)
    game.mainloop()

if __name__ == "__main__":
    # Check if the script is run as the main program and execute main function
    main()
