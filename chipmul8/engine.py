"""
Emulator game engine.
"""

import sys
from pathlib import Path

import pygame
from OpenGL.GL import glClearColor, glClear, glDrawPixels, GL_RGB, GL_UNSIGNED_BYTE, GL_COLOR_BUFFER_BIT
from pygame.locals import K_d

from chipmul8.interpreter import Interpreter


class GameEngine:
    def __init__(self, rom_path):
        """
        Initialise the game engine.

        :param rom_path: Path to the rom file.
        :type rom_path: Path
        """

        self.display_width = 64
        self.display_height = 32
        self.pixel_size = 10

        Interpreter.initialize()
        self.cpu = Interpreter()

        self.cpu.load_rom(rom_path=rom_path)

        self.window = None
        self.clock = None
        self.started = False

        self.temp_display = bytearray(self.display_width * self.display_height * 3)

    @property
    def display(self):
        """
        Retrieve interpreter display buffer.

        :return: Interpreter display buffer.
        :rtype: ndarray
        """

        return self.cpu.display_memory

    def create_window(self):
        """
        Create game window.

        :return: None.
        :rtype: None
        """

        pygame.init()

        self.window = pygame.display.set_mode(
            (self.display_width, self.display_height),
            pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
        )

        self.clock = pygame.time.Clock()

    def draw(self):
        """
        Render interpreter display buffer to the game screen.

        :return: None.
        :rtype: None
        """

        if self.cpu.frame_ready:
            for index, value in enumerate(reversed(self.display.ravel())):
                r = index * 3
                g = r + 1
                b = r + 2

                pixel_color = 0 if value == 1 else 255

                self.temp_display[r] = pixel_color
                self.temp_display[g] = pixel_color
                self.temp_display[b] = pixel_color

            glClearColor(0, 0, 0, 1)
            glClear(GL_COLOR_BUFFER_BIT)

            glDrawPixels(*(self.display_width, self.display_height), GL_RGB, GL_UNSIGNED_BYTE, self.temp_display)

            # Update display.
            pygame.display.flip()

            self.cpu.frame_ready = False
            self.cpu.temp = []

    def _key(self, key, down=True):
        """
        Handle key press.

        :param key: Key on which the event was registered.
        :type key: int
        :param down: Flag indicating whether the key registered was registered on the up or down stroke.
        :type down: bool
        :return: None.
        :rtype: None
        """

        print("Key", key, type(key))

        if key == K_d:
            self.cpu.keyboard[5] = down

    def start(self):
        """
        Start the game loop.

        :return: None.
        :rtype: None
        """

        while True:
            # Trigger an interpreter cycle to process the next instruction.
            self.cpu.emulate()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    print(event.size)
                elif event.type == pygame.KEYDOWN:
                    self._key(event.key)
                elif event.type == pygame.KEYUP:
                    self._key(event.key, down=False)

            self.draw()
