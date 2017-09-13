"""Module to handle TUI display.

Does not handle input!"""

from curtsies import FullscreenWindow, fsarray
import curtsies.fmtfuncs as fmt
from hyperpage import settings

default_style = {
    'em' : fmt.underline,
    'strong' : fmt.bold,
    'code' : fmt.blue,
    'h1' : lambda x: fmt.bold(fmt.red(x)),
    'h2' : lambda x: fmt.bold(fmt.blue(x)),
    'h3' : lambda x: fmt.bold(fmt.green(x)),
    'a': lambda x: fmt.underline(fmt.blue(x)),
    'hint' : fmt.on_red
}

wind = None
def init():
    """Initialize the display interface."""
    global wind, width, height
    wind = FullscreenWindow()
    wind.__enter__()
    width = wind.width
    height = wind.height

def exit():
    global wind
    wind.__exit__(None, None, None)

width = None
height = None

def check_dims():
    global width, height, held_mtx, held_doc, wind
    width = wind.width
    height = wind.height
    if held_mtx is None or held_mtx.get_w() != width:
        held_mtx = held_doc.draw(width)

def dim_dependent(fun):
    def f(*args, **kwargs):
        check_dims()
        fun(*args, **kwargs)
    return f

held_doc = None
held_mtx = None
def hold(doc):
    """Hold a DocHead for drawing."""
    global held_doc, held_mtx, wind, scroll_offset
    held_doc = doc
    held_mtx = None
    scroll_offset = 0
    draw()

y_scroll_offset = 0
@dim_dependent
def scroll_to(yoff):
    """Scroll to the given y-offset.
    
    Does nothing given invalid inputs."""
    global y_scroll_offset, held_mtx, wind
    max_yoff = held_mtx.get_h() - wind.height
    if max_yoff < 0:
        max_yoff = 0 
    if yoff <= max_yoff and yoff >= 0:
        y_scroll_offset = yoff
    draw()

@dim_dependent
def scroll_delta(dyoff):
    """Scroll relative to the current position.

    Negative ==> scroll up;
    Positive ==> scroll down"""
    global y_scroll_offset
    scroll_to(y_scroll_offset+dyoff)

@dim_dependent
def scroll_top():
    """Scroll to the top of the doc."""
    scroll_to(0)

@dim_dependent
def scroll_bottom():
    """Scroll to the bottom of the doc."""
    max_yoff = held_mtx.get_h() - wind.height
    if max_yoff < 0:
        max_yoff = 0
    scroll_to(max_yoff)

@dim_dependent
def draw():
    """Draw the current held matrix to the screen.

    Takes into account scrolling."""
    # slice the matrix
    global held_mtx, y_scroll_offset, wind
    end_y = y_scroll_offset+wind.height
    if end_y > held_mtx.get_h():
        end_y = held_mtx.get_h()
    put(held_mtx.y_slice(y_scroll_offset, end_y))

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
