"""
Emulator game engine.
"""

from pathlib import Path

import pygame
from OpenGL.GL import glClearColor, glClear, glDrawPixels, GL_RGB, GL_UNSIGNED_BYTE, GL_COLOR_BUFFER_BIT
from pygame.locals import (K_1, K_2, K_3, K_4, K_q, K_w, K_e, K_r, K_a, K_s, K_d, K_f, K_z, K_x, K_c, K_v)

from chipmul8.emulator.interpreter import Interpreter

keymap = {
    # 1 2 3 4 => 1 2 3 C
    # q w e r => 4 5 6 D
    # a s d f => 7 8 9 E
    # z x c v => A 0 B F

    K_1: 1,  K_2: 2, K_3: 3,  K_4: 12,
    K_q: 4,  K_w: 5, K_e: 6,  K_r: 13,
    K_a: 7,  K_s: 8, K_d: 9,  K_f: 14,
    K_z: 10, K_x: 0, K_c: 11, K_v: 15
}


class GameEngine:
    def __init__(self, rom_file, invert_colors=False):
        """
        Initialise the game engine.

        :param rom_file: Rom file.
        :type rom_file: _io.BufferedReader
        :param invert_colors: Invert display color flag
        :type invert_colors: bool
        """

        self.display_width = 64
        self.display_height = 32
        self.pixel_size = 10

        self._invert_colors = invert_colors

        Interpreter.initialize()
        self.cpu = Interpreter()

        rom_path = Path(rom_file.name)

        self.cpu.load_rom(rom_file)

        self.rom_name = rom_path.name[:len(rom_path.suffix) + 2]

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

        pygame.display.set_caption(self.rom_name)

        self.clock = pygame.time.Clock()

    def _pixel_color(self, value):
        """
        Determine pixel color.

        :param value: Interpreter display pixel (1 if filled, 0 is not filled).
        :type value: int
        :return: Pixel color value.
        :rtype: int
        """

        if self._invert_colors:
            return 255 if value == 1 else 0
        else:
            return 0 if value == 1 else 255

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

                pixel_color = self._pixel_color(value)

                self.temp_display[r] = pixel_color
                self.temp_display[g] = pixel_color
                self.temp_display[b] = pixel_color

            glClearColor(0, 0, 0, 1)
            glClear(GL_COLOR_BUFFER_BIT)

            glDrawPixels(*(self.display_width, self.display_height), GL_RGB, GL_UNSIGNED_BYTE, self.temp_display)

            # Update display.
            pygame.display.flip()

            self.cpu.frame_ready = False

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

        if key in keymap:
            self.cpu.keyboard[keymap[key]] = down

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
                    return
                elif event.type == pygame.VIDEORESIZE:
                    print(event.size)
                elif event.type == pygame.KEYDOWN:
                    self._key(event.key)
                elif event.type == pygame.KEYUP:
                    self._key(event.key, down=False)

            self.draw()
