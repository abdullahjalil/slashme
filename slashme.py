import pygame
import math
import numpy as np
import moderngl
from pyrr import Matrix44

# Initialize pygame
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

# Camera class
class Camera:
    def __init__(self):
        self.position = np.array([0.0, 2.0, 5.0], dtype='f4')
        self.front = np.array([0.0, 0.0, -1.0], dtype='f4')
        self.up = np.array([0.0, 1.0, 0.0], dtype='f4')
        self.right = np.array([1.0, 0.0, 0.0], dtype='f4')
        self.world_up = np.array([0.0, 1.0, 0.0], dtype='f4')
        self.yaw = -90.0
        self.pitch = 0.0
        self.distance_from_player = 5.0
    
    def update(self, player_pos):
        # Calculate camera position behind the player
        self.position = player_pos - (self.front * self.distance_from_player)
        self.position[1] += 2.0  # Raise camera slightly
        
        # Update view matrix
        return Matrix44.look_at(
            self.position,
            player_pos + self.front,
            self.up
        )
    
    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        sensitivity = 0.1
        xoffset *= sensitivity
        yoffset *= sensitivity
        
        self.yaw += xoffset
        self.pitch += yoffset
        
        if constrain_pitch:
            self.pitch = max(-89.0, min(89.0, self.pitch))
        
        self.update_camera_vectors()
    
    def update_camera_vectors(self):
        front = np.array([0.0, 0.0, 0.0], dtype='f4')
        front[0] = math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        front[1] = math.sin(math.radians(self.pitch))
        front[2] = math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch))
        self.front = front / np.linalg.norm(front)
        
        self.right = np.cross(self.front, self.world_up)
        self.right = self.right / np.linalg.norm(self.right)
        
        self.up = np.cross(self.right, self.front)
        self.up = self.up / np.linalg.norm(self.up)

# Player class
class Player:
    def __init__(self):
        self.position = np.array([0.0, 0.0, 0.0], dtype='f4')
        self.speed = 0.1
    
    def move(self, camera, direction):
        # Move in camera's forward direction (ignore pitch for horizontal movement)
        move_dir = np.array([camera.front[0], 0.0, camera.front[2]], dtype='f4')
        move_dir = move_dir / np.linalg.norm(move_dir)
        
        if direction == "forward":
            self.position += move_dir * self.speed
        elif direction == "backward":
            self.position -= move_dir * self.speed
        elif direction == "left":
            # Strafe left using camera's right vector
            strafe_dir = np.array([camera.right[0], 0.0, camera.right[2]], dtype='f4')
            strafe_dir = strafe_dir / np.linalg.norm(strafe_dir)
            self.position -= strafe_dir * self.speed
        elif direction == "right":
            # Strafe right using camera's right vector
            strafe_dir = np.array([camera.right[0], 0.0, camera.right[2]], dtype='f4')
            strafe_dir = strafe_dir / np.linalg.norm(strafe_dir)
            self.position += strafe_dir * self.speed
    
    def get_model_matrix(self):
        # Player always faces camera front direction (ignoring pitch)
        yaw = math.degrees(math.atan2(camera.front[0], camera.front[2]))
        model = Matrix44.from_translation(self.position)
        model = model * Matrix44.from_y_rotation(math.radians(yaw))
        return model

# Create objects
player = Player()
camera = Camera()
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
            x, y = event.rel
            camera.process_mouse_movement(x, -y)  # Negative y because pygame y-coordinates are inverted
    
    # Handle keyboard input for movement
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_w]:
        player.move(camera, "forward")
    if keys[pygame.K_s]:
        player.move(camera, "backward")
    if keys[pygame.K_a]:
        player.move(camera, "left")
    if keys[pygame.K_d]:
        player.move(camera, "right")
    
    # Clear screen
    ctx.clear(0.1, 0.1, 0.1)
    
    # Update camera and get view matrix
    view = camera.update(player.position + np.array([0.0, 1.0, 0.0], dtype='f4'))  # Look at player's head
    
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
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()