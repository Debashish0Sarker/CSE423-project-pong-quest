from OpenGL.GL import*
from OpenGL.GLUT import*
from OpenGL.GLU import*
import random 
import math

width = 800
height = 600

ball_pos = [0.0, -0.5]
ball_velocity = [0.0, 0.0]  
ball_radius = 0.05


def draw_points(x,y) :
    glPointSize(2)
    glBegin(GL_POINTS)
    glVertex2f(x,y)
    glEnd()

def find_zone(x0, y0, x1, y1):

    dx = x1 - x0
    dy = y1 - y0

    zone = -1

    if abs(dx) > abs(dy):  
        if dx > 0 and dy > 0:
            zone = 0
        elif dx < 0 and dy > 0:
            zone = 3
        elif dx < 0 and dy < 0:
            zone = 4
        else:
            zone = 7

    else:                  
        if dx > 0 and dy > 0:
            zone = 1
        elif dx < 0 and dy > 0:
            zone = 2
        elif dx < 0 and dy < 0:
            zone = 5
        else:
            zone = 6
   
    return zone


def convert(original_zone,x,y) :

    if (original_zone == 0) :
        return x,y
    elif (original_zone == 1) :
        return y,x
    elif (original_zone == 2) :
        return -y,x
    elif (original_zone == 3) :
        return -x,y
    elif (original_zone == 4) :
        return -x,-y
    elif (original_zone == 5) :
        return -y,-x
    elif (original_zone == 6) :
        return -y,x
    elif (original_zone == 7) :
        return x,-y

def convert_original(original_zone,x,y) :

    if (original_zone == 0) :
        return x,y
    elif (original_zone == 1) :
        return y,x
    elif (original_zone == 2) :
        return -y,-x
    elif (original_zone == 3) :
        return -x,y
    elif (original_zone == 4) :
        return -x,-y
    elif (original_zone == 5) :
        return -y,-x
    elif (original_zone == 6) :
        return y,-x
    elif (original_zone == 7) :
        return x,-y
   

def midpoint_line(zone,x0,y0, x1,y1) :

    dx = x1-x0
    dy = y1-y0

    d = (2*dy) - dx

    forE = 2*dy

    forNE = 2*(dy-dx)


    x = x0
    y = y0

    while (x < x1) :

        org_x, org_y = convert_original(zone,x,y)
        draw_points(org_x,org_y)

        if (d<=0) :
            x += 1
            d += forE
        else :
            x += 1
            y += 1
            d += forNE

def eight_way_symmetry(x0,y0,x1,y1) :


    zone = find_zone(x0,y0,x1,y1)
    conv_x0, conv_y0 = convert(zone,x0,y0)
    conv_x1, conv_y1 = convert(zone,x1,y1)
    midpoint_line(zone,conv_x0,conv_y0,conv_x1,conv_y1)


def midpoint_circle(x0,y0,r):
    def Eightway_symmetry(x, y, x0, y0):
        glVertex2f(x0+x,y0+y)
        glVertex2f(x0+y,y0+x)
        glVertex2f(x0+y,y0-x)
        glVertex2f(x0+x,y0-y)
        glVertex2f(x0-x,y0-y)
        glVertex2f(x0-y,y0-x)
        glVertex2f(x0-y,y0+x)
        glVertex2f(x0-x,y0+y)
    
    x = 0
    y = r
    d = 1-r

    glBegin(GL_POINTS)
    Eightway_symmetry(x,y,x0,y0)

    while x<y:
        if d<0:
            d += 2*x+3
        else:
            d += 2*x-2*y+5
            y -= 1
        x +=1
        Eightway_symmetry(x,y,x0,y0)
    glEnd()

def draw_ball(xc, yc, r):
    midpoint_circle(xc, yc, r)