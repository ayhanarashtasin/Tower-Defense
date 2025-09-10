from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18
import sys
import random
import math
      
camera_pos = (0, 800, 1000) 

fovY = 120
GRID_LENGTH = 800 
TOWER_SCALE = 1.6 
TOWER_HEALTH_MAX = 100 
WALL_HEIGHT = 90 
TOWER_BASE_FIRE_INTERVAL = 1.2
TOWER_DAMAGE_MULT_PER_LEVEL = 0.25
TOWER_COOLDOWN_REDUCTION_PER_LEVEL = 0.10 
TOWER_UPGRADE_BASE_COST = 50


towers = []


ENEMY_SCALE = 1.2
enemies = []
ENEMY_SPEED = 120.0 
ENEMY_DAMAGE = 10


current_wave = 0
last_update_time_ms = 0
game_over = False
is_paused = False


cheat_mode = False
AUTO_FIRE_INTERVAL = 0.6
cheat_fire_accum = 0.0


awaiting_next_wave = False


wave_reached_on_game_over = 0


ARROW_SPEED = 320.0
ARROW_TTL = 4.0 
ARROW_HEIGHT = 45.0 
ARROW_DAMAGE = 10
ARROW_HIT_RADIUS = 36.0
ARROW_HIT_RADIUS_3D = 40.0 
arrows = []

points = 0
WAVE_COST_BASE = 50
POINTS_PER_KILL = 5
MISSED_BULLET_DAMAGE = 0.5
missed_bullets = 0
BIG_WAVE_DAMAGE_PERCENT = 0.25
BIG_WAVE_DAMAGE_MIN = 30.0

TROOP_SPAWN_COST = 30
TROOP_BASE_COUNT = 5
TROOP_COUNT_INCREMENT = 2
TROOP_SPEED = 110.0
TROOP_HEALTH = 25.0
TROOP_DPS = 20.0
TROOP_ATTACK_RADIUS = 30.0
player_troops = []
troop_spawn_presses = 0
troop_id_counter = 0

wave_active = False
wave_front_z = 0.0
wave_width = 220.0
wave_speed = 1400.0
wave_targets = set()
wave_cost_current = WAVE_COST_BASE

HIT_EFFECT_DURATION = 0.45
hit_effects = []

enemy_id_counter = 0

archer_quadric = None

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_background():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    bands = 14
    for i in range(bands):
        t0 = i / float(bands)
        t1 = (i + 1) / float(bands)
        y0 = int(800 * t0)
        y1 = int(800 * t1)
        r = 0.08 + 0.70 * t0
        g = 0.20 + 0.35 * (1.0 - abs(0.5 - t0) * 2.0)
        b = 0.35 + 0.55 * (1.0 - t0 * 0.7)
        glColor3f(r, g, b)
        glBegin(GL_QUADS)
        glVertex3f(0, y0, 1)
        glVertex3f(1000, y0, 1)
        glVertex3f(1000, y1, 1)
        glVertex3f(0, y1, 1)
        glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    

def draw_archer_tower(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(TOWER_SCALE, TOWER_SCALE, TOWER_SCALE)

    glColor3f(0.18, 0.20, 0.28)
    glPushMatrix()
    glTranslatef(0, 60, 0)
    glScalef(1, 3, 1)
    glutSolidCube(40)
    glPopMatrix()

    accent_color = (0.10, 0.80, 0.95)
    for dx in (-18, 18):
        for dz in (-18, 18):
            glColor3f(*accent_color)
            glPushMatrix()
            glTranslatef(dx, 60, dz)
            glScalef(0.20, 3.4, 0.20)
            glutSolidCube(40)
            glPopMatrix()

    glColor3f(0.92, 0.98, 1.0)
    glPushMatrix()
    glTranslatef(0, 130, 0)
    glScalef(1.5, 0.5, 1.5)
    glutSolidCube(40)
    glPopMatrix()

    glColor3f(*accent_color)
    glPushMatrix()
    glTranslatef(-30, 130, 0)
    glScalef(0.07, 0.6, 1.55)
    glutSolidCube(40)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(30, 130, 0)
    glScalef(0.07, 0.6, 1.55)
    glutSolidCube(40)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 130, -30)
    glScalef(1.55, 0.6, 0.07)
    glutSolidCube(40)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 130, 30)
    glScalef(1.55, 0.6, 0.07)
    glutSolidCube(40)
    glPopMatrix()
    
    draw_person_with_gun()

    glPopMatrix()

