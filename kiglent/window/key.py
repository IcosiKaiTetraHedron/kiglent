"""Key constants and utilities for kiglent.window.

Usage::

    from kiglent.window import Window
    from kiglent.window import key

    window = Window()

    @window.event
    def on_key_press(symbol, modifiers):
        # Symbolic names:
        if symbol == key.RETURN:

        # Alphabet keys:
        elif symbol == key.Z:

        # Number keys:
        elif symbol == key._1:

        # Number keypad keys:
        elif symbol == key.NUM_1:

        # Modifiers:
        if modifiers & key.MOD_CTRL:

"""
from __future__ import annotations

from kiglent import compat_platform
from kiglent.event import EventHandler


class KeyStateHandler(EventHandler):
    """Simple handler that tracks the state of keys on the keyboard.

    If a key is pressed then this handler holds a ``True`` value for it.
    If the window loses focus, all keys will be reset to ``False`` to avoid a
    "sticky" key state.

    For example::

        >>> win = window.Window
        >>> keyboard = key.KeyStateHandler()
        >>> win.push_handlers(keyboard)

        # Hold down the "up" arrow...

        >>> keyboard[key.UP]
        True
        >>> keyboard[key.DOWN]
        False

    """
    def __init__(self) -> None:  # noqa: D107
        self.data = {}

    def on_key_press(self, symbol: int, modifiers: int) -> None:  # noqa: ARG002
        self.data[symbol] = True

    def on_key_release(self, symbol: int, modifiers: int) -> None:  # noqa: ARG002
        self.data[symbol] = False

    def on_deactivate(self) -> None:
        self.data.clear()

    def __getitem__(self, key: int) -> bool:
        return self.data.get(key, False)


def modifiers_string(modifiers: int) -> str:
    """Return a string describing a set of modifiers.

    Example::

        >>> modifiers_string(MOD_SHIFT | MOD_CTRL)
        'MOD_SHIFT|MOD_CTRL'

    Args:
        modifiers:
            Bitwise combination of modifier constants.
    """
    mod_names = []
    if modifiers & MOD_SHIFT:
        mod_names.append('MOD_SHIFT')
    if modifiers & MOD_CTRL:
        mod_names.append('MOD_CTRL')
    if modifiers & MOD_ALT:
        mod_names.append('MOD_ALT')
    if modifiers & MOD_CAPSLOCK:
        mod_names.append('MOD_CAPSLOCK')
    if modifiers & MOD_NUMLOCK:
        mod_names.append('MOD_NUMLOCK')
    if modifiers & MOD_SCROLLLOCK:
        mod_names.append('MOD_SCROLLLOCK')
    if modifiers & MOD_COMMAND:
        mod_names.append('MOD_COMMAND')
    if modifiers & MOD_OPTION:
        mod_names.append('MOD_OPTION')
    if modifiers & MOD_FUNCTION:
        mod_names.append('MOD_FUNCTION')
    return '|'.join(mod_names)


def symbol_string(symbol: int) -> str:
    """Return a string describing a key symbol from a key constant.

    Example::

        >>> symbol_string(BACKSPACE)
        'BACKSPACE'
    """
    if symbol < 1 << 32:
        return _key_names.get(symbol, str(symbol))

    return 'user_key(%x)' % (symbol >> 32)


def motion_string(motion: int) -> str:
    """Return a string describing a text motion from a motion constant.

    Example::

        >>> motion_string(MOTION_NEXT_WORD)
        'MOTION_NEXT_WORD'
    """
    return _motion_names.get(motion, str(motion))


def user_key(scancode: int) -> int:
    """Return a key symbol for a key not supported by kiglent.

    This can be used to map virtual keys or scancodes from unsupported
    keyboard layouts into a machine-specific symbol.  The symbol will
    be meaningless on any other machine, or under a different keyboard layout.

    Applications should use user-keys only when user explicitly binds them
    (for example, mapping keys to actions in a game options screen).
    """
    assert scancode > 0
    return scancode << 32

# Modifier mask constants
MOD_SHIFT       = 1 << 0
MOD_CTRL        = 1 << 1
MOD_ALT         = 1 << 2
MOD_CAPSLOCK    = 1 << 3
MOD_NUMLOCK     = 1 << 4
MOD_WINDOWS     = 1 << 5
MOD_COMMAND     = 1 << 6
MOD_OPTION      = 1 << 7
MOD_SCROLLLOCK  = 1 << 8
MOD_FUNCTION    = 1 << 9

