import pygame
from pygame.locals import *
import math
import random
import auxiliary
import const
import robot


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = 0  # z position of the ball
        self.velocity_x = 0
        self.velocity_y = 0
        self.velocity_z = 0  # z-axis velocity
        self.radius = 43 * const.SCALE
        self.kicked = False
        self.kicked_id = 0

        self.mass = 0.046  # Ball mass
        self.friction = 1.75  # Friction coefficient
        self.air_resistance = 1.05  # Air resistance coefficient
        self.gravity = 9.81 * const.SCALE  # Gravitational acceleration

    def update(self, goals, dt):
        self.handle_goal_collisions(goals)
        if self.z > 0:
            # Apply friction and air resistance
            self.velocity_x *= math.exp(-self.air_resistance * dt)
            self.velocity_y *= math.exp(-self.air_resistance * dt)
            self.velocity_z *= math.exp(-self.air_resistance * dt)
        else:
            self.velocity_x *= math.exp(-(self.friction + self.air_resistance) * dt)
            self.velocity_y *= math.exp(-(self.friction + self.air_resistance) * dt)
            self.velocity_z *= math.exp(-self.air_resistance * dt)

        # Apply gravity effect
        self.velocity_z -= self.gravity
        # Update the ball's position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        self.z += self.velocity_z * dt  # Update z position
        if self.z < 0:
            self.z = 0  # The ball should not go below the ground level
            self.velocity_z = 0

        # Check ball collision with walls
        if self.x <= const.WALL_THICKNESS or self.x >= const.SCREEN_WIDTH - const.WALL_THICKNESS:
            self.velocity_x *= -1  # Reverse x velocity
        if self.y <= const.WALL_THICKNESS or self.y >= const.SCREEN_HEIGHT - const.WALL_THICKNESS:
            self.velocity_y *= -1  # Reverse y velocity

        '''if self.x <= (const.SCREEN_WIDTH - const.FIELD_W) / 2 or self.x >= (const.SCREEN_WIDTH - const.FIELD_W) / 2 + const.FIELD_W:
            self.velocity_x = 0
            self.velocity_y = 0
            if self.x <= (const.SCREEN_WIDTH - const.FIELD_W) / 2:
                self.x = (const.SCREEN_WIDTH - const.FIELD_W) / 2
            else:
                self.x = (const.SCREEN_WIDTH - const.FIELD_W) / 2 + const.FIELD_W
        if self.y <= (const.SCREEN_HEIGHT - const.FIELD_H) / 2 or self.y >= (const.SCREEN_HEIGHT - const.FIELD_H) / 2 + const.FIELD_H:
            self.velocity_x = 0
            self.velocity_y = 0
            if self.y <= (const.SCREEN_HEIGHT - const.FIELD_H) / 2:
                self.y = (const.SCREEN_HEIGHT - const.FIELD_H) / 2
            else:
                self.y = (const.SCREEN_HEIGHT - const.FIELD_H) / 2 + const.FIELD_H'''

    def handle_goal_collisions(self, goals):
        for goal in goals:
            if goal.x <= self.x <= goal.x + goal.depth and goal.y <= self.y <= goal.y + goal.width:
                # The robot is inside the goal, so we reverse its speed
                self.velocity_x = -self.velocity_x
                self.velocity_y = -self.velocity_y

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
        print(self.velocity_x, self.velocity_y)

    def kick_up(self, angle, up_angle, power, rId, speedX, speedY):
        # Perform the kick action based on the provided angle and power
        hor_speed = power * math.cos(up_angle) * 0.5
        ver_speed = power * math.sin(up_angle) * 0.5
        self.velocity_x = hor_speed * math.cos(angle) + speedX
        self.velocity_y = hor_speed * math.sin(angle) + speedY
        self.velocity_z = ver_speed
        self.kicked = True
        self.kicked_id = rId
        print()

    def goto(self, point):
        self.x = point.x
        self.y = point.y
        self.velocity_x = 0
        self.velocity_y = 0
        self.kicked = False