def draw_enemy_unit(x, y, z, color=(0.85, 0.15, 0.25), enemy_type="grunt", scale_mult=1.0):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(ENEMY_SCALE * scale_mult, ENEMY_SCALE * scale_mult, ENEMY_SCALE * scale_mult)

    glColor3f(0.08, 0.08, 0.1)
    glPushMatrix()
    glTranslatef(0, 22, 0)
    if archer_quadric is not None:
        gluSphere(archer_quadric, 22, 20, 16)
    glPopMatrix()

    glColor3f(0.15, 0.15, 0.18)
    if archer_quadric is not None:
        glPushMatrix()
        glTranslatef(-12, 6, 8)
        glScalef(1.6, 0.6, 1.2)
        gluSphere(archer_quadric, 7, 14, 10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(12, 6, 8)
        glScalef(1.6, 0.6, 1.2)
        gluSphere(archer_quadric, 7, 14, 10)
        glPopMatrix()

    glColor3f(1.0, 0.95, 0.6)
    if archer_quadric is not None:
        glPushMatrix()
        glTranslatef(-8, 18, 18)
        glRotatef(12, 0, 1, 0)
        glScalef(1.2, 0.7, 0.35)
        gluSphere(archer_quadric, 5, 12, 10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(8, 18, 18)
        glRotatef(-12, 0, 1, 0)
        glScalef(1.2, 0.7, 0.35)
        gluSphere(archer_quadric, 5, 12, 10)
        glPopMatrix()

    glColor3f(1.0, 1.0, 1.0)
    if archer_quadric is not None:
        glPushMatrix()
        glTranslatef(8, 28, 15)
        glScalef(1.2, 0.6, 0.4)
        gluSphere(archer_quadric, 3.5, 10, 8)
        glPopMatrix()

    glColor3f(0.8, 0.7, 0.3)
    if archer_quadric is not None:
        glPushMatrix()
        glTranslatef(0, 40, -4)
        glRotatef(-30, 1, 0, 0)
        glRotatef(15, 0, 1, 0)
        gluCylinder(archer_quadric, 1.0, 1.0, 10, 10, 1)
        glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 40, -4)
    glRotatef(-30, 1, 0, 0)
    glRotatef(15, 0, 1, 0)
    glTranslatef(0, 0, 10)
    glColor3f(0.8, 0.2, 0.2)
    glBegin(GL_LINES)
    spikes = 8
    radius = 6.0
    for i in range(spikes):
        ang = 2.0 * math.pi * i / spikes
        glVertex3f(0, 0, 0)
        glVertex3f(radius * math.cos(ang), radius * math.sin(ang), 0)
    glEnd()
    glPopMatrix()

    glPopMatrix()


def draw_person_with_gun():
    glPushMatrix()
    glTranslatef(0, 145, 0)

    glColor3f(0.2, 0.5, 1.0)
    glPushMatrix()
    glTranslatef(0, 22, 0)
    glScalef(1.0, 1.6, 0.7)
    glutSolidCube(22)
    glPopMatrix()

    glColor3f(1.0, 0.85, 0.6)
    glPushMatrix()
    glTranslatef(0, 42, 0)
    if archer_quadric is not None:
        gluSphere(archer_quadric, 7, 12, 12)
    glPopMatrix()

    glColor3f(0.2, 0.2, 0.25)
    glPushMatrix()
    glTranslatef(-5.5, 8, 0)
    glScalef(0.5, 1.2, 0.5)
    glutSolidCube(14)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(5.5, 8, 0)
    glScalef(0.5, 1.2, 0.5)
    glutSolidCube(14)
    glPopMatrix()

    glColor3f(0.9, 0.8, 0.7)
    glPushMatrix()
    glTranslatef(-13, 26, 0)
    glScalef(0.4, 1.0, 0.4)
    glutSolidCube(12)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(13, 26, 0)
    glScalef(0.4, 1.0, 0.4)
    glutSolidCube(12)
    glPopMatrix()

    glColor3f(0.1, 0.1, 0.1)
    glPushMatrix()
    glTranslatef(0, 28, -6)
    glScalef(1.8, 0.4, 0.5)
    glutSolidCube(10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 28, -11)
    glRotatef(180, 0, 1, 0)
    if archer_quadric is not None:
        gluCylinder(archer_quadric, 1.2, 1.2, 16, 10, 1)
    glPopMatrix()

    glPopMatrix()

def draw_health_bar(x, y, z, health_ratio):
    bar_width = 80
    bar_height = 8
    glPushMatrix()
    glTranslatef(x, y, z)

    glColor3f(0.5, 0.0, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(-bar_width/2, 0, 0)
    glVertex3f(bar_width/2, 0, 0)
    glVertex3f(bar_width/2, bar_height, 0)
    glVertex3f(-bar_width/2, bar_height, 0)
    glEnd()

    glColor3f(0.1, 0.8, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-bar_width/2, 0, 0)
    glVertex3f(-bar_width/2 + bar_width * health_ratio, 0, 0)
    glVertex3f(-bar_width/2 + bar_width * health_ratio, bar_height, 0)
    glVertex3f(-bar_width/2, bar_height, 0)
    glEnd()

    glPopMatrix()

def draw_structures():
    health_bar_y = int(190 * TOWER_SCALE)
    for t in towers:
        draw_archer_tower(t["x"], t["y"], t["z"])
        ratio = max(0.0, min(1.0, t["health"] / float(TOWER_HEALTH_MAX)))
        draw_health_bar(t["x"], health_bar_y, t["z"], ratio)

def draw_enemies():
    for e in enemies:
        col = e.get("color", (0.85, 0.15, 0.25))
        scale_mult = e.get("scale_mult", 1.0)
        draw_enemy_unit(e["x"], e["y"], e["z"], color=col, enemy_type=e.get("type", "grunt"), scale_mult=scale_mult)

def draw_troop(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(1.6, 1.6, 1.6)

    if archer_quadric is not None:
        glColor3f(0.08, 0.12, 0.20)
        glPushMatrix()
        glTranslatef(0, 14, 0)
        gluSphere(archer_quadric, 12, 18, 14)
        glPopMatrix()

        glColor3f(0.75, 0.85, 0.90)
        glPushMatrix()
        glTranslatef(-2, 16, -3)
        gluSphere(archer_quadric, 9, 14, 12)
        glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 10, 0)
    glRotatef(90, 1, 0, 0)
    glColor3f(0.20, 0.95, 0.60)
    if archer_quadric is not None:
        gluCylinder(archer_quadric, 18.0, 18.0, 3.0, 24, 1)
    glTranslatef(0, 0, 0.1)
    glColor3f(0.05, 0.10, 0.12)
    if archer_quadric is not None:
        gluCylinder(archer_quadric, 12.0, 12.0, 2.8, 24, 1)
    glPopMatrix()

    spikes = 10
    radius = 15.0
    for i in range(spikes):
        ang = 2.0 * math.pi * i / spikes
        sx = radius * math.cos(ang)
        sz = radius * math.sin(ang)
        glPushMatrix()
        glTranslatef(sx, 6.0, sz)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.25, 0.85, 1.0)
        if archer_quadric is not None:
            gluCylinder(archer_quadric, 3.5, 0.0, 10.0, 10, 1)
        glPopMatrix()

    if archer_quadric is not None:
        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(-5.0, 16.0, 10.0)
        glScalef(1.6, 0.9, 0.6)
        gluSphere(archer_quadric, 2.6, 10, 8)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(5.0, 16.0, 10.0)
        glScalef(1.6, 0.9, 0.6)
        gluSphere(archer_quadric, 2.6, 10, 8)
        glPopMatrix()

    glPopMatrix()

def draw_arrow(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.9, 0.9, 0.9)
    if archer_quadric is not None:
        gluSphere(archer_quadric, 10, 14, 10)
    glPopMatrix()

def draw_hit_effect(x, y, z, life_ratio):
    glPushMatrix()
    glTranslatef(x, y, z)
    size = 10 + 80 * (1.0 - life_ratio)
    glColor3f(1.0, 1.0, 0.2)
    glBegin(GL_LINE_LOOP)
    segments = 20
    for i in range(segments):
        ang = 2.0 * 3.1415926 * i / segments
        glVertex3f(size * math.cos(ang), 5, size * math.sin(ang))
    glEnd()
    glPopMatrix()


def draw_playground():
    bands = 8
    for i in range(bands):
        t0 = i / float(bands)
        t1 = (i + 1) / float(bands)
        z0 = (t0) * GRID_LENGTH
        z1 = (t1) * GRID_LENGTH
        c0 = (
            0.10 + 0.10 * t0,
            0.25 + 0.25 * t0,
            0.70 + 0.25 * t0,
        )
        glColor3f(*c0)
        glBegin(GL_QUADS)
        glVertex3f(-GRID_LENGTH, 0, z1)
        glVertex3f(GRID_LENGTH, 0, z1)
        glVertex3f(GRID_LENGTH, 0, z0)
        glVertex3f(-GRID_LENGTH, 0, z0)
        glEnd()

    for i in range(bands):
        t0 = i / float(bands)
        t1 = (i + 1) / float(bands)
        z0 = -(t0) * GRID_LENGTH
        z1 = -(t1) * GRID_LENGTH
        c0 = (
            0.90 + 0.10 * t0,
            0.20 + 0.40 * t0,
            0.55 - 0.25 * t0,
        )
        glColor3f(*c0)
        glBegin(GL_QUADS)
        glVertex3f(-GRID_LENGTH, 0, z0)
        glVertex3f(GRID_LENGTH, 0, z0)
        glVertex3f(GRID_LENGTH, 0, z1)
        glVertex3f(-GRID_LENGTH, 0, z1)
        glEnd()

    glBegin(GL_LINES)
    glColor3f(0.95, 0.98, 1.0)
    for dy in (0, 1, 2):
        glVertex3f(-GRID_LENGTH, 1 + dy, 0)
        glVertex3f(GRID_LENGTH, 1 + dy, 0)
    glEnd()

    if wave_active:
        glColor3f(0.85, 0.9, 1.0)
        z0 = wave_front_z
        z1 = wave_front_z - wave_width
        glBegin(GL_QUADS)
        glVertex3f(-GRID_LENGTH, 2, z0)
        glVertex3f(GRID_LENGTH, 2, z0)
        glVertex3f(GRID_LENGTH, 2, z1)
        glVertex3f(-GRID_LENGTH, 2, z1)
        glEnd()

    wall_thickness = 20
    h = WALL_HEIGHT
    base_r, base_g, base_b = 0.25, 0.28, 0.35
    stripe_r, stripe_g, stripe_b = 0.10, 0.75, 0.95
    glColor3f(base_r, base_g, base_b)
    glPushMatrix()
    glTranslatef(-GRID_LENGTH - wall_thickness/2, h/2, 0)
    glScalef(wall_thickness, h, GRID_LENGTH * 2 + wall_thickness)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(stripe_r, stripe_g, stripe_b)
    glPushMatrix()
    glTranslatef(-GRID_LENGTH - wall_thickness/2, h - 3, 0)
    glScalef(wall_thickness + 2, 6, GRID_LENGTH * 2 + wall_thickness + 2)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(base_r, base_g, base_b)
    glPushMatrix()
    glTranslatef(GRID_LENGTH + wall_thickness/2, h/2, 0)
    glScalef(wall_thickness, h, GRID_LENGTH * 2 + wall_thickness)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(stripe_r, stripe_g, stripe_b)
    glPushMatrix()
    glTranslatef(GRID_LENGTH + wall_thickness/2, h - 3, 0)
    glScalef(wall_thickness + 2, 6, GRID_LENGTH * 2 + wall_thickness + 2)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(base_r, base_g, base_b)
    glPushMatrix()
    glTranslatef(0, h/2, GRID_LENGTH + wall_thickness/2)
    glScalef(GRID_LENGTH * 2 + wall_thickness, h, wall_thickness)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(stripe_r, stripe_g, stripe_b)
    glPushMatrix()
    glTranslatef(0, h - 3, GRID_LENGTH + wall_thickness/2)
    glScalef(GRID_LENGTH * 2 + wall_thickness + 2, 6, wall_thickness + 2)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(base_r, base_g, base_b)
    glPushMatrix()
    glTranslatef(0, h/2, -GRID_LENGTH - wall_thickness/2)
    glScalef(GRID_LENGTH * 2 + wall_thickness, h, wall_thickness)
    glutSolidCube(1)
    glPopMatrix()
    glColor3f(stripe_r, stripe_g, stripe_b)
    glPushMatrix()
    glTranslatef(0, h - 3, -GRID_LENGTH - wall_thickness/2)
    glScalef(GRID_LENGTH * 2 + wall_thickness + 2, 6, wall_thickness + 2)
    glutSolidCube(1)
    glPopMatrix()

def fire_arrow_from_tower(index):
    if index < 0 or index >= len(towers):
        return
    tower = towers[index]
    if tower["health"] <= 0:
        return
    if tower.get("cooldown", 0.0) > 0.0:
        return
    gun_local_y = 145 + 28
    gun_local_z_tip = -11 - 16
    spawn_y = int(gun_local_y * TOWER_SCALE)
    spawn_z = tower["z"] + gun_local_z_tip * TOWER_SCALE
    
    target_id = None
    min_d2 = None
    for e in enemies:
        if not e.get("alive", True):
            continue
        dx = e["x"] - tower["x"]
        dz = e["z"] - spawn_z
        d2 = dx*dx + dz*dz
        if min_d2 is None or d2 < min_d2:
            min_d2 = d2
            target_id = e.get("id")

    vx = 0.0
    vz = -ARROW_SPEED
    arrows.append({
        "x": tower["x"],
        "y": float(spawn_y),
        "z": spawn_z,
        "vx": vx,
        "vy": 0.0,
        "vz": vz,
        "ttl": ARROW_TTL,
        "target_id": target_id
    })
    tower["cooldown"] = tower.get("fire_interval", TOWER_BASE_FIRE_INTERVAL)

def try_wave_attack():
    global enemies, points, wave_active, wave_front_z, wave_targets, wave_cost_current
    if wave_active:
        return
    if points < wave_cost_current:
        return
    points -= wave_cost_current
    wave_cost_current *= 2
    wave_active = True
    wave_front_z = GRID_LENGTH
    wave_targets = set(e.get("id") for e in enemies if e.get("alive", True))

def upgrade_tower(index):
    global points
    if index < 0 or index >= len(towers):
        return
    t = towers[index]
    if t["health"] <= 0:
        return
    cost = t.get("upgrade_cost", TOWER_UPGRADE_BASE_COST)
    if points < cost:
        return
    points -= cost
    t["level"] = t.get("level", 1) + 1
    base_interval = t.get("fire_interval", TOWER_BASE_FIRE_INTERVAL)
    t["fire_interval"] = max(0.25, base_interval * (1.0 - TOWER_COOLDOWN_REDUCTION_PER_LEVEL))
    t["upgrade_cost"] = cost * 2

def keyboardListener(key, x, y):
    global points, is_paused, awaiting_next_wave

    if isinstance(key, bytes):
        key = key.decode('utf-8')

    if key in ('R', 'r'):
        init_game_state()
        is_paused = False
        return

    if key == ' ':
        is_paused = not is_paused
        return

    if key in ('B', 'b'):
        is_paused = False
        return

    if key in ('C', 'c'):
        global cheat_mode
        cheat_mode = not cheat_mode
        return

    if game_over:
        if key in ('R', 'r'):
            init_game_state()
        elif key == '\x1b':
            sys.exit(0)
        return

    if key in ('\r',):
        if awaiting_next_wave:
            awaiting_next_wave = False
            start_next_wave()
            return

    if key in ('A', 'a'):
        fire_arrow_from_tower(0)
    elif key in ('S', 's'):
        fire_arrow_from_tower(1)
    elif key in ('D', 'd'):
        fire_arrow_from_tower(2)
    elif key in ('W', 'w'):
        try_wave_attack()
    elif key in ('T', 't'):
        spawn_player_troops()


def specialKeyListener(key, x, y):
    global camera_pos
    x_cam, y_cam, z_cam = camera_pos
    step = 25
    
    if key == GLUT_KEY_UP:
        y_cam += step
    if key == GLUT_KEY_DOWN:
        y_cam -= step
    if key == GLUT_KEY_LEFT:
        x_cam -= step
    if key == GLUT_KEY_RIGHT:
        x_cam += step

    camera_pos = (x_cam, y_cam, z_cam)


def mouseListener(button, state, x, y):
    global points
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        win_w, win_h = 1000, 800
        world_x = (x / float(win_w) - 0.5) * (GRID_LENGTH * 2 * 0.8)
        nearest_idx = None
        nearest_dx = None
        for idx, t in enumerate(towers):
            dx = abs(t["x"] - world_x)
            if nearest_dx is None or dx < nearest_dx:
                nearest_dx = dx
                nearest_idx = idx

        if nearest_idx is not None:
            upgrade_tower(nearest_idx)

def spawn_player_troops():
    global points, troop_spawn_presses, player_troops, troop_id_counter
    if points < TROOP_SPAWN_COST:
        return
    points -= TROOP_SPAWN_COST
    troop_spawn_presses += 1
    count = TROOP_BASE_COUNT + (troop_spawn_presses - 1) * TROOP_COUNT_INCREMENT
    margin = 80
    for i in range(count):
        x = random.uniform(-GRID_LENGTH + margin, GRID_LENGTH - margin)
        z = random.uniform(0 + margin, GRID_LENGTH - margin)
        player_troops.append({
            "id": troop_id_counter,
            "x": x,
            "y": 0.0,
            "z": z,
            "health": TROOP_HEALTH
        })
        troop_id_counter += 1


def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 3000)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    x, y, z = camera_pos
    gluLookAt(x, y, z,
              0, 0, 0,
              0, 1, 0)

