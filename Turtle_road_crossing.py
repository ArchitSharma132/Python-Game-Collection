import time
import turtle
import random

# Constants
COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]
STARTING_MOVE_DISTANCE = 5
MOVE_INCREMENT = 10
FONT = ("Courier", 24, "normal")
STARTING_POSITION = (0, -280)
MOVE_DISTANCE = 10
FINISH_LINE_Y = 280


class Player(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.shape("turtle")
        self.penup()
        self.goto(STARTING_POSITION)
        self.setheading(90)

    def go_up(self):
        self.forward(MOVE_DISTANCE)

    def has_crossed_finish_line(self):
        return self.ycor() > FINISH_LINE_Y


class Scoreboard(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.penup()
        self.level = 1
        self.goto(-290, 250)
        self.write(f"Level: {self.level}", align="left", font=FONT)

    def increase_level(self):
        self.level += 1
        self.clear()
        self.write(f"Level: {self.level}", align="left", font=FONT)
    def game_over(self):
        self.goto(-90,0)
        self.write(f"GAME OVER", align="left", font=FONT)

class CarManager:
    def __init__(self):
        self.all_cars = []

    def create_cars(self):
        random_chance = random.randint(1, 6)
        if random_chance == 1:
            new_car = turtle.Turtle("square")
            new_car.shapesize(stretch_wid=1, stretch_len=2)
            new_car.penup()
            new_car.color(random.choice(COLORS))
            random_y = random.randint(-250, 250)
            new_car.goto(300, random_y)
            self.all_cars.append(new_car)

    def move_cars(self):
        for car in self.all_cars:
            car.backward(STARTING_MOVE_DISTANCE)


screen = turtle.Screen()

screen.setup(width=600, height=600)
screen.tracer(0)

# Creating player and car manager
player = Player()
car_manager = CarManager()
scoreboard = Scoreboard()
# Listening for key press
screen.listen()
screen.onkey(player.go_up, "Up")


game_is_on = True
while game_is_on:
    time.sleep(0.1)
    screen.update()
    car_manager.create_cars()
    car_manager.move_cars()

    for car in car_manager.all_cars:
        if car.distance(player) < 20:
            scoreboard.game_over()
            game_is_on = False
    if player.has_crossed_finish_line():
        player.goto(STARTING_POSITION)
        STARTING_MOVE_DISTANCE += 5
        scoreboard.increase_level()
screen.exitonclick()