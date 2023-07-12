import pygame
from pygame.locals import *
import math
import random
import auxiliary

SCALE = 0.1

# Constants for screen size
SCREEN_WIDTH = 10400 * SCALE
SCREEN_HEIGHT = 7400 * SCALE

FIELD_W = 9000 * SCALE
FIELD_H = 6000 * SCALE

WALL_THICKNESS = 0
LINE_THICKNESS = 1

# Constants for the goal
GOAL_WIDTH = 1000 * SCALE  # For Division A
GOAL_HEIGHT = 160 * SCALE
GOAL_DEPTH = 180 * SCALE
GOAL_WALL_THICKNESS = 20 * SCALE

# Goal positions
GOAL_Y_POSITION = SCREEN_HEIGHT / 2 - GOAL_WIDTH / 2
GOAL_1_X_POSITION = (SCREEN_WIDTH - FIELD_W) / 2 - GOAL_DEPTH
GOAL_2_X_POSITION = (SCREEN_WIDTH + FIELD_W) / 2


class Robot:
    def __init__(self, r_id, x, y, angle, team):
        self.rId = r_id
        self.x = x
        self.y = y
        self.size = 180 * SCALE
        self.height = 800 * SCALE
        self.maxSpeed = 6
        self.maxSpeedR = 0.15
        self.direction_indicator_length = self.size * 1.3
        self.angle = angle
        if team == 'y':
            self.color = (255, 255, 0)
        else:
            self.color = (0, 0, 255)

        # Changeable params
        self.speedX = 0
        self.speedY = 0
        self.speedR = 0

        self.kick_power = 40
        self.mass = 5.0  # Robot mass
        self.friction = 0.6  # Friction coefficient
        self.up_kick_angle = auxiliary.format_angle(45 / (180 / math.pi))

    def update(self, robots, ball):
        self.handle_collisions(robots, ball)

        if self.x <= WALL_THICKNESS:
            self.x = WALL_THICKNESS
            self.speedX = -self.speedX
        elif self.x >= SCREEN_WIDTH - WALL_THICKNESS:
            self.x = SCREEN_WIDTH - WALL_THICKNESS
            self.speedX = -self.speedX

        if self.y <= WALL_THICKNESS:
            self.y = WALL_THICKNESS
            self.speedY = -self.speedY
        elif self.y >= SCREEN_HEIGHT - WALL_THICKNESS:
            self.y = SCREEN_HEIGHT - WALL_THICKNESS
            self.speedY = -self.speedY

        if (self.speedX ** 2 + self.speedY ** 2) ** 0.5 > self.maxSpeed:
            tempAng = math.atan2(self.speedY, self.speedX)
            self.speedX = self.maxSpeed * math.cos(tempAng)
            self.speedY = self.maxSpeed * math.sin(tempAng)

        self.x += self.speedX
        self.y += self.speedY

        if self.speedR > self.maxSpeedR:
            self.speedR = self.maxSpeedR
        if self.speedR < -self.maxSpeedR:
            self.speedR = -self.maxSpeedR
        self.angle += self.speedR

        self.apply_friction()

    def apply_friction(self):
        # Apply friction to slow down the robot's movement
        self.speedX *= (1 - self.friction)
        self.speedY *= (1 - self.friction)
        self.speedR *= (1 - self.friction)

    def handle_collisions(self, robots, ball):
        for robot in robots:
            if robot != self:
                distance = math.hypot(robot.x - self.x, robot.y - self.y)
                if distance <= (self.size + robot.size):
                    self.collide_with_robot(robot)

        distance_to_ball = math.hypot(ball.x - self.x, ball.y - self.y)
        if distance_to_ball <= (self.size + ball.radius) * 1.1:
            self.collide_with_ball(ball)

    def collide_with_robot(self, robot):
        # Calculate the angle between the two robots
        angle = math.atan2(robot.y - self.y, robot.x - self.x)

        # Calculate the distance between the two robots
        distance = math.hypot(robot.x - self.x, robot.y - self.y)

        # Calculate the overlap between the two robots
        overlap = self.size + robot.size - distance

        # Calculate the impulse force
        impulse = overlap * self.mass * robot.mass / (self.mass + robot.mass)

        # Apply the impulse force to both robots
        self.speedX -= impulse * math.cos(angle) / self.mass
        self.speedY -= impulse * math.sin(angle) / self.mass
        robot.speedX += impulse * math.cos(angle) / robot.mass
        robot.speedY += impulse * math.sin(angle) / robot.mass

    def collide_with_ball(self, ball):
        overlap = self.size + ball.radius - math.hypot(ball.x - self.x, ball.y - self.y)
        angle = math.atan2(ball.y - self.y, ball.x - self.x)

        if ball.z < self.height:
            if ball.kicked and self.rId != ball.kicked_id:
                if auxiliary.format_angle(self.angle - angle) < 10 / (180 / math.pi):
                    ball_speed = ((ball.velocity_x ** 2 + ball.velocity_y ** 2) ** 0.5) * 0.15
                else:
                    ball_speed = ((ball.velocity_x ** 2 + ball.velocity_y ** 2) ** 0.5) * 0.6
                ball.velocity_x = ball_speed * math.cos(angle)
                ball.velocity_y = ball_speed * math.sin(angle)
            else:
                overlap_x = 0.5 * overlap * math.cos(angle)
                overlap_y = 0.5 * overlap * math.sin(angle)
                ball.x += overlap_x
                ball.y += overlap_y

    def render(self, screen):
        # Calculate the endpoint of the direction indicator
        direction_x = self.x + self.direction_indicator_length * math.cos(self.angle)
        direction_y = self.y + self.direction_indicator_length * math.sin(self.angle)

        # Draw the direction indicator as a line
        pygame.draw.line(screen, self.color, (int(self.x), int(self.y)), (int(direction_x), int(direction_y)), 3)

        # Draw the robot as a circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

    def go_to_point(self, point):
        # Calculate the angle to the ball
        angle_to_point = math.atan2(point.y - self.y, point.x - self.x)

        # Calculate the distance to the ball
        distance_to_point = math.dist((self.x, self.y), (point.x, point.y))

        self.speedX = distance_to_point * math.cos(angle_to_point)
        self.speedY = distance_to_point * math.sin(angle_to_point)

    def rotate_to_point(self, point):
        vx = self.x - point.x
        vy = self.y - point.y
        ux = -math.cos(self.angle)
        uy = -math.sin(self.angle)
        dif = -math.atan2(auxiliary.scal_mult(auxiliary.Point(vx, vy), auxiliary.Point(ux, uy)),
                          auxiliary.vect_mult(auxiliary.Point(vx, vy), auxiliary.Point(ux, uy)))
        if abs(dif) > 0.1:
            self.speedR = dif * 10
        else:
            self.speedR = 0

    def drive_to_ball(self, ball, robots):
        # Calculate the distance to the ball
        distance_to_ball = math.hypot(ball.x - self.x, ball.y - self.y)

        self.rotate_to_point(ball)
        if distance_to_ball > (self.size + ball.radius) * 1.3:  # Adjust the threshold as needed
            # Move towards the ball
            self.go_to_point(ball)
        else:
            pass
            self.kick_ball(ball)

    def kick_ball(self, ball):
        # Calculate the angle to the ball
        angle_to_ball = auxiliary.format_angle(math.atan2(ball.y - self.y, ball.x - self.x) - self.angle)

        # Calculate the distance to the ball
        distance_to_ball = math.hypot(ball.x - self.x, ball.y - self.y)

        if abs(angle_to_ball) < 10 / (180 / math.pi) and distance_to_ball < (
                self.size + ball.radius) * 1.15 and ball.z == 0:
            ball.kick_up(self.angle, self.up_kick_angle, self.kick_power, self.rId, self.speedX, self.speedY)
            # ball.kick(self.angle, self.kick_power, self.rId, self.speedX, self.speedY)


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = 0  # z position of the ball
        self.velocity_x = 0
        self.velocity_y = 0
        self.velocity_z = 0  # z-axis velocity
        self.radius = 43 * SCALE
        self.kicked = False
        self.kicked_id = 0

        self.mass = 0.046  # Ball mass
        self.friction = 0.05  # Friction coefficient
        self.air_resistance = 0.05  # Air resistance coefficient
        self.gravity = 9.81 * SCALE  # Gravitational acceleration

    def update(self):
        if self.z > 0:
            # Apply friction and air resistance
            self.velocity_x *= (1 - self.air_resistance)
            self.velocity_y *= (1 - self.air_resistance)
            self.velocity_z *= (1 - self.air_resistance)
        else:
            self.velocity_x *= (1 - self.friction - self.air_resistance)
            self.velocity_y *= (1 - self.friction - self.air_resistance)
            self.velocity_z *= (1 - self.air_resistance)

        # Apply gravity effect
        self.velocity_z -= self.gravity

        # Update the ball's position
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.z += self.velocity_z  # Update z position
        if self.z < 0:
            self.z = 0  # The ball should not go below the ground level
            self.velocity_z = 0

        # Check ball collision with walls
        if self.x <= WALL_THICKNESS or self.x >= SCREEN_WIDTH - WALL_THICKNESS:
            self.velocity_x *= -1  # Reverse x velocity
        if self.y <= WALL_THICKNESS or self.y >= SCREEN_HEIGHT - WALL_THICKNESS:
            self.velocity_y *= -1  # Reverse y velocity

        '''if self.x <= (SCREEN_WIDTH - FIELD_W) / 2 or self.x >= (SCREEN_WIDTH - FIELD_W) / 2 + FIELD_W:
            self.velocity_x = 0
            self.velocity_y = 0
            if self.x <= (SCREEN_WIDTH - FIELD_W) / 2:
                self.x = (SCREEN_WIDTH - FIELD_W) / 2
            else:
                self.x = (SCREEN_WIDTH - FIELD_W) / 2 + FIELD_W
        if self.y <= (SCREEN_HEIGHT - FIELD_H) / 2 or self.y >= (SCREEN_HEIGHT - FIELD_H) / 2 + FIELD_H:
            self.velocity_x = 0
            self.velocity_y = 0
            if self.y <= (SCREEN_HEIGHT - FIELD_H) / 2:
                self.y = (SCREEN_HEIGHT - FIELD_H) / 2
            else:
                self.y = (SCREEN_HEIGHT - FIELD_H) / 2 + FIELD_H'''

    def render(self, screen):
        # Render the ball on the screen
        ball_color = (255, 165, 0)  # Adjust the color as needed
        ball_radius = self.radius  # Adjust the radius as needed
        ball_pos = (int(self.x), int(self.y))
        pygame.draw.circle(screen, ball_color, ball_pos, ball_radius * (self.z * 0.01 + 1))

    def kick(self, angle, power, rId, speedX, speedY):
        # Perform the kick action based on the provided angle and power
        kick_speed = power  # Adjust the kick speed as needed
        self.velocity_x = kick_speed * math.cos(angle) + speedX
        self.velocity_y = kick_speed * math.sin(angle) + speedY
        self.velocity_z = 0
        self.kicked = True
        self.kicked_id = rId

    def kick_up(self, angle, up_angle, power, rId, speedX, speedY):
        # Perform the kick action based on the provided angle and power
        hor_speed = power * math.cos(up_angle)
        ver_speed = power * math.sin(up_angle) * 0.7
        self.velocity_x = hor_speed * math.cos(angle) + speedX
        self.velocity_y = hor_speed * math.sin(angle) + speedY
        self.velocity_z = ver_speed
        self.kicked = True
        self.kicked_id = rId

    def goto(self, point):
        self.x = point.x
        self.y = point.y
        self.velocity_x = 0
        self.velocity_y = 0
        self.kicked = False