def init_game_state():
    global towers, enemies, current_wave, game_over, points, wave_active, wave_cost_current, arrows, hit_effects, cheat_fire_accum, awaiting_next_wave, wave_reached_on_game_over, missed_bullets, player_troops, troop_spawn_presses
    towers = []
    enemies = []
    game_over = False
    current_wave = 0
    points = 0
    missed_bullets = 0
    player_troops = []
    troop_spawn_presses = 0
    arrows = []
    hit_effects = []
    wave_active = False
    wave_cost_current = WAVE_COST_BASE
    cheat_fire_accum = 0.0
    awaiting_next_wave = False
    wave_reached_on_game_over = 0

    z_back = GRID_LENGTH - 100
    for x in (-300, 0, 300):
        towers.append({
            "x": x,
            "y": 0,
            "z": z_back,
            "health": TOWER_HEALTH_MAX,
            "level": 1,
            "fire_interval": TOWER_BASE_FIRE_INTERVAL,
            "cooldown": 0.0,
            "upgrade_cost": TOWER_UPGRADE_BASE_COST
        })

def start_next_wave():
    global current_wave, enemies, enemy_id_counter
    current_wave += 1

    enemy_count = 3 + (current_wave - 1) * 3
    enemy_health = 10 + (current_wave - 1) * 2

    margin = 80
    for i in range(enemy_count):
        x = random.uniform(-GRID_LENGTH + margin, GRID_LENGTH - margin)
        z = random.uniform(-GRID_LENGTH + margin, -margin)

        r = random.random()
        prob_fast = min(0.15 + current_wave * 0.03, 0.55)
        prob_armored = min(0.10 + current_wave * 0.03, 0.5)
        prob_flying = min(0.08 + current_wave * 0.025, 0.4)

        e_type = "grunt"
        if r < prob_flying:
            e_type = "flying"
        elif r < prob_flying + prob_fast:
            e_type = "fast"
        elif r < prob_flying + prob_fast + prob_armored:
            e_type = "armored"

        speed_mult = 1.0
        health_mult = 1.0
        y_offset = 0.0
        color = (0.85, 0.15, 0.25)
        scale_mult = 1.0
        hit_radius_mult = 1.0
        if e_type == "fast":
            speed_mult = 1.6 + current_wave * 0.05
            color = (1.0, 0.5, 0.2)
        elif e_type == "armored":
            health_mult = 2.0 + current_wave * 0.15
            color = (0.6, 0.6, 0.65)
        elif e_type == "flying":
            y_offset = 35.0 + current_wave * 2.0
            speed_mult = 1.2 + current_wave * 0.04
            color = (0.7, 0.3, 1.0)

        enemies.append({
            "x": x, "y": y_offset, "z": z,
            "health": enemy_health * health_mult,
            "max_health": enemy_health * health_mult,
            "alive": True,
            "id": enemy_id_counter,
            "type": e_type,
            "speed_mult": speed_mult,
            "color": color,
            "scale_mult": scale_mult,
            "hit_radius_mult": hit_radius_mult
        })
        enemy_id_counter += 1

    if current_wave >= 4 and (current_wave - 4) % 3 == 0:
        for j in range(2):
            x = random.uniform(-GRID_LENGTH + margin, GRID_LENGTH - margin)
            z = random.uniform(-GRID_LENGTH + margin, -margin)
            enemies.append({
                "x": x, "y": 0.0, "z": z,
                "health": enemy_health * 9.0,
                "max_health": enemy_health * 9.0,
                "alive": True,
                "id": enemy_id_counter,
                "type": "big",
                "speed_mult": 0.6,
                "color": (0.05, 0.05, 0.08),
                "scale_mult": 2.0,
                "hit_radius_mult": 2.0
            })
            enemy_id_counter += 1

