import time
import turtle
import random

# Constants
COLORS = ["red", "orange", "yellow", "green", "blue", "purple"]
FONT = ("Courier", 24, "normal")
Ball_Speed = 10
FINISH_LINE_Y = 230
STARTING_POSITION = (0, -230)


class Player(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.shape("turtle")
        self.penup()
        self.goto(STARTING_POSITION)
        self.setheading(90)
        self.speed(0)

    def go_left(self):
        x = player.xcor()
        if x > -246:  # Set left boundary
            player.setx(x - 20)
        if x < -246:
            player.setx(x=-246)

    def go_right(self):
        x = player.xcor()
        if x < 246:  # Set right boundary
            player.setx(x + 20)
        if x > 246:
            player.setx(x=246)

    def go_up(self):
        self.forward(20)

    def has_crossed_finish_line(self):
        return self.ycor() > FINISH_LINE_Y


class Scoreboard(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.penup()
        self.level = 1
        self.lives = 3
        self.goto(-230, 224)
        self.write(f"Level: {self.level}", align="left", font=FONT)

    def increase_level(self):
        self.level += 1
        self.clear()
        self.write(f"Level: {self.level}", align="left", font=FONT)

    def game_over(self):
        self.goto(-90, 0)
        self.write(f"GAME OVER", align="left", font=FONT)


class BallManager:
    def __init__(self):
        self.all_balls = []

    def create_balls(self):
        random_chance = random.randint(1, 15)
        if random_chance % 5 == 0 or random_chance == 1:
            new_ball = turtle.Turtle("circle")
            new_ball.penup()
            new_ball.color(random.choice(COLORS))
            new_ball.shapesize(random.uniform(0.5, 1.5))
            random_x = random.randint(-246, 246)
            new_ball.goto(random_x, 256)
            self.all_balls.append(new_ball)

    def move_balls(self):
        for ball in self.all_balls:
            new_y = ball.ycor() - Ball_Speed
            ball.goto(ball.xcor(), new_y)


screen = turtle.Screen()
screen.setup(width=512, height=512)
screen.tracer(0)

player = Player()
ball_manager = BallManager()
scoreboard = Scoreboard()
screen.listen()
screen.onkey(player.go_left, "Left")
screen.onkey(player.go_right, "Right")
screen.onkey(player.go_up, "Up")
game_is_on = True
while game_is_on:
    time.sleep(0.1)
    screen.update()
    ball_manager.create_balls()
    ball_manager.move_balls()
    for ball in ball_manager.all_balls:
        if player.ycor() == -230:
            continue
        elif ball.distance(player) < 20:
            scoreboard.game_over()
            game_is_on = False
    if player.has_crossed_finish_line():
        player.goto(player.xcor(), -230)
        Ball_Speed += 5
        scoreboard.increase_level()

screen.exitonclick()