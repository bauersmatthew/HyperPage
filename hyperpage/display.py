"""Module to handle TUI display.

Does not handle input!"""

from curtsies import FullscreenWindow, fsarray
import curtsies.fmtfuncs as fmt
from hyperpage import settings

wind = None
def init():
    """Initialize the display interface."""
    global wind, width, height
    wind = FullscreenWindow()
    wind.__enter__()

def exit():
    global wind
    wind.__exit__(None, None, None)

def get_dims():
    return wind.width, wind.height

def put(mtx):
    """Write a Matrix to the screen.
        
        Requirements: mtx width <= disp width, mtx height <= disp height"""
    global wind
    if mtx.get_h() > wind.height or mtx.get_w() > wind.width:
        raise RuntimeError('Malsized matrix!')
    render = render_mtx(mtx, settings.style_attrs)
    wind.render_to_terminal(render)

def render_mtx(mtx, style):
    """Render a Matrix of RichChar's with the given style dict."""
    lines = []
    for y in range(mtx.get_h()):
        lines.append('')
        for x in range(mtx.get_w()):
            cell = mtx[x, y]
            if cell is None:
                lines[-1] += ' '
            else:
                ch = cell.char
                for attr in cell.attrs:
                    if attr in style:
                        ch = style[attr](ch)
                lines[-1] += ch
    return fsarray(lines)