def update_game(dt):
    global enemies, towers, game_over, arrows, points, wave_active, wave_front_z, wave_targets, cheat_fire_accum, awaiting_next_wave, missed_bullets, player_troops
    if game_over:
        return

    if current_wave == 0 and not enemies and not awaiting_next_wave:
        start_next_wave()

    if current_wave > 0 and not enemies and not wave_active:
        awaiting_next_wave = True

    alive_towers = [t for t in towers if t["health"] > 0]
    if not alive_towers:
        game_over = True
        return

    remaining = []
    for e in enemies:
        ex, ez = e["x"], e["z"]

        alive_troops = [t for t in player_troops if t["health"] > 0]
        target_points = []
        if alive_troops:
            target_points = alive_troops
        else:
            target_points = alive_towers

        nearest = None
        best_d2 = None
        for t in target_points:
            dx_t = t["x"] - ex
            dz_t = t["z"] - ez
            d2 = dx_t*dx_t + dz_t*dz_t
            if best_d2 is None or d2 < best_d2:
                best_d2 = d2
                nearest = t

        dx = nearest["x"] - ex
        dz = nearest["z"] - ez
        dist = max(1e-5, (dx*dx + dz*dz) ** 0.5)

        step = ENEMY_SPEED * e.get("speed_mult", 1.0) * dt
        if dist > step:
            ex += dx / dist * step
            ez += dz / dist * step
            e["x"], e["z"] = ex, ez
            remaining.append(e)
        else:
            if nearest in player_troops:
                nearest["health"] = max(0.0, nearest.get("health", 0.0) - ENEMY_DAMAGE)
            else:
                nearest["health"] = max(0, nearest["health"] - ENEMY_DAMAGE)

    enemies = remaining

    troop_next = []
    for t in player_troops:
        if t["health"] <= 0:
            continue
        nearest = None
        best_d2 = None
        for e in enemies:
            if not e.get("alive", True):
                continue
            dx = e["x"] - t["x"]
            dz = e["z"] - t["z"]
            d2 = dx*dx + dz*dz
            if best_d2 is None or d2 < best_d2:
                best_d2 = d2
                nearest = e
        if nearest is not None:
            dx = nearest["x"] - t["x"]
            dz = nearest["z"] - t["z"]
            dist = max(1e-5, (dx*dx + dz*dz) ** 0.5)
            if dist > TROOP_ATTACK_RADIUS:
                step = TROOP_SPEED * dt
                t["x"] += dx / dist * step
                t["z"] += dz / dist * step
            else:
                nearest["health"] = nearest.get("health", 0.0) - TROOP_DPS * dt
                if nearest["health"] <= 0:
                    nearest["alive"] = False
                    points += POINTS_PER_KILL
        troop_next.append(t)
    player_troops = troop_next

    for t in towers:
        if t["health"] > 0:
            t["cooldown"] = max(0.0, t.get("cooldown", 0.0) - dt)

    if cheat_mode and alive_towers and not awaiting_next_wave:
        for idx, t in enumerate(towers):
            if t["health"] <= 0:
                continue
            if t.get("cooldown", 0.0) <= 0.0:
                fire_arrow_from_tower(idx)
                t["cooldown"] = t.get("fire_interval", TOWER_BASE_FIRE_INTERVAL)

    if wave_active:
        global wave_front_z
        prev_front = wave_front_z
        wave_front_z -= wave_speed * dt
        z0 = prev_front
        z1 = wave_front_z - wave_width
        for e in enemies:
            if not e.get("alive", True):
                continue
            if e.get("id") not in wave_targets:
                continue
            ez = e["z"]
            if z1 <= ez <= z0:
                if e.get("type") == "big":
                    max_health = e.get("max_health", e.get("health", 10))
                    if "max_health" not in e:
                        e["max_health"] = e.get("health", 10)
                    chip = max(BIG_WAVE_DAMAGE_MIN, BIG_WAVE_DAMAGE_PERCENT * e["max_health"])
                    e["health"] = e.get("health", 1) - chip
                    if e["health"] <= 0:
                        e["alive"] = False
                        points += POINTS_PER_KILL
                else:
                    e["alive"] = False
                    points += POINTS_PER_KILL
                hit_effects.append({
                    "x": e["x"],
                    "y": e.get("y", 0.0) + 25.0,
                    "z": e["z"],
                    "life": 1.0
                })
        if wave_front_z - wave_width < -GRID_LENGTH:
            wave_active = False
            wave_targets = set()

    next_arrows = []
    for a in arrows:
        a["ttl"] -= dt
        if a["ttl"] <= 0:
            missed_bullets += 1
            nearest_t = min(
                (t for t in towers if t["health"] > 0),
                key=lambda t: (t["x"]-a["x"])**2 + (t["z"]-a["z"])**2,
                default=None
            )
            if nearest_t is not None:
                nearest_t["health"] = max(0, nearest_t["health"] - MISSED_BULLET_DAMAGE)
            continue

        target = None
        tid = a.get("target_id")
        if tid is not None:
            for e in enemies:
                if e.get("id") == tid and e.get("alive", True):
                    target = e
                    break

        if target is not None:
            dx = target["x"] - a["x"]
            dy = (target.get("y", 0.0) + 20.0) - a["y"]
            dz = target["z"] - a["z"]
            dist = max(1e-5, (dx*dx + dy*dy + dz*dz) ** 0.5)
            a["vx"] = (dx / dist) * ARROW_SPEED
            a["vy"] = (dy / dist) * ARROW_SPEED
            a["vz"] = (dz / dist) * ARROW_SPEED

        a["x"] += a.get("vx", 0.0) * dt
        a["y"] += a.get("vy", 0.0) * dt
        a["z"] += a.get("vz", -ARROW_SPEED) * dt

        hit_any = False
        for e in enemies:
            if not e.get("alive", True):
                continue
            dx = e["x"] - a["x"]
            enemy_center_y = e.get("y", 0.0) + 20.0
            dy = enemy_center_y - a["y"]
            dz = e["z"] - a["z"]
            hit_r = ARROW_HIT_RADIUS_3D * e.get("hit_radius_mult", 1.0)
            if dx*dx + dy*dy + dz*dz <= hit_r * hit_r:
                hit_any = True
                dmg_mult = 1.0
                if towers:
                    nearest_t = min(
                        (t for t in towers if t["health"] > 0),
                        key=lambda t: (t["x"]-a["x"])**2 + (t["z"]-a["z"])**2,
                        default=None
                    )
                    if nearest_t is not None:
                        lvl = nearest_t.get("level", 1)
                        dmg_mult = 1.0 + (lvl - 1) * TOWER_DAMAGE_MULT_PER_LEVEL

                damage = ARROW_DAMAGE * dmg_mult
                e["health"] = e.get("health", 10) - damage
                hit_effects.append({"x": a["x"], "y": a["y"], "z": a["z"], "life": 1.0})
                if e["health"] <= 0:
                    e["alive"] = False
                    points += POINTS_PER_KILL
                break

        if not hit_any:
            boundary_limit = GRID_LENGTH + 10
            out_left = a["x"] < -boundary_limit
            out_right = a["x"] > boundary_limit
            out_front = a["z"] < -boundary_limit
            out_back = a["z"] > boundary_limit
            out_below = a["y"] < 0.0
            out_above = a["y"] > WALL_HEIGHT + 220.0

            if out_left or out_right or out_front or out_back or out_below or out_above:
                hit_x = max(min(a["x"], boundary_limit), -boundary_limit)
                hit_z = max(min(a["z"], boundary_limit), -boundary_limit)
                hit_effects.append({"x": hit_x, "y": a["y"], "z": hit_z, "life": 1.0})
                missed_bullets += 1
                nearest_t = min(
                    (t for t in towers if t["health"] > 0),
                    key=lambda t: (t["x"]-a["x"])**2 + (t["z"]-a["z"])**2,
                    default=None
                )
                if nearest_t is not None:
                    nearest_t["health"] = max(0, nearest_t["health"] - MISSED_BULLET_DAMAGE)
                continue

            next_arrows.append(a)

    arrows = next_arrows

    enemies = [e for e in enemies if e.get("alive", True)]

    next_fx = []
    for fx in hit_effects:
        fx["life"] -= dt / HIT_EFFECT_DURATION
        if fx["life"] > 0:
            next_fx.append(fx)
    hit_effects[:] = next_fx

    if not any(t["health"] > 0 for t in towers):
        game_over = True
        global wave_reached_on_game_over
        wave_reached_on_game_over = max(wave_reached_on_game_over, current_wave)


