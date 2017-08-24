"""Module to handle TUI display.

Does not handle input!"""

from curtsies import FullscreenWindow, fsarray
import curtsies.fmtfuncs as fmt

default_style = {
    'em' : fmt.underline,
    'strong' : fmt.bold,
    'code' : fmt.blue,
    'h1' : lambda x: fmt.bold(fmt.red(x)),
    'h2' : lambda x: fmt.bold(fmt.blue(x)),
    'h3' : lambda x: fmt.bold(fmt.green(x))
}

class Display(FullscreenWindow):
    def put(self, mtx):
        """Write a Matrix to the screen.
        
        Requirements: mtx width <= disp width, mtx height <= disp height"""
        if mtx.get_h() > self.height or mtx.get_w() > self.width:
            raise RuntimeError('Malsized matrix!')
        render = render_mtx(mtx, default_style)
        self.render_to_terminal(render)


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
