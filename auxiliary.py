import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    def __init__(self, start_x, start_y, end_x, end_y):
        self.startX = start_x
        self.startY = start_y
        self.endX = end_x
        self.endY = end_y


class Circle:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius


def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def construct_tangents(robot, obstacle):
    tangents = []

    robot_to_obstacle = math.hypot(obstacle.x - robot.x, obstacle.y - robot.y)
    robot_radius = robot.size

    if robot_to_obstacle <= 2 * robot_radius:
        return tangents

    # Calculate the angle between the robot and the obstacle
    angle_to_obstacle = math.atan2(obstacle.y - robot.y, obstacle.x - robot.x)

    # Calculate the tangent angles
    tangent_angle_1 = angle_to_obstacle + math.asin(2 * robot_radius / robot_to_obstacle)
    tangent_angle_2 = angle_to_obstacle - math.asin(2 * robot_radius / robot_to_obstacle)

    # Calculate the tangent points
    tangent_point_1 = Point(robot.x + robot_radius * math.cos(tangent_angle_1),
                            robot.y + robot_radius * math.sin(tangent_angle_1))

    tangent_point_2 = Point(robot.x + robot_radius * math.cos(tangent_angle_2),
                            robot.y + robot_radius * math.sin(tangent_angle_2))

    # Create tangent lines
    tangent_line_1 = Line(robot.x, robot.y, tangent_point_1.x, tangent_point_1.y)
    tangent_line_2 = Line(robot.x, robot.y, tangent_point_2.x, tangent_point_2.y)

    tangents.append(tangent_line_1)
    tangents.append(tangent_line_2)

    return tangents


def calculate_path_length(start_point, end_point, obstacles):
    path_length = math.hypot(end_point.x - start_point.x, end_point.y - start_point.y)

    for obstacle in obstacles:
        tangents = construct_tangents(start_point, obstacle)

        for tangent in tangents:
            intersection_point = get_line_intersection(start_point, end_point, Point(tangent.startX, tangent.startY),
                                                       Point(tangent.endX, tangent.endY))

            if intersection_point:
                partial_path_length = math.hypot(intersection_point.x - start_point.x,
                                                 intersection_point.y - start_point.y)

                if partial_path_length < path_length:
                    path_length = partial_path_length

    return path_length


def get_line_intersection(line1_start, line1_end, line2_start, line2_end):
    # Calculate the differences
    delta_x1 = line1_end.x - line1_start.x
    delta_y1 = line1_end.y - line1_start.y
    delta_x2 = line2_end.x - line2_start.x
    delta_y2 = line2_end.y - line2_start.y

    # Calculate the determinants
    determinant = delta_x1 * delta_y2 - delta_x2 * delta_y1

    if determinant == 0:
        # The lines are parallel or coincident
        return None

    # Calculate the differences between the start points
    delta_x_start = line1_start.x - line2_start.x
    delta_y_start = line1_start.y - line2_start.y

    # Calculate the t parameters
    t1 = (delta_x_start * delta_y2 - delta_x2 * delta_y_start) / determinant
    t2 = (delta_x_start * delta_y1 - delta_x1 * delta_y_start) / determinant

    if 0 <= t1 <= 1 and 0 <= t2 <= 1:
        # The lines intersect within their segments
        intersection_x = line1_start.x + t1 * delta_x1
        intersection_y = line1_start.y + t1 * delta_y1
        return Point(intersection_x, intersection_y)

    # The lines do not intersect within their segments
    return None


def vect_mult(v, u):
    return v.x * u.x + v.y * u.y


def scal_mult(v, u):
    return v.x * u.y - v.y * u.x


def format_angle(ang):
    while ang > math.pi:
        ang -= 2 * math.pi
    while ang < -math.pi:
        ang += 2 * math.pi
    return ang
