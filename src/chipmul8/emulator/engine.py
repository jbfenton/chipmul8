"""
Emulator game engine.
"""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Final

import pygame
from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_RGB, GL_UNSIGNED_BYTE, glClear, glClearColor, glDrawPixels
from pygame.locals import K_1, K_2, K_3, K_4, K_a, K_c, K_d, K_e, K_f, K_q, K_r, K_s, K_v, K_w, K_x, K_z

from chipmul8.emulator.interpreter import Interpreter

if TYPE_CHECKING:
    from io import BufferedReader

    import numpy as np
    import numpy.typing as npt

# fmt: off
keymap: Final = MappingProxyType(
    {
        # 1 2 3 4 => 1 2 3 C
        # q w e r => 4 5 6 D
        # a s d f => 7 8 9 E
        # z x c v => A 0 B F
        K_1: 1,  K_2: 2, K_3: 3,  K_4: 12,
        K_q: 4,  K_w: 5, K_e: 6,  K_r: 13,
        K_a: 7,  K_s: 8, K_d: 9,  K_f: 14,
        K_z: 10, K_x: 0, K_c: 11, K_v: 15,
    }
)
# fmt: on

class GameEngine:
    clock: pygame.time.Clock

    def __init__(self, rom_file: BufferedReader, invert_colors: bool = False) -> None:
        """
        Initialise the game engine.

        :param rom_file: Rom file.
        :param invert_colors: Invert display colour flag
        """
        self.display_width: int = 64
        self.display_height: int = 32
        self.pixel_size: int = 10

        self._invert_colors = invert_colors

        Interpreter.initialize()
        self.cpu = Interpreter()

        rom_path = Path(rom_file.name)

        self.cpu.load_rom(rom_file)

        self.rom_name = rom_path.name[: len(rom_path.suffix) + 2]

        self.window: pygame.Surface | None = None
        self.started = False

        self.temp_display = bytearray(self.display_width * self.display_height * 3)

    @property
    def display(self) -> npt.NDArray[np.int8]:
        """
        Retrieve interpreter display buffer.

        :return: Interpreter display buffer.
        :rtype: ndarray
        """
        return self.cpu.display_memory

    def create_window(self) -> None:
        """
        Create game window.

        :return: None.
        """
        pygame.init()

        self.window = pygame.display.set_mode(
            (self.display_width, self.display_height), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE
        )

        pygame.display.set_caption(self.rom_name)

        self.clock = pygame.time.Clock()

    def _pixel_color(self, value: int) -> int:
        """
        Determine pixel colour.

        :param value: Interpreter display pixel (1 if filled, 0 is not filled).
        :return: Pixel colour value.
        """
        if self._invert_colors:
            return 255 if value == 1 else 0

        return 0 if value == 1 else 255

    def draw(self) -> None:
        """
        Render interpreter display buffer to the game screen.

        :return: None.
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

    def _key(self, key: int, down: bool = True) -> None:
        """
        Handle key press.

        :param key: Key on which the event was registered.
        :param down: Flag indicating whether the key registered was registered on the up or down stroke.
        :return: None.
        """
        if key in keymap:
            self.cpu.keyboard[keymap[key]] = down

    def start(self) -> None:
        """
        Start the game loop.

        :return: None.
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
