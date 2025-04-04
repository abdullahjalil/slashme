# packages
import pygame
import math
import numpy as np
import moderngl # documenntation: https://moderngl.readthedocs.io/en/5.8.2/
import pyrr import Matrix44 # Maths library for convenient functions and conversions

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