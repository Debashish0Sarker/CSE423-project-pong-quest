#full_game_150_iteration(using_gl_shape)
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import random

ball_x, ball_y = 0.0, -0.1 
ball_dy = 0.0
ball_radius = 0.05
gravity = -0.001
jump_strength = 0.045
background_offset = 0.0
background_speed = 0.02
reset_game = False
lives = 3
x_s=200
score = 0
last_distance_update = 0.0 

window_width = 800
window_height = 600

surfaces = []
walls = []
buttons = {
    "reset": {"x1": 50, "y1": 550, "x2": 30, "y2": 30}, 
    "exit": {"x1": 750, "y1": 550, "x2": 30, "y2": 30}, 
}

# Surface types
SURFACE_STANDARD = 0
SURFACE_BOUNCY = 1
SURFACE_SPIKY = 2
special_objects = []
SPECIAL_SPEED = 0
SPECIAL_LOW_GRAVITY = 1
SPECIAL_LARGE_BALL = 2

special_effect_active = False
special_effect_type = None
special_effect_end_time = 0
original_gravity = gravity
original_ball_radius = ball_radius
original_background_speed = background_speed

def add_surface(x1, y1, x2, y2, surface_type):
    x1 = 2 * (x1 / window_width) - 1
    x2 = 2 * (x2 / window_width) - 1
    y1 = 2 * (y1 / window_height) - 1
    y2 = 2 * (y2 / window_height) - 1
    surfaces.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "type": surface_type})

def add_wall(x, height):
    x = 2 * (x / window_width) - 1 
    walls.append({"x": x, "height": height})

def draw_circle(cx, cy, radius):
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)  
    for angle in range(0, 361, 10):
        theta = math.radians(angle)
        x = cx + radius * math.cos(theta)
        y = cy + radius * math.sin(theta)
        glVertex2f(x, y)
    glEnd()

def draw_line(x1, y1, x2, y2):
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()

def draw_wall(x, height):
    glBegin(GL_QUADS)
    glVertex2f(x - 0.02, -1)
    glVertex2f(x + 0.02, -1)
    glVertex2f(x + 0.02, -1 + height)
    glVertex2f(x - 0.02, -1 + height)
    glEnd()

def update_score():
    global score, last_distance_update
    if background_offset < last_distance_update - 0.1: 
        score += 1
        last_distance_update = background_offset

def reset():
    global ball_x, ball_y, ball_dy, background_offset, reset_game, score, last_distance_update
    ball_x, ball_y = 0.0, -0.1
    ball_dy = 0.0
    background_offset = 0.0
    reset_game = False
    last_distance_update = 0.0

def update_scene():
    global ball_y, ball_dy, ball_x, lives
    ball_dy += gravity
    ball_y += ball_dy
    if ball_y - ball_radius <= -1:
        ball_y = -1 + ball_radius
        ball_dy = 0

    for surface in surfaces:
        x1, y1, x2, y2, surface_type = surface.values()
        x1 += background_offset
        x2 += background_offset

        if x1 <= ball_x <= x2 and abs(ball_y - y1) <= ball_radius:
            if surface_type == SURFACE_STANDARD:
                ball_dy = 0
                ball_y = y1 + ball_radius
            elif surface_type == SURFACE_BOUNCY:
                ball_dy = jump_strength * 1.5
                ball_y = y1 + ball_radius
            elif surface_type == SURFACE_SPIKY:
                lives -= 1 
                reset()
            break

    for wall in walls:
        wall_x = wall["x"] + background_offset
        wall_height = wall["height"]

        if abs(ball_x - wall_x) <= ball_radius:
            if ball_y - ball_radius <= -1 + wall_height: 

                if ball_x < wall_x:
                    ball_x = wall_x - ball_radius 
                else:
                    ball_x = wall_x + ball_radius 
                ball_dy = 0 
                break
    check_special_object_collision()
    reset_special_effect()
    update_score()
    check_trap_collision()
    update_trap()

def add_special_object(x, y, effect_type):
    x = 2 * (x / window_width) - 1
    y = 2 * (y / window_height) - 1 
    special_objects.append({"x": x, "y": y, "effect_type": effect_type})

def draw_special_object(x, y):
    x += background_offset 
    glBegin(GL_QUADS)
    glVertex2f(x - 0.03, y - 0.03)
    glVertex2f(x + 0.03, y - 0.03)
    glVertex2f(x + 0.03, y + 0.03)
    glVertex2f(x - 0.03, y + 0.03)
    glEnd()

