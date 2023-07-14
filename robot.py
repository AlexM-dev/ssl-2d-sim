import const
import auxiliary
import math


class Robot:
    def __init__(self, r_id, x, y, angle, team):
        self.rId = r_id
        self.x = x
        self.y = y
        self.size = 180 * const.SCALE
        self.height = 150 * const.SCALE
        self.maxSpeed = 6 * 1000 * const.SCALE
        self.maxSpeedR = 10
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

        self.kick_power = 25000 * const.SCALE
        self.mass = 5.0  # Robot mass
        self.friction = 15.1  # Friction coefficient
        self.up_kick_angle = auxiliary.format_angle(45 / (180 / math.pi))

    def update(self, robots, ball, dt):
        self.handle_collisions(robots, ball)

        if self.x <= const.WALL_THICKNESS:
            self.x = const.WALL_THICKNESS
            self.speedX = -self.speedX
        elif self.x >= const.SCREEN_WIDTH - const.WALL_THICKNESS:
            self.x = const.SCREEN_WIDTH - const.WALL_THICKNESS
            self.speedX = -self.speedX

        if self.y <= const.WALL_THICKNESS:
            self.y = const.WALL_THICKNESS
            self.speedY = -self.speedY
        elif self.y >= const.SCREEN_HEIGHT - const.WALL_THICKNESS:
            self.y = const.SCREEN_HEIGHT - const.WALL_THICKNESS
            self.speedY = -self.speedY

        if (self.speedX ** 2 + self.speedY ** 2) ** 0.5 > self.maxSpeed:
            tempAng = math.atan2(self.speedY, self.speedX)
            self.speedX = self.maxSpeed * math.cos(tempAng)
            self.speedY = self.maxSpeed * math.sin(tempAng)

        self.x += self.speedX * dt
        self.y += self.speedY * dt

        if self.speedR > self.maxSpeedR:
            self.speedR = self.maxSpeedR
        if self.speedR < -self.maxSpeedR:
            self.speedR = -self.maxSpeedR
        self.angle += self.speedR * dt

        self.apply_friction(dt)

    def apply_friction(self, dt):
        self.speedX *= math.exp(-self.friction * dt)
        self.speedY *= math.exp(-self.friction * dt)
        self.speedR *= math.exp(-self.friction * dt)

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
                if abs(auxiliary.format_angle(self.angle - angle)) < 10 / (180 / math.pi):
                    ball_speed = ((ball.velocity_x ** 2 + ball.velocity_y ** 2) ** 0.5) * 0.5
                else:
                    ball_speed = ((ball.velocity_x ** 2 + ball.velocity_y ** 2) ** 0.5) * 0.9
                ball.velocity_x = ball_speed * math.cos(angle)
                ball.velocity_y = ball_speed * math.sin(angle)
            else:
                overlap_x = 0.5 * overlap * math.cos(angle)
                overlap_y = 0.5 * overlap * math.sin(angle)
                ball.x += overlap_x
                ball.y += overlap_y

    def go_to_point(self, point):
        # Calculate the angle to the ball
        angle_to_point = math.atan2(point.y - self.y, point.x - self.x)

        # Calculate the distance to the ball
        distance_to_point = math.dist((self.x, self.y), (point.x, point.y))

        self.speedX = distance_to_point * math.cos(angle_to_point) * 10
        self.speedY = distance_to_point * math.sin(angle_to_point) * 10

    def rotate_to_point(self, point):
        vx = self.x - point.x
        vy = self.y - point.y
        ux = -math.cos(self.angle)
        uy = -math.sin(self.angle)
        dif = -math.atan2(auxiliary.scal_mult(auxiliary.Point(vx, vy), auxiliary.Point(ux, uy)),
                          auxiliary.vect_mult(auxiliary.Point(vx, vy), auxiliary.Point(ux, uy)))
        if abs(dif) > 0.1:
            self.speedR = dif * 7
        else:
            self.speedR = 0

    def drive_to_ball(self, ball, robots=None):
        # Calculate the distance to the ball
        if robots is None:
            pass
        distance_to_ball = math.hypot(ball.x - self.x, ball.y - self.y)

        self.rotate_to_point(ball)
        if distance_to_ball > (self.size + ball.radius):  # Adjust the threshold as needed
            # Move towards the ball
            self.go_to_point(ball)
        else:
            self.kick_ball(ball)

    def kick_ball(self, ball):
        # Calculate the angle to the ball
        angle_to_ball = auxiliary.format_angle(math.atan2(ball.y - self.y, ball.x - self.x) - self.angle)

        # Calculate the distance to the ball
        distance_to_ball = math.hypot(ball.x - self.x, ball.y - self.y)

        if abs(angle_to_ball) < 10 / (180 / math.pi) and distance_to_ball < (
                self.size + ball.radius) * 1.15 and ball.z == 0:
            # ball.kick_up(self.angle, self.up_kick_angle, self.kick_power, self.rId, self.speedX, self.speedY)
            ball.kick(self.angle, self.kick_power, self.rId, self.speedX, self.speedY)

    def drive_to_ball_and_kick_to_point(self, ball, point, robots=None):
        # Calculate the angle to the ball
        self.rotate_to_point(point)
        target_angle = math.atan2(ball.y - point.y, ball.x - point.x)
        target_x = ball.x + (ball.radius + self.size) * 5 * math.cos(target_angle)
        target_y = ball.y + (ball.radius + self.size) * 5 * math.sin(target_angle)

        distance_to_ball = math.hypot(ball.x - self.x, ball.y - self.y)
        if distance_to_ball > (self.size + ball.radius):  # Adjust the threshold as needed
            # Move towards the ball
            print(auxiliary.format_angle(math.atan2(ball.y - self.y, ball.x - self.x) - self.angle))
            if abs(auxiliary.format_angle(math.atan2(ball.y - self.y, ball.x - self.x) - self.angle)) < 20 / (180 / math.pi):
                self.drive_to_ball(ball)
            else:
                self.go_to_point(auxiliary.Point(target_x, target_y))
        else:
            self.kick_ball(ball)