#: Accelerator modifier.  On Windows and Linux, this is ``MOD_CTRL``, on
#: Mac OS X it's ``MOD_COMMAND``.
MOD_ACCEL = MOD_CTRL
if compat_platform == 'darwin':
    MOD_ACCEL = MOD_COMMAND


# Key symbol constants

# ASCII commands
BACKSPACE     = 0xff08
TAB           = 0xff09
LINEFEED      = 0xff0a
CLEAR         = 0xff0b
RETURN        = 0xff0d
ENTER         = 0xff0d      # synonym
PAUSE         = 0xff13
SCROLLLOCK    = 0xff14
SYSREQ        = 0xff15
ESCAPE        = 0xff1b

# Cursor control and motion
HOME          = 0xff50
LEFT          = 0xff51
UP            = 0xff52
RIGHT         = 0xff53
DOWN          = 0xff54
PAGEUP        = 0xff55
PAGEDOWN      = 0xff56
END           = 0xff57
BEGIN         = 0xff58

# Misc functions
DELETE        = 0xffff
SELECT        = 0xff60
PRINT         = 0xff61
EXECUTE       = 0xff62
INSERT        = 0xff63
UNDO          = 0xff65
REDO          = 0xff66
MENU          = 0xff67
FIND          = 0xff68
CANCEL        = 0xff69
HELP          = 0xff6a
BREAK         = 0xff6b
MODESWITCH    = 0xff7e
SCRIPTSWITCH  = 0xff7e
FUNCTION      = 0xffd2

# Text motion constants
# These are allowed to clash with key constants since they are
# abstractions of keyboard shortcuts. See the following for more
# information:
#
# 1. doc/programming_guide/keyboard.rst
# 2. doc/modules/window_key.rst
#
# To add new motions, consult the Adding New Motions section of
# doc/programming_guide/keyboard.rst
MOTION_UP                = UP
MOTION_RIGHT             = RIGHT
MOTION_DOWN              = DOWN
MOTION_LEFT              = LEFT
MOTION_NEXT_WORD         = 1
MOTION_PREVIOUS_WORD     = 2
MOTION_BEGINNING_OF_LINE = 3
MOTION_END_OF_LINE       = 4
MOTION_NEXT_PAGE         = PAGEDOWN
MOTION_PREVIOUS_PAGE     = PAGEUP
MOTION_BEGINNING_OF_FILE = 5
MOTION_END_OF_FILE       = 6
MOTION_BACKSPACE         = BACKSPACE
MOTION_DELETE            = DELETE
MOTION_COPY              = 7
MOTION_PASTE             = 8

# Number pad
NUMLOCK       = 0xff7f
NUM_SPACE     = 0xff80
NUM_TAB       = 0xff89
NUM_ENTER     = 0xff8d
NUM_F1        = 0xff91
NUM_F2        = 0xff92
NUM_F3        = 0xff93
NUM_F4        = 0xff94
NUM_HOME      = 0xff95
NUM_LEFT      = 0xff96
NUM_UP        = 0xff97
NUM_RIGHT     = 0xff98
NUM_DOWN      = 0xff99
NUM_PRIOR     = 0xff9a
NUM_PAGE_UP   = 0xff9a
NUM_NEXT      = 0xff9b
NUM_PAGE_DOWN = 0xff9b
NUM_END       = 0xff9c
NUM_BEGIN     = 0xff9d
NUM_INSERT    = 0xff9e
NUM_DELETE    = 0xff9f
NUM_EQUAL     = 0xffbd
NUM_MULTIPLY  = 0xffaa
NUM_ADD       = 0xffab
NUM_SEPARATOR = 0xffac
NUM_SUBTRACT  = 0xffad
NUM_DECIMAL   = 0xffae
NUM_DIVIDE    = 0xffaf

NUM_0         = 0xffb0
NUM_1         = 0xffb1
NUM_2         = 0xffb2
NUM_3         = 0xffb3
NUM_4         = 0xffb4
NUM_5         = 0xffb5
NUM_6         = 0xffb6
NUM_7         = 0xffb7
NUM_8         = 0xffb8
NUM_9         = 0xffb9

