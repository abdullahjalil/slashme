# packages
import pygame
import math
import numpy as np
import moderngl # documenntation: https://moderngl.readthedocs.io/en/5.8.2/
from pyrr import Matrix44 # Maths library for convenient functions and conversions

# initializing the game(pygame)
pygame.init()
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)


# Set up display
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height), pygame.OPENGL | pygame.DOUBLEBUF)
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# ModernGL context
ctx = moderngl.create_context()

# Enable depth testing
ctx.enable(moderngl.DEPTH_TEST)

# Shader program
vertex_shader = """
#version 330 core

in vec3 in_position;
in vec3 in_color;

uniform mat4 projection;
uniform mat4 modelview;

out vec3 color;

void main() {
    gl_Position = projection * modelview * vec4(in_position, 1.0);
    color = in_color;
}
"""

fragment_shader = """
#version 330 core

in vec3 color;
out vec4 frag_color;

void main() {
    frag_color = vec4(color, 1.0);
}
"""

prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

# Create a simple cube
def create_cube():
    vertices = [
        # Front face
        -0.5, -0.5,  0.5, 1.0, 0.0, 0.0,
         0.5, -0.5,  0.5, 1.0, 0.0, 0.0,
         0.5,  0.5,  0.5, 1.0, 0.0, 0.0,
        -0.5,  0.5,  0.5, 1.0, 0.0, 0.0,
        
        # Back face
        -0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
         0.5, -0.5, -0.5, 0.0, 1.0, 0.0,
         0.5,  0.5, -0.5, 0.0, 1.0, 0.0,
        -0.5,  0.5, -0.5, 0.0, 1.0, 0.0,
        
        # Top face
        -0.5,  0.5, -0.5, 0.0, 0.0, 1.0,
         0.5,  0.5, -0.5, 0.0, 0.0, 1.0,
         0.5,  0.5,  0.5, 0.0, 0.0, 1.0,
        -0.5,  0.5,  0.5, 0.0, 0.0, 1.0,
        
        # Bottom face
        -0.5, -0.5, -0.5, 1.0, 1.0, 0.0,
         0.5, -0.5, -0.5, 1.0, 1.0, 0.0,
         0.5, -0.5,  0.5, 1.0, 1.0, 0.0,
        -0.5, -0.5,  0.5, 1.0, 1.0, 0.0,
        
        # Right face
         0.5, -0.5, -0.5, 1.0, 0.0, 1.0,
         0.5,  0.5, -0.5, 1.0, 0.0, 1.0,
         0.5,  0.5,  0.5, 1.0, 0.0, 1.0,
         0.5, -0.5,  0.5, 1.0, 0.0, 1.0,
        
        # Left face
        -0.5, -0.5, -0.5, 0.0, 1.0, 1.0,
        -0.5,  0.5, -0.5, 0.0, 1.0, 1.0,
        -0.5,  0.5,  0.5, 0.0, 1.0, 1.0,
        -0.5, -0.5,  0.5, 0.0, 1.0, 1.0,
    ]
    
    indices = [
        0, 1, 2, 2, 3, 0,    # Front
        4, 5, 6, 6, 7, 4,    # Back
        8, 9, 10, 10, 11, 8, # Top
        12, 13, 14, 14, 15, 12, # Bottom
        16, 17, 18, 18, 19, 16, # Right
        20, 21, 22, 22, 23, 20  # Left
    ]
    
    vbo = ctx.buffer(np.array(vertices, dtype='f4'))
    ibo = ctx.buffer(np.array(indices, dtype='i4'))
    
    vao = ctx.vertex_array(
        prog,
        [
            (vbo, '3f 3f', 'in_position', 'in_color')
        ],
        ibo
    )
    
    return vao

# Create a ground plane
def create_ground():
    vertices = [
        -10.0, -0.5, -10.0, 0.5, 0.5, 0.5,
         10.0, -0.5, -10.0, 0.5, 0.5, 0.5,
         10.0, -0.5,  10.0, 0.5, 0.5, 0.5,
        -10.0, -0.5,  10.0, 0.5, 0.5, 0.5,
    ]
    
    indices = [0, 1, 2, 2, 3, 0]
    
    vbo = ctx.buffer(np.array(vertices, dtype='f4'))
    ibo = ctx.buffer(np.array(indices, dtype='i4'))
    
    vao = ctx.vertex_array(
        prog,
        [
            (vbo, '3f 3f', 'in_position', 'in_color')
        ],
        ibo
    )
    
    return vao