def idle():
    global last_update_time_ms
    now_ms = glutGet(GLUT_ELAPSED_TIME)
    if last_update_time_ms == 0:
        last_update_time_ms = now_ms
    dt = (now_ms - last_update_time_ms) / 1000.0
    last_update_time_ms = now_ms

    if not is_paused:
        update_game(dt)
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    draw_background()
    glClear(GL_DEPTH_BUFFER_BIT)

    setupCamera()

    draw_playground()
    draw_structures()
    draw_enemies()
    for t in player_troops:
        draw_troop(t["x"], t["y"], t["z"])
    for a in arrows:
        draw_arrow(a["x"], a["y"], a["z"])
    for fx in hit_effects:
        draw_hit_effect(fx["x"], fx["y"], fx["z"], fx["life"]) 
    
    draw_text(10, 770, "TOWER DEFENSE")
    cost = wave_cost_current
    draw_text(10, 740, f"My Side: Blue | Enemy Side: Pink | Wave: {current_wave} | Points: {points} | Wave Cost: {cost} | Troop Cost: {TROOP_SPAWN_COST}")
    draw_text(10, 710, f"Missed Bullets: {missed_bullets}")
    draw_text(10, 680, f"Troops: {len(player_troops)} (T to spawn, cost {TROOP_SPAWN_COST})")
    if is_paused and not game_over:
        draw_text(380, 760, "PAUSED (Space to resume, B to start)")
    if cheat_mode and not game_over:
        draw_text(800, 770, "CHEAT MODE ON")
    if awaiting_next_wave and not game_over:
        draw_text(320, 420, f"Wave {current_wave} cleared! Press Enter for Wave {current_wave+1}")

    if not game_over:
        base_y = 700
        step_y = 90
        for idx, t in enumerate(towers):
            y = base_y - idx * step_y
            dmg_mult = 1.0 + (t.get("level", 1) - 1) * TOWER_DAMAGE_MULT_PER_LEVEL
            fire_interval = t.get("fire_interval", TOWER_BASE_FIRE_INTERVAL)
            next_cost = t.get("upgrade_cost", TOWER_UPGRADE_BASE_COST)
            draw_text(750, y, f"Tower {idx+1} | Lv {t.get('level',1)}")
            draw_text(750, y-25, f"Damage x{dmg_mult:.2f}")
            draw_text(750, y-50, f"Fire {fire_interval:.2f}s")
            draw_text(750, y-75, f"Next Upgrade: {next_cost}")
    if game_over:
        draw_text(450, 500, "GAME OVER!")
        draw_text(420, 470, f"Final Score: {points}")
        draw_text(400, 440, f"Highest Wave Reached: {wave_reached_on_game_over}")
    if towers:
        alive = sum(1 for t in towers if t['health'] > 0)
        draw_text(10, 650, f"Towers Alive: {alive}/3")
    if game_over:
        draw_text(420, 400, "GAME OVER")

    glutSwapBuffers()


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Tower Defense Playground")

    global archer_quadric
    archer_quadric = gluNewQuadric()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glClearDepth(1.0)

    init_game_state()

    glutMainLoop()

if __name__ == "__main__":
    main()
