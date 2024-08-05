import pygame
import math
import random

pygame.init()

#Screen & Name Logic
WIDTH, HEIGHT = 500, 720
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('suika')

#Clock
timer = pygame.time.Clock()

#Game Variables
WALL_THICKNESS = 10 
WALL_THRESHOLD = 110

#Ball Colors that will be encountered throughout gameplay
yellow = (255, 255, 186)
orange = (255, 223, 186)
red = (255, 179, 186)
blue = (186, 225, 255)
green = (186, 255, 201)
purple = (195, 177, 225)
dark_green = (184, 216, 190)
dark_blue = (62, 71, 114)
pink = (248, 200, 220)
lavender = (230, 230, 250)
crimson = (220, 20, 60)
gold = (255, 215, 0)

#Balls allowed to be dispensed from player
BALL_COLOR = [yellow,orange,red]

#Order of evolution
COLOR_TRANSITIONS = {
    yellow: orange,
    orange: red,
    red: blue,
    blue: purple,
    purple: green,
    green: dark_green,
    dark_green: dark_blue,
    dark_blue: pink,
    pink: lavender,
    lavender: crimson,
    crimson: gold
}

#Size of each ball
COLOR_RADIUS = {
    yellow: 10,
    orange: 20,
    red: 40,
    blue: 50,
    purple: 60,
    green: 70,
    dark_green: 80,
    dark_blue: 100,
    pink: 120,
    lavender: 130,
    crimson: 150,
    gold: 180
}

#Score gain from each ball merge
COLOR_SCORES = {
    yellow: 10,
    orange: 20,
    red: 30,
    blue: 40,
    purple: 50,
    green: 60,
    dark_green: 70,
    dark_blue: 80,
    pink: 90,
    lavender: 100,
    crimson: 110,
    gold: 120
}

#Game Variables
bottom = HEIGHT - WALL_THICKNESS - 15
box_left = WALL_THICKNESS + 15
box_right = WIDTH - WALL_THICKNESS - 15

gravity = 0.40
friction = 0.99999
bounce_stop = 0.3

cooldown_time = 500 #Buffer before each shot
last_shot_time = 0

balls = []

#Player Class
class Player:
    def __init__(self, x_pos, y_pos, score, image_path):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.score = score
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect(topleft=(x_pos, y_pos))

    #Draws the player icon on the screen
    def draw(self, screen):
        screen.blit(self.image, self.rect)

    #Moves the player ONLY in the horizontal
    def move(self, dx):
        self.x_pos += dx
        # Restrict movement to container area
        self.x_pos = max(WALL_THICKNESS - 10, min(WIDTH - WALL_THICKNESS + 10 - self.rect.width, self.x_pos))
        self.rect.topleft = (self.x_pos, self.y_pos)

    def increase_score(self, points):
        self.score += points

#Instantiate the Player object
player = Player(210, 0, 0, 'images/panda.png')