class Goal:
    def __init__(self, x):
        self.x = x
        self.y = const.GOAL_Y_POSITION
        self.width = const.GOAL_WIDTH
        self.height = const.GOAL_HEIGHT
        self.depth = const.GOAL_DEPTH
        self.WALL_THICKNESS = const.WALL_THICKNESS

    def render(self, screen):
        # Draw the goal as a rectangle
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.depth, self.width), const.LINE_THICKNESS, 0)

    def check_goal(self, ball):
        # Check if the ball is inside the goal
        if self.x < ball.x < self.x + self.depth and self.y < ball.y < self.y + self.width:
            return True
        return False


class PenaltyArea:
    def __init__(self, x):
        self.x = x
        self.y = const.GOAL_Y_POSITION - const.GOAL_WIDTH / 2
        self.width = const.GOAL_WIDTH
        self.height = const.GOAL_WIDTH * 2

    def render(self, screen):
        # Draw the penalty area as a rectangle
        pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.width, self.height), const.LINE_THICKNESS, 0)

    def is_inside(self, x, y):
        # Check if a point is inside the penalty area
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height


class Game:
    def __init__(self):
        pygame.init()
        window_size = (const.SCREEN_WIDTH, const.SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(window_size)
        self.state = 'g'
        pygame.display.set_caption("SSL Simulator")
        self.font = pygame.font.SysFont('Calibri', 25, True, False)
        self.txt = ''

        self.cur_update_time = pygame.time.get_ticks()

        self.clock = pygame.time.Clock()

        self.goals = [Goal(const.GOAL_1_X_POSITION), Goal(const.GOAL_2_X_POSITION)]

        self.penalty_areas = [PenaltyArea(const.GOAL_1_X_POSITION + const.GOAL_DEPTH), PenaltyArea(const.GOAL_2_X_POSITION - const.GOAL_WIDTH)]

        self.lines = [
            pygame.Rect((const.SCREEN_WIDTH - const.FIELD_W) / 2, (const.SCREEN_HEIGHT - const.FIELD_H) / 2, const.FIELD_W, const.LINE_THICKNESS),
            pygame.Rect((const.SCREEN_WIDTH - const.FIELD_W) / 2, (const.SCREEN_HEIGHT - const.FIELD_H) / 2 + const.FIELD_H - const.LINE_THICKNESS, const.FIELD_W,
                        const.LINE_THICKNESS),
            pygame.Rect((const.SCREEN_WIDTH - const.FIELD_W) / 2, (const.SCREEN_HEIGHT - const.FIELD_H) / 2, const.LINE_THICKNESS, const.FIELD_H),
            pygame.Rect((const.SCREEN_WIDTH - const.FIELD_W) / 2 + const.FIELD_W - const.LINE_THICKNESS, (const.SCREEN_HEIGHT - const.FIELD_H) / 2,
                        const.LINE_THICKNESS, const.FIELD_H),
            pygame.Rect((const.SCREEN_WIDTH - const.FIELD_W) / 2, const.FIELD_H / 2 + (const.SCREEN_HEIGHT - const.FIELD_H) / 2, const.FIELD_W,
                        const.LINE_THICKNESS),
            pygame.Rect(const.FIELD_W / 2 + (const.SCREEN_WIDTH - const.FIELD_W) / 2, (const.SCREEN_HEIGHT - const.FIELD_H) / 2, const.LINE_THICKNESS,
                        const.FIELD_H),
            pygame.Rect(const.GOAL_WIDTH + (const.SCREEN_WIDTH - const.FIELD_W) / 2,
                        const.FIELD_H / 2 - const.GOAL_WIDTH + (const.SCREEN_HEIGHT - const.FIELD_H) / 2, const.LINE_THICKNESS,
                        2 * const.GOAL_WIDTH),
            pygame.Rect(const.FIELD_W - const.GOAL_WIDTH + (const.SCREEN_WIDTH - const.FIELD_W) / 2,
                        const.FIELD_H / 2 - const.GOAL_WIDTH + (const.SCREEN_HEIGHT - const.FIELD_H) / 2, const.LINE_THICKNESS,
                        2 * const.GOAL_WIDTH),
            pygame.Rect((const.SCREEN_WIDTH - const.FIELD_W) / 2, const.FIELD_H / 2 + (const.SCREEN_HEIGHT - const.FIELD_H) / 2 - const.GOAL_WIDTH,
                        const.GOAL_WIDTH,
                        const.LINE_THICKNESS),
            pygame.Rect((const.SCREEN_WIDTH - const.FIELD_W) / 2,
                        2 * const.GOAL_WIDTH + const.FIELD_H / 2 + (const.SCREEN_HEIGHT - const.FIELD_H) / 2 - const.GOAL_WIDTH,
                        const.GOAL_WIDTH,
                        const.LINE_THICKNESS),
            pygame.Rect(const.FIELD_W - const.GOAL_WIDTH + (const.SCREEN_WIDTH - const.FIELD_W) / 2,
                        const.FIELD_H / 2 + (const.SCREEN_HEIGHT - const.FIELD_H) / 2 - const.GOAL_WIDTH,
                        const.GOAL_WIDTH,
                        const.LINE_THICKNESS),
            pygame.Rect(const.FIELD_W - const.GOAL_WIDTH + (const.SCREEN_WIDTH - const.FIELD_W) / 2,
                        2 * const.GOAL_WIDTH + const.FIELD_H / 2 + (const.SCREEN_HEIGHT - const.FIELD_H) / 2 - const.GOAL_WIDTH,
                        const.GOAL_WIDTH,
                        const.LINE_THICKNESS),
        ]

        # Create walls
        self.walls = [
            pygame.Rect(0, 0, const.SCREEN_WIDTH, const.WALL_THICKNESS),
            pygame.Rect(0, const.SCREEN_HEIGHT - const.WALL_THICKNESS, const.SCREEN_WIDTH, const.WALL_THICKNESS),
            pygame.Rect(0, 0, const.WALL_THICKNESS, const.SCREEN_HEIGHT),
            pygame.Rect(const.SCREEN_WIDTH - const.WALL_THICKNESS, 0, const.WALL_THICKNESS, const.SCREEN_HEIGHT)
        ]

        random.seed(30)
        robot1 = robot.Robot(0, const.SCREEN_WIDTH - 600, 370, 0, 'b')  # Example robot position and orientation
        self.ball = Ball(800, 300)  # Example ball position

        self.robots = [robot1]  # Add more robots as needed

        self.robots.append(robot.Robot(1, 100, 370, 0, 'b'))
        self.robots.append(robot.Robot(2, 250, 570, 0, 'b'))
        self.robots.append(robot.Robot(3, 250, 170, 0, 'b'))
        self.robots.append(robot.Robot(4, 350, 470, 0, 'b'))
        self.robots.append(robot.Robot(5, 350, 270, 0, 'b'))

        self.robots.append(robot.Robot(6, const.SCREEN_WIDTH - 100, 370, math.pi, 'y'))
        self.robots.append(robot.Robot(7, const.SCREEN_WIDTH - 250, 570, math.pi, 'y'))
        self.robots.append(robot.Robot(8, const.SCREEN_WIDTH - 250, 170, math.pi, 'y'))
        self.robots.append(robot.Robot(9, const.SCREEN_WIDTH - 350, 470, math.pi, 'y'))
        self.robots.append(robot.Robot(10, const.SCREEN_WIDTH - 350, 270, math.pi, 'y'))
        self.robots.append(robot.Robot(11, 600, 370, math.pi, 'y'))

        self.gks = [1, 6]

        self.running = True

    def run(self):
        while self.running:
            if self.state == 'g':
                text = ''
            # Get delta time in seconds
            dt = self.clock.get_time() / 1000

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

            for penalty_area in self.penalty_areas:
                penalty_area.render(self.screen)

            for goal in self.goals:
                goal.render(self.screen)
                if goal.check_goal(self.ball):
                    if game.state == 'g':
                        print("Goal!")
                        text += "Goal! "
                        game.state = 'h'

            if self.ball.x <= (const.SCREEN_WIDTH - const.FIELD_W) / 2 or self.ball.x >= (const.SCREEN_WIDTH - const.FIELD_W) / 2 + const.FIELD_W or \
                    self.ball.y <= (const.SCREEN_HEIGHT - const.FIELD_H) / 2 or self.ball.y >= (const.SCREEN_HEIGHT - const.FIELD_H) / 2 + const.FIELD_H:
                if game.state == 'g':
                    print("Out ot bounce!")
                    text += "Out ot bounce! "
                    game.state = 'h'

            pygame.draw.circle(self.screen, (255, 255, 255), (const.SCREEN_WIDTH / 2, const.SCREEN_HEIGHT / 2), 500 * const.SCALE,
                               const.LINE_THICKNESS)

            if self.state == 'g':
                #self.robots[0].go_to_point(self.ball)
                # Start of robot control
                self.robots[0].drive_to_ball(self.ball, self.robots)
                # self.robots[0].drive_to_ball_and_kick_to_point(self.ball, auxiliary.Point(0, 0))
                # for i in range(11):
                #   self.robots[i+1].go_to_point(auxiliary.Point(900, 200 + self.robots[0].size * i * 2))
                # End of robot control
                #   for robot in self.robots:
                #       robot.drive_to_ball(self.ball, self.robots)
            elif self.state == 'h':
                for r in self.robots:
                    r.speedR = 0
                    r.speedX = 0
                    r.speedY = 0

            # Update robot and ball(also try to fix tunneling)
            for r in self.robots:
                r.update(self.robots, self.ball, dt)
            self.ball.update(self.goals, dt)

            for r in self.robots:
                self.render_robot(r)

            # Render the ball
            self.ball.render(self.screen)

            # Check robots in penalty area
            violators = list(set(self.get_robots_in_penalty_area()) & set(self.get_robots_touching_ball()))
            for gk in self.gks:
                if gk in violators:
                    violators.remove(gk)
            if len(violators) > 0 and game.state == 'g':
                text += f'Robots {violators} break rules! '
                print("Robots", violators, "break rules")
                game.state = 'h'

            self.screen.blit(self.font.render(text, True, (0, 0, 0)), [0, 0])
            # Update the display
            pygame.display.flip()

            # Set the desired frames per second
            self.clock.tick()  # Adjust the FPS as needed

        pygame.quit()

    def get_robots_in_penalty_area(self):
        ids = []
        for r in self.robots:
            for penalty_area in self.penalty_areas:
                if penalty_area.is_inside(r.x, r.y):
                    ids.append(r.rId)
        return ids

    def get_robots_touching_ball(self):
        ids = []
        for r in self.robots:
            if auxiliary.dist(self.ball, r) < (self.ball.radius + r.size) * 1.15 and self.ball.z <= r.height:
                ids.append(r.rId)
        return ids

    def render_robot(self, r):
        # Calculate the endpoint of the direction indicator
        direction_x = r.x + r.direction_indicator_length * math.cos(r.angle)
        direction_y = r.y + r.direction_indicator_length * math.sin(r.angle)

        # Draw the direction indicator as a line
        pygame.draw.line(self.screen, r.color, (int(r.x), int(r.y)), (int(direction_x), int(direction_y)), 3)

        # Draw the robot as a circle
        pygame.draw.circle(self.screen, r.color, (int(r.x), int(r.y)), r.size)


if __name__ == "__main__":
    game = Game()
    game.run()
