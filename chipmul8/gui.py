"""
Emulator GUI.
"""

import sys
from pathlib import Path
from tkinter import Tk
from tkinter import filedialog

import pygame
from pygame.locals import *

from .interpreter import Interpreter


class GameEngine:
    """
    PyGame based game engine.
    """

    def __init__(self, rom_path=None):
        """
        Create an GameEngine instance.

        :param rom_path: Path to emulator ROM file.
        :type rom_path: str
        """

        self.display_width = 640
        self.display_height = 320

        self.drawing_surface_width = 64
        self.drawing_surface_height = 32

        pygame.init()
        Interpreter.initialize()

        self.interpreter = Interpreter()
        self.interpreter.load_rom(self._validate_rom_path(rom_path))

        self.clock = pygame.time.Clock()
        self.display_window = pygame.display.set_mode((self.display_width, self.display_height), pygame.DOUBLEBUF)
        self.drawing_surface = pygame.Surface((self.drawing_surface_width, self.drawing_surface_height))

    def _validate_rom_path(self, rom_path):
        """
        Validate rom path.

        :param rom_path: Path to ROM file on disk.
        :type rom_path: str or None
        :return: Rom path.
        :rtype: str
        """

        if not rom_path:
            Tk().withdraw()
            rom_path = filedialog.askopenfilename(
                title="Select ROM",
                filetypes=(
                    ("CHIP-8 ROMs", "*.c8"),
                    ("all files", "*.*")
                )
            )

        if Path(rom_path).exists():
            return rom_path
        else:
            print("Rom path does not exist")
            self.quit()

    def draw(self):
        """
        Draw frame.

        :return: None
        :rtype: None
        """

        if self.interpreter.frame_ready:
            for row in range(0, self.drawing_surface_height):
                for column in range(0, self.drawing_surface_width):
                    pixel_color = (255, 255, 255) if self.interpreter.display_memory[row, column] == 1 else (0, 0, 0)

                    pygame.draw.rect(
                        self.drawing_surface,
                        pixel_color,
                        (
                            column,
                            row,
                            10,
                            10
                        )
                    )

            # Screen scaling
            # https://stackoverflow.com/questions/43196126/how-do-you-scale-a-design-resolution-to-other-resolutions-with-pygame
            frame = pygame.transform.scale(self.drawing_surface, (self.display_width, self.display_height))
            self.display_window.blit(frame, frame.get_rect())

            pygame.display.flip()

    def _key(self, key, down=True):
        """
        Handle key press.

        :param key: Pressed key.
        :type key: int
        :param down: Key state.
        :type down: bool
        :return: None
        :rtype: None
        """

        if key == K_d:
            self.interpreter.keyboard[5] = down

    @staticmethod
    def quit():
        """
        Terminate game session and exit.

        :return: None
        :rtype: None
        """

        pygame.display.quit()
        pygame.quit()

        sys.exit()

    def start(self):
        """
        Start the game loop.

        :return: None
        :rtype: None
        """

        while True:
            self.interpreter.emulate()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.VIDEORESIZE:
                    print(event.size)
                elif event.type == pygame.KEYDOWN:
                    self._key(event.key)
                elif event.type == pygame.KEYUP:
                    self._key(event.key, down=False)

            self.draw()
            self.clock.tick(120)

            print(self.clock.get_fps())