def check_special_object_collision():
    global special_effect_active, special_effect_type, special_effect_end_time
    global gravity, ball_radius, background_speed

    for obj in special_objects:
        obj_x = obj["x"] + background_offset
        obj_y = obj["y"]

        if abs(ball_x - obj_x) <= ball_radius and abs(ball_y - obj_y) <= ball_radius:
            special_effect_active = True
            special_effect_type = obj["effect_type"]
            special_effect_end_time = time.time() + 5 

            if special_effect_type == SPECIAL_SPEED:
                background_speed *= 2
            elif special_effect_type == SPECIAL_LOW_GRAVITY:
                gravity /= 2
            elif special_effect_type == SPECIAL_LARGE_BALL:
                ball_radius *= 2
            special_objects.remove(obj)
            break

# Reset Special Effect
def reset_special_effect():
    global special_effect_active, gravity, ball_radius, background_speed

    if special_effect_active and time.time() >= special_effect_end_time:
        special_effect_active = False
        gravity = original_gravity
        ball_radius = original_ball_radius
        background_speed = original_background_speed

def is_ball_on_surface():
    global ball_y
    if ball_y - ball_radius <= -1: 
        return True
    for surface in surfaces: 
        x1, y1, x2, y2 = surface["x1"] + background_offset, surface["y1"], surface["x2"] + background_offset, surface["y2"]
        if x1 <= ball_x <= x2 and abs(ball_y - y1) <= ball_radius:
            return True
    return False

trap_x = 0.5  
trap_y = -0.5 
trap_width = 0.1
trap_height = 0.02
trap_speed = 0.01
trap_direction = 1  
trap_movement = "vertical" 

# Draw Trap
# Draw Trap
def draw_trap(x, y, width, height):
    x += background_offset 
    glBegin(GL_QUADS)
    glVertex2f(x - width / 2, y - height / 2)
    glVertex2f(x + width / 2, y - height / 2)
    glVertex2f(x + width / 2, y + height / 2)
    glVertex2f(x - width / 2, y + height / 2)
    glEnd()

def update_trap():
    global trap_x, trap_y, trap_direction

    if trap_movement == "horizontal":
        trap_x += trap_direction * trap_speed
        if trap_x + trap_width / 2 >= 1 or trap_x - trap_width / 2 <= -1:
            trap_direction *= -1  
    elif trap_movement == "vertical":
        trap_y += trap_direction * trap_speed
        if trap_y + trap_height / 2 >= 1 or trap_y - trap_height / 2 <= -1:
            trap_direction *= -1  

def check_trap_collision():
    global lives, reset_game
    adjusted_trap_x = trap_x + background_offset
    trap_top = trap_y + trap_height / 2
    trap_bottom = trap_y - trap_height / 2
    trap_left = adjusted_trap_x - trap_width / 2
    trap_right = adjusted_trap_x + trap_width / 2
    if (trap_left <= ball_x <= trap_right and
        trap_bottom <= ball_y <= trap_top):
        lives -= 1
        reset()

def draw_circle_in_points(cx, cy, radius):
    glBegin(GL_POINTS)
    for angle in range(0, 361, 1):
        theta = math.radians(angle)
        x = (cx + radius * math.cos(theta)) / window_width * 2 - 1
        y = (cy + radius * math.sin(theta)) / window_height * 2 - 1
        glVertex2f(x, y)
    glEnd()

