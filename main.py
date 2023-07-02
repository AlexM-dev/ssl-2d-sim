import pygame
from pygame.locals import *
import math

# Constants for screen size
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600

# Constants for wall thickness
WALL_THICKNESS = 5


def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


class Robot:
    def __init__(self, rId, x, y, angle):
        self.rId = rId
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 0  # Adjust the robot's speed as needed
        self.kick_power = 50
        self.size = 15
        self.direction_indicator_length = self.size * 1.3
        self.color = (0, 0, 255)

    def update(self):
        if self.x <= WALL_THICKNESS or self.x >= SCREEN_WIDTH - WALL_THICKNESS:
            self.angle += math.pi  # Reverse x velocity
        if self.y <= WALL_THICKNESS or self.y >= SCREEN_HEIGHT - WALL_THICKNESS:
            self.angle += math.pi  # Reverse y velocity
        # Update the robot's position, velocity, etc.
        if self.speed > 5:
            self.speed = 5
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

    def render(self, screen):
        # Calculate the endpoint of the direction indicator
        direction_x = self.x + self.direction_indicator_length * math.cos(self.angle)
        direction_y = self.y + self.direction_indicator_length * math.sin(self.angle)

        # Draw the direction indicator as a line
        pygame.draw.line(screen, (0, 0, 255), (int(self.x), int(self.y)), (int(direction_x), int(direction_y)), 3)

        # Draw the robot as a circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

    def go_to_point(self, point):
        # Calculate the angle to the ball
        angle_to_ball = math.atan2(point.y - self.y, point.x - self.x)

        # Calculate the distance to the ball
        distance_to_ball = dist(point, self)

        self.speed = distance_to_ball
        self.angle = angle_to_ball

    def go_to_point_with_detour(self, point, robots):
        range_k = 4
        self.go_to_point(point)
        for robot in robots:
            if robot.rId == self.rId:
                continue
            if dist(robot, self) < range_k * self.size:
                x1 = self.speed * math.cos(self.angle)
                y1 = self.speed * math.cos(self.angle)
                ang = math.atan2(robot.y - self.y, robot.x - self.x)
                x2 = (range_k * self.size / dist(robot, self) ** 2) * math.cos(ang)
                y2 = (range_k * self.size / dist(robot, self) ** 2) * math.sin(ang)
                x = x1 + x2
                y = y1 + y2
                ang = math.atan2(y, x)
                spd = math.sqrt(x ** 2 + y ** 2)

                # Gradient Descent for angle adjustment
                step_size = 10  # Adjust the step size as needed
                self.angle += step_size * math.sin(ang)

                # Smooth the speed adjustment
                target_speed = math.sqrt(x ** 2 + y ** 2)  # Calculate the desired target speed
                speed_step = 0.1  # Adjust the speed adjustment step as needed
                if self.speed < target_speed:
                    self.speed += speed_step
                elif self.speed > target_speed:
                    self.speed -= speed_step

    def drive_to_ball(self, ball, robots):
        # Calculate the angle to the ball
        angle_to_ball = math.atan2(ball.y - self.y, ball.x - self.x)
        # Calculate the distance to the ball
        distance_to_ball = math.hypot(ball.x - self.x, ball.y - self.y)

        if distance_to_ball > self.size:  # Adjust the threshold as needed
            # Move towards the ball
            self.go_to_point_with_detour(ball, robots)
        else:
            # Kick the ball when close enough
            ball.kick(angle_to_ball, self.kick_power)


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity_x = 0
        self.velocity_y = 0
        self.kicked = False

    def update(self):
        # Update the ball's position, velocity, etc.
        if self.kicked:
            # Apply deceleration effect
            deceleration = 0.1  # Adjust the deceleration rate as needed
            self.velocity_x *= (1 - deceleration)
            self.velocity_y *= (1 - deceleration)
            self.x += self.velocity_x
            self.y += self.velocity_y

            # Check ball collision with walls
            if self.x <= WALL_THICKNESS or self.x >= SCREEN_WIDTH - WALL_THICKNESS:
                self.velocity_x *= -1  # Reverse x velocity
            if self.y <= WALL_THICKNESS or self.y >= SCREEN_HEIGHT - WALL_THICKNESS:
                self.velocity_y *= -1  # Reverse y velocity

    def render(self, screen):
        # Render the ball on the screen
        ball_color = (255, 165, 0)  # Adjust the color as needed
        ball_radius = 5  # Adjust the radius as needed
        ball_pos = (int(self.x), int(self.y))
        pygame.draw.circle(screen, ball_color, ball_pos, ball_radius)

    def kick(self, angle, power):
        # Perform the kick action based on the provided angle and power
        kick_speed = power  # Adjust the kick speed as needed
        self.velocity_x = kick_speed * math.cos(angle)
        self.velocity_y = kick_speed * math.sin(angle)
        self.kicked = True

    def goto(self, point):
        self.x = point.x
        self.y = point.y
        self.velocity_x = 0
        self.velocity_y = 0
        self.kicked = False


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Game:
    def __init__(self):
        pygame.init()
        window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("SSL Simulator")

        self.clock = pygame.time.Clock()

        # Create walls
        self.walls = [
            pygame.Rect(0, 0, SCREEN_WIDTH, WALL_THICKNESS),
            pygame.Rect(0, SCREEN_HEIGHT - WALL_THICKNESS, SCREEN_WIDTH, WALL_THICKNESS),
            pygame.Rect(0, 0, WALL_THICKNESS, SCREEN_HEIGHT),
            pygame.Rect(SCREEN_WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, SCREEN_HEIGHT)
        ]

        robot1 = Robot(0, 100, 300, 0)  # Example robot position and orientation
        robot2 = Robot(1, 500, 250, 0)  # Another example robot
        robot3 = Robot(1, 500, 350, 0)
        self.ball = Ball(800, 300)  # Example ball position

        self.robots = [robot1, robot2, robot3]  # Add more robots as needed

        self.running = True
        self.replay_mode = False

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    self.ball.goto(Point(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

            # Clear the screen
            self.screen.fill((153, 255, 153))  # Set background color

            # Draw walls
            for wall in self.walls:
                pygame.draw.rect(self.screen, (0, 0, 0), wall)

            self.robots[0].go_to_point_with_detour(self.ball, self.robots)
            for robot in self.robots:
                robot.update()
                robot.render(self.screen)

            # Update and render the ball
            self.ball.update()
            self.ball.render(self.screen)

            # Update the display
            pygame.display.flip()

            # Set the desired frames per second
            self.clock.tick(60)  # Adjust the FPS as needed

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