class Goal:
    def __init__(self, x):
        self.x = x
        self.y = GOAL_Y_POSITION
        self.width = GOAL_WIDTH
        self.height = GOAL_HEIGHT
        self.depth = GOAL_DEPTH
        self.wall_thickness = GOAL_WALL_THICKNESS

    def render(self, screen):
        # Draw the goal as a rectangle
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.depth, self.width), LINE_THICKNESS, 0)

    def check_goal(self, ball):
        # Check if the ball is inside the goal
        if self.x < ball.x < self.x + self.depth and self.y < ball.y < self.y + self.width:
            return True
        return False


class Game:
    def __init__(self):
        pygame.init()
        window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(window_size)
        self.state = 'g'
        pygame.display.set_caption("SSL Simulator")

        self.clock = pygame.time.Clock()

        self.goals = [Goal(GOAL_1_X_POSITION), Goal(GOAL_2_X_POSITION)]

        self.lines = [
            pygame.Rect((SCREEN_WIDTH - FIELD_W) / 2, (SCREEN_HEIGHT - FIELD_H) / 2, FIELD_W, LINE_THICKNESS),
            pygame.Rect((SCREEN_WIDTH - FIELD_W) / 2, (SCREEN_HEIGHT - FIELD_H) / 2 + FIELD_H - LINE_THICKNESS, FIELD_W,
                        LINE_THICKNESS),
            pygame.Rect((SCREEN_WIDTH - FIELD_W) / 2, (SCREEN_HEIGHT - FIELD_H) / 2, LINE_THICKNESS, FIELD_H),
            pygame.Rect((SCREEN_WIDTH - FIELD_W) / 2 + FIELD_W - LINE_THICKNESS, (SCREEN_HEIGHT - FIELD_H) / 2,
                        LINE_THICKNESS, FIELD_H),
            pygame.Rect((SCREEN_WIDTH - FIELD_W) / 2, FIELD_H / 2 + (SCREEN_HEIGHT - FIELD_H) / 2, FIELD_W, LINE_THICKNESS),
            pygame.Rect(FIELD_W / 2 + (SCREEN_WIDTH - FIELD_W) / 2, (SCREEN_HEIGHT - FIELD_H) / 2, LINE_THICKNESS, FIELD_H),
            pygame.Rect(GOAL_WIDTH + (SCREEN_WIDTH - FIELD_W) / 2, FIELD_H / 2 - GOAL_WIDTH + (SCREEN_HEIGHT - FIELD_H) / 2, LINE_THICKNESS,
                        2 * GOAL_WIDTH),
            pygame.Rect(FIELD_W - GOAL_WIDTH + (SCREEN_WIDTH - FIELD_W) / 2,
                        FIELD_H / 2 - GOAL_WIDTH + (SCREEN_HEIGHT - FIELD_H) / 2, LINE_THICKNESS,
                        2 * GOAL_WIDTH),
            pygame.Rect((SCREEN_WIDTH - FIELD_W) / 2, FIELD_H / 2 + (SCREEN_HEIGHT - FIELD_H) / 2 - GOAL_WIDTH, GOAL_WIDTH,
                        LINE_THICKNESS),
            pygame.Rect((SCREEN_WIDTH - FIELD_W) / 2, 2 * GOAL_WIDTH + FIELD_H / 2 + (SCREEN_HEIGHT - FIELD_H) / 2 - GOAL_WIDTH,
                        GOAL_WIDTH,
                        LINE_THICKNESS),
            pygame.Rect(FIELD_W - GOAL_WIDTH + (SCREEN_WIDTH - FIELD_W) / 2, FIELD_H / 2 + (SCREEN_HEIGHT - FIELD_H) / 2 - GOAL_WIDTH,
                        GOAL_WIDTH,
                        LINE_THICKNESS),
            pygame.Rect(FIELD_W - GOAL_WIDTH + (SCREEN_WIDTH - FIELD_W) / 2,
                        2 * GOAL_WIDTH + FIELD_H / 2 + (SCREEN_HEIGHT - FIELD_H) / 2 - GOAL_WIDTH,
                        GOAL_WIDTH,
                        LINE_THICKNESS),
        ]

        # Create walls
        self.walls = [
            pygame.Rect(0, 0, SCREEN_WIDTH, WALL_THICKNESS),
            pygame.Rect(0, SCREEN_HEIGHT - WALL_THICKNESS, SCREEN_WIDTH, WALL_THICKNESS),
            pygame.Rect(0, 0, WALL_THICKNESS, SCREEN_HEIGHT),
            pygame.Rect(SCREEN_WIDTH - WALL_THICKNESS, 0, WALL_THICKNESS, SCREEN_HEIGHT)
        ]

        random.seed(30)
        robot1 = Robot(0, 100, 300, 0, 'b')  # Example robot position and orientation
        self.ball = Ball(800, 300)  # Example ball position

        self.robots = [robot1]  # Add more robots as needed

        for i in range(11):
            if i < 6:
                self.robots.append(Robot(i + 1, 900, 200 + robot1.size * i * 2, 0, 'y'))
            else:
                self.robots.append(Robot(i + 1, 900, 200 + robot1.size * i * 2, 0, 'b'))

        self.running = True

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    self.ball.goto(auxiliary.Point(x, y))
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_g:
                        game.state = 'g'
                    if event.key == pygame.K_h:
                        game.state = 'h'

            # Clear the screen
            self.screen.fill((0, 170, 0))  # Set background color

            # Draw walls
            for wall in self.walls:
                pygame.draw.rect(self.screen, (0, 0, 0), wall)

            for line in self.lines:
                pygame.draw.rect(self.screen, (255, 255, 255), line)

            for goal in self.goals:
                goal.render(self.screen)
                if goal.check_goal(self.ball):
                    print("Goal!")

            pygame.draw.circle(self.screen, (255, 255, 255), (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2), 500 * SCALE, LINE_THICKNESS)

            if self.state == 'g':
                # Start of robot control
                self.robots[0].drive_to_ball(self.ball, self.robots)
                # self.robots[0].go_to_point(self.ball)
                # for i in range(11):
                #   self.robots[i+1].go_to_point(auxiliary.Point(900, 200 + self.robots[0].size * i * 2))
                # End of robot control
                #   for robot in self.robots:
                #       robot.drive_to_ball(self.ball, self.robots)
            elif self.state == 'h':
                for robot in self.robots:
                    robot.speedR = 0
                    robot.speedX = 0
                    robot.speedY = 0

            for robot in self.robots:
                robot.update(self.robots, self.ball)
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