def draw_x_in_points(x, y, size):
    glBegin(GL_POINTS)
    for i in range(size):
        x1 = (x - size // 2 + i) / window_width * 2 - 1
        y1 = (y - size // 2 + i) / window_height * 2 - 1
        x2 = (x + size // 2 - i) / window_width * 2 - 1
        y2 = (y - size // 2 + i) / window_height * 2 - 1
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
    glEnd()
def draw_screen_controls():
    glColor3f(0.0, 1.0, 1.0)  
    x1, y1 = 50, 550  
    radius = 20  
    draw_circle_in_points(x1, y1, radius)
    glColor3f(1.0, 0.0, 0.0)  # Red
    x3, y3 = 750, 550  # center x
    size = 20
    draw_x_in_points(x3, y3, size)

def display():
    global score

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    #ball
    glColor3f(1, 0, 0)
    draw_circle(ball_x, ball_y, ball_radius)
    draw_screen_controls()

    for surface in surfaces:
        x1, y1, x2, y2, surface_type = surface.values()
        x1 += background_offset
        x2 += background_offset

        if surface_type == SURFACE_STANDARD:
            glColor3f(0, 1, 0) #Green
        elif surface_type == SURFACE_BOUNCY:
            glColor3f(0, 0, 1) #Blue
        elif surface_type == SURFACE_SPIKY:
            glColor3f(1, 0, 0) #Red

        draw_line(x1, y1, x2, y2)

    for wall in walls:
        wall_x = wall["x"] + background_offset
        glColor3f(1, 1, 0) #Yellow
        draw_wall(wall_x, wall["height"])

    for obj in special_objects:
        if obj["effect_type"] == SPECIAL_SPEED:
            glColor3f(0, 1, 1)  #Cyan for speed boost
        elif obj["effect_type"] == SPECIAL_LOW_GRAVITY:
            glColor3f(1, 0, 1)  #Magenta for low gravity
        elif obj["effect_type"] == SPECIAL_LARGE_BALL:
            glColor3f(1, 1, 0)  #Yellow for larger ball
        draw_special_object(obj["x"], obj["y"])

    glColor3f(1, 1, 1)
    glRasterPos2f(-0.9, 0.9)  # Position top-left corner
    for char in f"Score: {score}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # Display lives
    glColor3f(1, 1, 1)
    glRasterPos2f(0.6, 0.9)  # Position top-right corner
    for char in f"Lives: {lives}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    # Game Over Screen
    if lives <= 0:
        glColor3f(1, 0, 0)
        glRasterPos2f(-0.3, 0)  # Center 
        for char in "GAME OVER":
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))

    glColor3f(1, 0.5, 0)  # Orange for trap
    draw_trap(trap_x, trap_y, trap_width, trap_height)

    glutSwapBuffers()

def mouse_callback(button, state, x, y):
    global reset_game
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:

        rx,ry,rw,rh = 50, 550,30,30
        if rx <= x <= rx +rw and window_height - (ry+rh) <= y <= window_height - ry:
            print("Starting Over")
            reset()

        ex,ey,ew,eh = 750, 550, 30,30
        if ex <= x <= ex+ew and window_height - (ey +eh) <= y <= window_height - ey:
            print('Goodbye! Final Score:', score)
            glutLeaveMainLoop()

def keyboard_down(key, x, y):
    global ball_dy, background_offset

    if key == b'w':  # Jump
        if is_ball_on_surface():
            ball_dy = jump_strength
    elif key == b'a':  # Move right
        background_offset += background_speed
    elif key == b'd':  # Move left
        background_offset -= background_speed

def timer(value):
    if lives > 0: 
        update_scene()
        glutPostRedisplay()
        glutTimerFunc(16, timer, 0) 

# Initialization
def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    gluOrtho2D(-1, 1, -1, 1)


ball_x, ball_y = 0.0, -0.5

# Add surfaces
for i in range (150):
    y_l=[200,250,300,350,400,450,500]
    x_l=[.1,.2,.3,.4,.5]
    h=random.choice(x_l)
    y=random.choice(y_l)
    if i%5==0:
        add_surface(x_s, y, x_s+200, y, SURFACE_BOUNCY)
    elif i%7==0:
        add_surface(x_s, y, x_s+200, y, SURFACE_SPIKY)
    else:
        add_surface(x_s, y, x_s+200, y, SURFACE_STANDARD)
    if i%11==0:
        add_special_object(x_s+100, y+5, SPECIAL_SPEED)
    elif i%13==0:
        add_special_object(x_s+100, y+5, SPECIAL_LOW_GRAVITY)
    elif i%9==0:
        add_special_object(x_s+100, y+5, SPECIAL_LARGE_BALL)
    add_wall(x_s+y, h)

    x_s+=200
# add_surface(200, 200, 400, 200, SURFACE_STANDARD)
# add_surface(200+1000, 500, 400+1000, 500, SURFACE_STANDARD)
# add_surface(500, 200, 700, 200, SURFACE_BOUNCY)
# add_surface(700, 300, 800, 300, SURFACE_SPIKY)

# Add walls
add_wall(600, 0.4)
add_wall(800, .1)

# Add special objects
add_special_object(400, 100, SPECIAL_SPEED)
add_special_object(700, 200, SPECIAL_LOW_GRAVITY)
add_special_object(800, 300, SPECIAL_LARGE_BALL)

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(window_width, window_height)
glutCreateWindow(b"Bounce Ball Game")
init()
glutDisplayFunc(display)
glutKeyboardFunc(keyboard_down)
glutMouseFunc(mouse_callback)
glutTimerFunc(16, timer, 0)
glutMainLoop()
