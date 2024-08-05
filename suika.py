import pygame
import math
import random
import pymunk
import pymunk.pygame_util

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 500, 720
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Suika')

# Clock for FPS control
timer = pygame.time.Clock()

# Game Variables
WALL_THICKNESS = 10
WALL_THRESHOLD = 110
COOLDOWN_TIME = 500  # Buffer before each shot

last_shot_time = 0
balls = []

# Ball Colors
colors = {
    'yellow': (255, 255, 186),
    'orange': (255, 223, 186),
    'red': (255, 179, 186),
    'blue': (186, 225, 255),
    'green': (186, 255, 201),
    'purple': (195, 177, 225),
    'dark_green': (184, 216, 190),
    'dark_blue': (62, 71, 114),
    'pink': (248, 200, 220),
    'lavender': (230, 230, 250),
    'crimson': (220, 20, 60),
    'gold': (255, 215, 0)
}

# Balls allowed to be dispensed from player
BALL_COLORS = [colors['yellow'], colors['orange'], colors['red']]

# Order of evolution
COLOR_TRANSITIONS = {
    colors['yellow']: colors['orange'],
    colors['orange']: colors['red'],
    colors['red']: colors['blue'],
    colors['blue']: colors['purple'],
    colors['purple']: colors['dark_green'],
    colors['dark_green']: colors['dark_blue'],
    colors['dark_blue']: colors['pink'],
    colors['pink']: colors['lavender'],
    colors['lavender']: colors['crimson'],
    colors['crimson']: colors['gold']
}

# Size of each ball
COLOR_RADIUS = {
    colors['yellow']: 10,
    colors['orange']: 20,
    colors['red']: 40,
    colors['blue']: 50,
    colors['purple']: 60,
    colors['green']: 70,
    colors['dark_green']: 80,
    colors['dark_blue']: 100,
    colors['pink']: 120,
    colors['lavender']: 130,
    colors['crimson']: 150,
    colors['gold']: 180
}

# Score gain from each ball merge
COLOR_SCORES = {
    colors['yellow']: 10,
    colors['orange']: 20,
    colors['red']: 30,
    colors['blue']: 40,
    colors['purple']: 50,
    colors['green']: 60,
    colors['dark_green']: 70,
    colors['dark_blue']: 80,
    colors['pink']: 90,
    colors['lavender']: 100,
    colors['crimson']: 110,
    colors['gold']: 120
}

# Initialize Pymunk Space
space = pymunk.Space()
space.gravity = (0, 400)  # Reduced gravity

# Create walls
static_lines = [
    pymunk.Segment(space.static_body, (0, 0), (0, HEIGHT), WALL_THICKNESS),  # Left wall
    pymunk.Segment(space.static_body, (WIDTH, 0), (WIDTH, HEIGHT), WALL_THICKNESS),  # Right wall
    pymunk.Segment(space.static_body, (0, 0), (WIDTH, 0), WALL_THICKNESS),  # Top wall
    pymunk.Segment(space.static_body, (0, HEIGHT), (WIDTH, HEIGHT), WALL_THICKNESS)  # Bottom wall
]
for line in static_lines:
    line.elasticity = 0.2
    line.friction = 1.0
    space.add(line)

# Create box (container)
box_left = WALL_THICKNESS + 15
box_right = WIDTH - WALL_THICKNESS - 15
box_top = WALL_THICKNESS + 100
box_bottom = HEIGHT - WALL_THICKNESS - 15

box_lines = [
    pymunk.Segment(space.static_body, (box_left, box_top), (box_left, box_bottom + 5), WALL_THICKNESS),  # Left wall
    pymunk.Segment(space.static_body, (box_right, box_top), (box_right, box_bottom + 5), WALL_THICKNESS),  # Right wall
    pymunk.Segment(space.static_body, (box_left, box_bottom), (box_right, box_bottom), WALL_THICKNESS)  # Bottom floor
]
for line in box_lines:
    line.elasticity = 0.2
    line.friction = 1.0
    space.add(line)

# Player Class
class Player:
    def __init__(self, x_pos, y_pos, score, image_path):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.score = score
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(topleft=(x_pos, y_pos))

    def draw(self):
        screen.blit(self.image, self.rect)

    def move(self, dx):
        self.x_pos += dx
        self.x_pos = max(WALL_THICKNESS - 10, min(WIDTH - WALL_THICKNESS + 10 - self.rect.width, self.x_pos))
        self.rect.topleft = (self.x_pos, self.y_pos)

    def increase_score(self, points):
        self.score += points