# Function keys
F1            = 0xffbe
F2            = 0xffbf
F3            = 0xffc0
F4            = 0xffc1
F5            = 0xffc2
F6            = 0xffc3
F7            = 0xffc4
F8            = 0xffc5
F9            = 0xffc6
F10           = 0xffc7
F11           = 0xffc8
F12           = 0xffc9
F13           = 0xffca
F14           = 0xffcb
F15           = 0xffcc
F16           = 0xffcd
F17           = 0xffce
F18           = 0xffcf
F19           = 0xffd0
F20           = 0xffd1
F21           = 0xffd2
F22           = 0xffd3
F23           = 0xffd4
F24           = 0xffd5
# Modifiers
LSHIFT        = 0xffe1
RSHIFT        = 0xffe2
LCTRL         = 0xffe3
RCTRL         = 0xffe4
CAPSLOCK      = 0xffe5
LMETA         = 0xffe7
RMETA         = 0xffe8
LALT          = 0xffe9
RALT          = 0xffea
LWINDOWS      = 0xffeb
RWINDOWS      = 0xffec
LCOMMAND      = 0xffed
RCOMMAND      = 0xffee
LOPTION       = 0xffef
ROPTION       = 0xfff0

# Latin-1
SPACE         = 0x020
EXCLAMATION   = 0x021
DOUBLEQUOTE   = 0x022
HASH          = 0x023
POUND         = 0x023  # synonym
DOLLAR        = 0x024
PERCENT       = 0x025
AMPERSAND     = 0x026
APOSTROPHE    = 0x027
PARENLEFT     = 0x028
PARENRIGHT    = 0x029
ASTERISK      = 0x02a
PLUS          = 0x02b
COMMA         = 0x02c
MINUS         = 0x02d
PERIOD        = 0x02e
SLASH         = 0x02f
_0            = 0x030
_1            = 0x031
_2            = 0x032
_3            = 0x033
_4            = 0x034
_5            = 0x035
_6            = 0x036
_7            = 0x037
_8            = 0x038
_9            = 0x039
COLON         = 0x03a
SEMICOLON     = 0x03b
LESS          = 0x03c
EQUAL         = 0x03d
GREATER       = 0x03e
QUESTION      = 0x03f
AT            = 0x040
BRACKETLEFT   = 0x05b
BACKSLASH     = 0x05c
BRACKETRIGHT  = 0x05d
ASCIICIRCUM   = 0x05e
UNDERSCORE    = 0x05f
GRAVE         = 0x060
QUOTELEFT     = 0x060
A             = 0x061
B             = 0x062
C             = 0x063
D             = 0x064
E             = 0x065
F             = 0x066
G             = 0x067
H             = 0x068
I             = 0x069
J             = 0x06a
K             = 0x06b
L             = 0x06c
M             = 0x06d
N             = 0x06e
O             = 0x06f
P             = 0x070
Q             = 0x071
R             = 0x072
S             = 0x073
T             = 0x074
U             = 0x075
V             = 0x076
W             = 0x077
X             = 0x078
Y             = 0x079
Z             = 0x07a
BRACELEFT     = 0x07b
BAR           = 0x07c
BRACERIGHT    = 0x07d
ASCIITILDE    = 0x07e


motion_dict = {
    MOTION_UP: "MOTION_UP",
    MOTION_RIGHT: "MOTION_RIGHT",
    MOTION_DOWN: "MOTION_DOWN",
    MOTION_LEFT: "MOTION_LEFT",
    MOTION_NEXT_WORD: "MOTION_NEXT_WORD",
    MOTION_PREVIOUS_WORD: "MOTION_PREVIOUS_WORD",
    MOTION_BEGINNING_OF_LINE: "MOTION_BEGINNING_OF_LINE",
    MOTION_END_OF_LINE: "MOTION_END_OF_LINE",
    MOTION_NEXT_PAGE: "MOTION_NEXT_PAGE",
    MOTION_PREVIOUS_PAGE: "MOTION_PREVIOUS_PAGE",
    MOTION_BEGINNING_OF_FILE: "MOTION_BEGINNING_OF_FILE",
    MOTION_END_OF_FILE: "MOTION_END_OF_FILE",
    MOTION_BACKSPACE: "MOTION_BACKSPACE",
    MOTION_DELETE: "MOTION_DELETE",
    MOTION_COPY: "MOTION_COPY",
    MOTION_PASTE: "MOTION_PASTE",
}