#Ball Class
class Ball:
    def __init__(self, x_pos, y_pos, radius, color, retention, y_speed, x_speed):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.radius = radius
        self.color = color
        self.retention = retention
        self.y_speed = y_speed
        self.x_speed = x_speed

    #Main function that creates the ball
    def create(self):
        pygame.draw.circle(screen, self.color, (self.x_pos, self.y_pos-4), self.radius)

    #Checks and applies gravity if they are above the bottom floor
    def check_gravity(self):
        if self.y_pos + self.radius < bottom:
            self.y_speed += gravity
        else: #allows the ball to 'bounce' once hitting the ground, very minimally though
            if abs(self.y_speed) > bounce_stop:
                self.y_speed = -self.y_speed * self.retention
            else:
                #if it is below the threshold, the ball will stop moving.
                self.y_speed = 0
        return self.y_speed
    
    #Updates the position of the ball, especially when under the effects of gravity, collisions, and friction.
    def update_pos(self):
        self.y_pos += self.y_speed
        self.x_pos += self.x_speed
        self.x_speed *= friction

    #Checks if in contact with any walls
    def check_walls(self):
        #Check collision with the left wall
        if self.x_pos - self.radius <= box_left:
            self.x_speed = abs(self.x_speed) * self.retention
            self.x_pos = box_left + self.radius + 6
        #Check collision with the right wall
        elif self.x_pos + self.radius >= box_right:
            self.x_speed = -abs(self.x_speed) * self.retention
            self.x_pos = box_right - self.radius - 6
        
        #Check collision with the bottom wall
        if self.y_pos + self.radius >= bottom:
            self.y_pos = bottom - self.radius
            if abs(self.y_speed) > bounce_stop:
                self.y_speed = -abs(self.y_speed) * self.retention
            else:
                self.y_speed = 0
                self.x_speed *= friction

    #Strenuous code that handles collisions
    def handle_collision(self, other):
        dx = other.x_pos - self.x_pos #Calculates x distance between first and second balls interested with collisions
        dy = other.y_pos - self.y_pos #Calculates y distance between first and second balls interested with collisions
        distance = math.hypot(dx, dy) #Calculates the magnitude of the distance between the two

        #If it is found that the distance between the two is within each other, and they are the same color, a merge will occur
        if distance < self.radius + other.radius:
            if self.color == other.color and self.color in COLOR_TRANSITIONS:
                new_ball = self.merge_with(other)
                score_increase = COLOR_SCORES.get(self.color, 0)
                player.increase_score(score_increase)
                return new_ball
            else:
                #Calculate angle of collision
                angle = math.atan2(dy, dx)

                #Calculate velocities in the direction of the collision angle
                self_speed = math.sqrt(self.x_speed ** 2 + self.y_speed ** 2)
                other_speed = math.sqrt(other.x_speed ** 2 + other.y_speed ** 2)

                self_angle = math.atan2(self.y_speed, self.x_speed)
                other_angle = math.atan2(other.y_speed, other.x_speed)

                self_new_x_speed = self_speed * math.cos(self_angle - angle)
                self_new_y_speed = self_speed * math.sin(self_angle - angle)
                other_new_x_speed = other_speed * math.cos(other_angle - angle)
                other_new_y_speed = other_speed * math.sin(other_angle - angle)

                #Exchange velocities in the direction of the collision
                self_new_x_speed, other_new_x_speed = other_new_x_speed, self_new_x_speed

                #Convert back to original angle
                self_final_x_speed = math.cos(angle) * self_new_x_speed + math.cos(angle + math.pi / 2) * self_new_y_speed
                self_final_y_speed = math.sin(angle) * self_new_x_speed + math.sin(angle + math.pi / 2) * self_new_y_speed
                other_final_x_speed = math.cos(angle) * other_new_x_speed + math.cos(angle + math.pi / 2) * self_new_y_speed
                other_final_y_speed = math.sin(angle) * other_new_x_speed + math.sin(angle + math.pi / 2) * self_new_y_speed

                # Update velocities
                self.x_speed = self_final_x_speed * self.retention
                self.y_speed = self_final_y_speed * self.retention
                other.x_speed = other_final_x_speed * other.retention
                other.y_speed = other_final_y_speed * other.retention

                # Adjust positions to prevent sticking
                overlap = 0.5 * (self.radius + other.radius - distance + 1)
                self.x_pos -= overlap * math.cos(angle)
                self.y_pos -= overlap * math.sin(angle)
                other.x_pos += overlap * math.cos(angle)
                other.y_pos += overlap * math.sin(angle)

    #Merges two balls together, combining their positions, radius, and color
    def merge_with(self, other):
        new_x_pos = (self.x_pos + other.x_pos) / 2
        new_y_pos = (self.y_pos + other.y_pos) / 2
        new_color = COLOR_TRANSITIONS[self.color]
        new_radius = COLOR_RADIUS[new_color]
        new_retention = (self.retention + other.retention) / 2
        new_y_speed = (self.y_speed + other.y_speed) / 2
        new_x_speed = (self.x_speed + other.x_speed) / 2

        new_ball = Ball(new_x_pos, new_y_pos, new_radius, new_color, new_retention, new_y_speed, new_x_speed)

        return new_ball

#Creates a random ball, that is also a preview ball held underneath the player to show what will be shot next
def create_random_ball():
    x_pos = player.rect.centerx
    y_pos = player.rect.centery
    color = random.choice(BALL_COLOR)
    radius = COLOR_RADIUS[color]
    retention = 0.3
    y_speed = 0
    x_speed = 0
    return Ball(x_pos, y_pos, radius, color, retention, y_speed, x_speed)

preview_ball = create_random_ball()