# Instantiate the Player object
player = Player(210, 0, 0, 'images/panda.png')

# Ball Class
class Ball:
    def __init__(self, x_pos, y_pos, radius, color):
        self.body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, radius))
        self.body.position = x_pos, y_pos
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.color = color
        self.shape.elasticity = 0.2
        self.shape.friction = 0.5
        space.add(self.body, self.shape)

    def draw(self):
        x, y = self.body.position
        pygame.draw.circle(screen, self.shape.color, (int(x), int(y+4)), int(self.shape.radius))

    def handle_collision(self, other):
        dx = other.body.position.x - self.body.position.x
        dy = other.body.position.y - self.body.position.y
        distance = math.hypot(dx, dy)

        if distance < self.shape.radius + other.shape.radius:
            if self.shape.color == other.shape.color and self.shape.color in COLOR_TRANSITIONS:
                new_ball = self.merge_with(other)
                score_increase = COLOR_SCORES.get(self.shape.color, 0)
                player.increase_score(score_increase)
                return new_ball
        return None

    def merge_with(self, other):
        new_x_pos = (self.body.position.x + other.body.position.x) / 2
        new_y_pos = (self.body.position.y + other.body.position.y) / 2
        new_color = COLOR_TRANSITIONS[self.shape.color]
        new_radius = COLOR_RADIUS[new_color]
        return Ball(new_x_pos, new_y_pos, new_radius, new_color)

def create_random_ball():
    x_pos = player.rect.centerx
    y_pos = player.rect.centery
    color = random.choice(BALL_COLORS)
    radius = COLOR_RADIUS[color]
    return Ball(x_pos, y_pos, radius, color)

preview_ball = create_random_ball()

# Drawing Functions
def draw_lines(lines):
    for line in lines:
        body = line.body
        pv1 = body.position + line.a.rotated(body.angle)
        pv2 = body.position + line.b.rotated(body.angle)
        pygame.draw.lines(screen, (139, 69, 19), False, [pv1, pv2], WALL_THICKNESS)

def update_preview_ball_position():
    preview_ball.body.position = player.rect.centerx, player.rect.centery + 50

def draw_preview_ball():
    preview_ball.draw()

def draw_score():
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {player.score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))

def draw_dotted_vertical_line(color, x_pos, start_y, end_y, dot_length, gap_length):
    current_y = start_y
    while current_y < end_y:
        dot_end_y = min(current_y + dot_length, end_y)
        pygame.draw.line(screen, color, (x_pos, current_y), (x_pos, dot_end_y), 5)
        current_y = dot_end_y + gap_length

# Game Loop
running = True
while running:
    screen.fill((242, 196, 171))
    draw_lines(static_lines)
    draw_lines(box_lines)
    draw_dotted_vertical_line((0, 0, 0), player.rect.x + 49, player.rect.y + 100, box_bottom - 10, 5, 20)

    current_time = pygame.time.get_ticks()
    can_shoot = (current_time - last_shot_time >= COOLDOWN_TIME)

    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and can_shoot:
                balls.append(preview_ball)
                preview_ball = create_random_ball()
                last_shot_time = current_time

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move(-3)
    if keys[pygame.K_RIGHT]:
        player.move(3)

    update_preview_ball_position()
    player.draw()
    draw_preview_ball()

    balls_to_remove = []
    balls_to_add = []

    for i, ball in enumerate(balls):
        ball.draw()

        if ball.body.position.y + ball.shape.radius < WALL_THRESHOLD:
            print("Game Over!")
            running = False
            break

        for j in range(i + 1, len(balls)):
            result = ball.handle_collision(balls[j])
            if result:
                if ball not in balls_to_remove:
                    balls_to_remove.append(ball)
                if balls[j] not in balls_to_remove:
                    balls_to_remove.append(balls[j])
                balls_to_add.append(result)

    # Safely remove balls
    removed_balls = set()
    for ball in balls_to_remove:
        if ball not in removed_balls
            removed_balls.add(ball)
            if ball.body in space.bodies:
                space.remove(ball.body, ball.shape)
            balls.remove(ball)

    balls.extend(balls_to_add)

    draw_score()
    space.step(1/60.0)
    pygame.display.flip()
    timer.tick(60)

pygame.quit()
