"""
chipmul8 - A CHIP-8 Emulator.
"""

import os

from click import File, argument, command, echo, option


@command()
@option('--invert_colors/--no-invert_colors', default=False, help="Inverts the black/white values for the display")
@argument("input_file", type=File("rb"), nargs=1)
def cli(invert_colors, input_file):
    """
    CLI interface for launching the emulator.

    :param invert_colors: Invert display color flag.
    :type invert_colors: bool
    :param input_file: Rom file.
    :type input_file: _io.BufferedReader
    :return: None.
    :rtype: None
    """

    # Suppress PyGame support prompt
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

    from .emulator.engine import GameEngine

    rom_file = input_file

    echo(f"Loaded rom from path: {input_file.name}")

    try:
        game = GameEngine(rom_file=rom_file, invert_colors=invert_colors)
        game.create_window()
        game.start()
    except Exception as e:
        echo(f"An exception occurred: {e}")

    echo("Goodbye, Parzival. Thank you for playing my game.")