key_dict = {
    NUMLOCK: "NUMLOCK",
    NUM_SPACE: "NUM_SPACE",
    NUM_TAB: "NUM_TAB",
    NUM_ENTER: "NUM_ENTER",
    NUM_F1: "NUM_F1",
    NUM_F2: "NUM_F2",
    NUM_F3: "NUM_F3",
    NUM_F4: "NUM_F4",
    NUM_HOME: "NUM_HOME",
    NUM_LEFT: "NUM_LEFT",
    NUM_UP: "NUM_UP",
    NUM_RIGHT: "NUM_RIGHT",
    NUM_DOWN: "NUM_DOWN",
    NUM_PRIOR: "NUM_PRIOR",
    NUM_PAGE_UP: "NUM_PAGE_UP",
    NUM_NEXT: "NUM_NEXT",
    NUM_PAGE_DOWN: "NUM_PAGE_DOWN",
    NUM_END: "NUM_END",
    NUM_BEGIN: "NUM_BEGIN",
    NUM_INSERT: "NUM_INSERT",
    NUM_DELETE: "NUM_DELETE",
    NUM_EQUAL: "NUM_EQUAL",
    NUM_MULTIPLY: "NUM_MULTIPLY",
    NUM_ADD: "NUM_ADD",
    NUM_SEPARATOR: "NUM_SEPARATOR",
    NUM_SUBTRACT: "NUM_SUBTRACT",
    NUM_DECIMAL: "NUM_DECIMAL",
    NUM_DIVIDE: "NUM_DIVIDE",
    NUM_0: "NUM_0",
    NUM_1: "NUM_1",
    NUM_2: "NUM_2",
    NUM_3: "NUM_3",
    NUM_4: "NUM_4",
    NUM_5: "NUM_5",
    NUM_6: "NUM_6",
    NUM_7: "NUM_7",
    NUM_8: "NUM_8",
    NUM_9: "NUM_9",
    F1: "F1",
    F2: "F2",
    F3: "F3",
    F4: "F4",
    F5: "F5",
    F6: "F6",
    F7: "F7",
    F8: "F8",
    F9: "F9",
    F10: "F10",
    F11: "F11",
    F12: "F12",
    F13: "F13",
    F14: "F14",
    F15: "F15",
    F16: "F16",
    F17: "F17",
    F18: "F18",
    F19: "F19",
    F20: "F20",
    F21: "F21",
    F22: "F22",
    F23: "F23",
    F24: "F24",
    LSHIFT: "LSHIFT",
    RSHIFT: "RSHIFT",
    LCTRL: "LCTRL",
    RCTRL: "RCTRL",
    CAPSLOCK: "CAPSLOCK",
    LMETA: "LMETA",
    RMETA: "RMETA",
    LALT: "LALT",
    RALT: "RALT",
    LWINDOWS: "LWINDOWS",
    RWINDOWS: "RWINDOWS",
    LCOMMAND: "LCOMMAND",
    RCOMMAND: "RCOMMAND",
    LOPTION: "LOPTION",
    ROPTION: "ROPTION",
    SPACE: "SPACE",
    EXCLAMATION: "EXCLAMATION",
    DOUBLEQUOTE: "DOUBLEQUOTE",
    HASH: "HASH",
    POUND: "POUND",
    DOLLAR: "DOLLAR",
    PERCENT: "PERCENT",
    AMPERSAND: "AMPERSAND",
    APOSTROPHE: "APOSTROPHE",
    PARENLEFT: "PARENLEFT",
    PARENRIGHT: "PARENRIGHT",
    ASTERISK: "ASTERISK",
    PLUS: "PLUS",
    COMMA: "COMMA",
    MINUS: "MINUS",
    PERIOD: "PERIOD",
    SLASH: "SLASH",
    _0: "_0",
    _1: "_1",
    _2: "_2",
    _3: "_3",
    _4: "_4",
    _5: "_5",
    _6: "_6",
    _7: "_7",
    _8: "_8",
    _9: "_9",
    COLON: "COLON",
    SEMICOLON: "SEMICOLON",
    LESS: "LESS",
    EQUAL: "EQUAL",
    GREATER: "GREATER",
    QUESTION: "QUESTION",
    AT: "AT",
    BRACKETLEFT: "BRACKETLEFT",
    BACKSLASH: "BACKSLASH",
    BRACKETRIGHT: "BRACKETRIGHT",
    ASCIICIRCUM: "ASCIICIRCUM",
    UNDERSCORE: "UNDERSCORE",
    GRAVE: "GRAVE",
    QUOTELEFT: "QUOTELEFT",
    A: "A",
    B: "B",
    C: "C",
    D: "D",
    E: "E",
    F: "F",
    G: "G",
    H: "H",
    I: "I",
    J: "J",
    K: "K",
    L: "L",
    M: "M",
    N: "N",
    O: "O",
    P: "P",
    Q: "Q",
    R: "R",
    S: "S",
    T: "T",
    U: "U",
    V: "V",
    W: "W",
    X: "X",
    Y: "Y",
    Z: "Z",
    BRACELEFT: "BRACELEFT",
    BAR: "BAR",
    BRACERIGHT: "BRACERIGHT",
    ASCIITILDE: "ASCIITILDE",
}