# Create objects
player_cube = create_cube()
ground = create_ground()
obstacles = [create_cube() for _ in range(5)]
obstacle_positions = [
    (2, 0, 2),
    (-2, 0, 3),
    (4, 0, -1),
    (-3, 0, -4),
    (0, 0, -2)
]

# Camera settings
class Camera:
    def __init__(self):
        self.position = np.array([0.0, 2.0, 5.0], dtype='f4')
        self.pitch = 0.0
        self.yaw = -90.0
        self.distance_from_player = 5.0
        self.angle_around_player = 0.0
    
    def update(self, player_pos, player_rot_y):
        # Calculate camera position based on player position and rotation
        theta = player_rot_y + self.angle_around_player
        offset_x = self.distance_from_player * math.sin(math.radians(theta))
        offset_z = self.distance_from_player * math.cos(math.radians(theta))
        
        self.position[0] = player_pos[0] - offset_x
        self.position[1] = player_pos[1] + 2.0  # Height above player
        self.position[2] = player_pos[2] - offset_z
        
        # Calculate look-at point slightly above player
        look_at = np.array([
            player_pos[0],
            player_pos[1] + 1.0,
            player_pos[2]
        ], dtype='f4')
        
        return Matrix44.look_at(
            self.position,
            look_at,
            (0.0, 1.0, 0.0)
        )

camera = Camera()

# Player settings
class Player:
    def __init__(self):
        self.position = np.array([0.0, 0.0, 0.0], dtype='f4')
        self.rotation_y = 0.0
        self.speed = 0.1
    
    def move(self, dx, dz):
        # Move player based on current rotation
        self.position[0] += dx * math.cos(math.radians(self.rotation_y)) - dz * math.sin(math.radians(self.rotation_y))
        self.position[2] += dx * math.sin(math.radians(self.rotation_y)) + dz * math.cos(math.radians(self.rotation_y))
    
    def get_model_matrix(self):
        # Create transformation matrix for player
        model = Matrix44.from_translation(self.position)
        model = model * Matrix44.from_y_rotation(math.radians(self.rotation_y))
        return model

player = Player()

# Projection matrix
projection = Matrix44.perspective_projection(45.0, screen_width / screen_height, 0.1, 100.0)

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        elif event.type == pygame.MOUSEMOTION:
            # Mouse look
            dx, dy = event.rel
            player.rotation_y -= dx * 0.1
            camera.angle_around_player -= dx * 0.1
            camera.pitch = max(-89.0, min(89.0, camera.pitch + dy * 0.1))
    
    # Handle keyboard input for movement
    keys = pygame.key.get_pressed()
    move_x, move_z = 0.0, 0.0
    
    if keys[pygame.K_w]:
        move_z = -player.speed
    if keys[pygame.K_s]:
        move_z = player.speed
    if keys[pygame.K_a]:
        move_x = -player.speed
    if keys[pygame.K_d]:
        move_x = player.speed
    
    player.move(move_x, move_z)
    
    # Clear screen
    ctx.clear(0.1, 0.1, 0.1)
    
    # Update camera
    view = camera.update(player.position, player.rotation_y)
    
    # Draw ground
    ground_model = Matrix44.from_translation((0, 0, 0))
    prog['projection'].write(projection.astype('f4'))
    prog['modelview'].write((view * ground_model).astype('f4'))
    ground.render()
    
    # Draw player
    player_model = player.get_model_matrix()
    prog['modelview'].write((view * player_model).astype('f4'))
    player_cube.render()
    
    # Draw obstacles
    for i, obstacle in enumerate(obstacles):
        obstacle_model = Matrix44.from_translation(obstacle_positions[i])
        prog['modelview'].write((view * obstacle_model).astype('f4'))
        obstacle.render()
    
    # Swap buffers
    pygame.display.flip()
    clock.tick(60)

pygame.quit()