#Drawing Functions
def draw_walls():
    left = pygame.draw.line(screen, 'white', (0, 0), (0, HEIGHT), WALL_THICKNESS)
    right = pygame.draw.line(screen, 'white', (WIDTH, 0), (WIDTH, HEIGHT), WALL_THICKNESS)
    top = pygame.draw.line(screen, 'white', (0, 0), (WIDTH, 0), WALL_THICKNESS)
    bottom = pygame.draw.line(screen, 'white', (0, HEIGHT), (WIDTH, HEIGHT), WALL_THICKNESS)
    return [left, right, top, bottom]

#Function used to simulate a dotted line
def draw_dotted_vertical_line(surface, color, x_pos, start_y, end_y, dot_length, gap_length):
    current_y = start_y
    while current_y < end_y:
        dot_end_y = min(current_y + dot_length, end_y)
        pygame.draw.line(surface, color, (x_pos, current_y), (x_pos, dot_end_y), 5)
        current_y = dot_end_y + gap_length

#Used to show a preview of ball to spewed, sets the to be previwed to be equal to the current ball in hand
def update_preview_ball_position():
    preview_ball.x_pos = player.rect.centerx
    preview_ball.y_pos = player.rect.centery + 50

#Draws the previewed ball, so it can actually be shown
def draw_preview_ball():
    preview_x_pos = player.rect.x + player.rect.width - 50
    preview_y_pos = player.rect.y + (player.rect.height // 2) + 50
    pygame.draw.circle(screen, preview_ball.color, (preview_x_pos, preview_y_pos), preview_ball.radius)

#Draws the box where the balls will be dropped in to
def draw_box():
    left = pygame.draw.line(screen, (139, 69, 19), (box_left, WALL_THICKNESS + 100), (box_left, HEIGHT - WALL_THICKNESS - 10), WALL_THICKNESS)
    right = pygame.draw.line(screen, (139, 69, 19), (box_right, WALL_THICKNESS + 100), (box_right, HEIGHT - WALL_THICKNESS - 10), WALL_THICKNESS)
    bottom = pygame.draw.line(screen, (139, 69, 19), (box_left, HEIGHT - WALL_THICKNESS - 15), (box_right, HEIGHT - WALL_THICKNESS - 15), WALL_THICKNESS)
    return [left, right, bottom]

#Draws the score on the top left of the screen
def draw_score(screen, player):
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {player.score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))  #Position the score at the top-left of the screen

#Game Loop
running = True
while running:
    screen.fill((242, 196, 171))
    draw_walls()
    draw_box()
    draw_dotted_vertical_line(screen, (0,0,0), player.rect.x + 49, player.rect.y + 100, bottom-10, 5, 20)

    #Get current time
    current_time = pygame.time.get_ticks()
    can_shoot = (current_time - last_shot_time >= cooldown_time)

    #Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and can_shoot:
                new_ball = preview_ball
                balls.append(new_ball)
                preview_ball = create_random_ball()
                last_shot_time = current_time  # Update last shot time

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move(-3)
    if keys[pygame.K_RIGHT]:
        player.move(3)

    #Call functions
    update_preview_ball_position()
    player.draw(screen)
    draw_preview_ball()

    #Two seperate arrays, in which the balls that are currently surviving go in the latter array, and the balls that have been removed due to merge have been put in the first
    balls_to_remove = []
    balls_to_add = []

    #Constantly checking and applying to all balls in the game
    for i, ball in enumerate(balls):
        ball.create() #Creating
        ball.update_pos() #Updating position
        ball.check_gravity() #Applying gravity
        ball.check_walls() #Cheks to see if in contact with walls

        #Check if the ball is above the threshold to end the game
        if ball.y_pos + ball.radius < WALL_THRESHOLD:
            print("Game Over!")
            running = False  #End the game

        #If a collision has occured, appending will occur
        for j in range(i + 1, len(balls)):
            result = ball.handle_collision(balls[j])
            if result:
                balls_to_remove.append(ball)
                balls_to_remove.append(balls[j])
                balls_to_add.append(result)

    #Moreover, adds balls to remove array
    for ball in balls_to_remove:
        if ball in balls:
            balls.remove(ball)
    balls.extend(balls_to_add)

    draw_score(screen, player)  #Draw the score

    pygame.display.flip()
    timer.tick(60)  #Control frame rate

pygame.quit()
