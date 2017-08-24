"""Describes display elements, which closely match HTML elements used in
markdown.

Each element class must have:
 - a constructor accepting an html tree (as described in markdown.py)
 - a draw() function taking a width argument and returning a Matrix of RichChars

"""
import copy
from collections import namedtuple
import regex as re
from math import ceil

RichChar = namedtuple('RichChar', ('char', 'attrs'))

class Matrix(dict):
    """A 0,0-based matrix of unicode characters."""
    def __init__(self, width, height=0):
        """Initialize a matrix with given width and optional height."""
        self.width = width
        for _ in range(height):
            self.add_row()

    def get_w(self):
        """Get matrix width."""
        return self.width
    def get_h(self):
        """Get matrix height."""
        return len(self)/self.get_w()

    def add_row(self, contents=None):
        """Add one row to the end of the matrix."""
        height = self.get_h()
        for x in range(self.get_w()):
            self[x, height] = None
        if contents:
            for x, cell in enumerate(contents):
                self[x, height] = cell

    def del_row(self):
        """Remove one row from the end of the matrix."""
        height = self.get_h()
        for x in range(self.get_w()):
            del self[x, height]

    def __add__(self, other):
        """Append one matrix to the end of the other."""
        if self.get_w() != other.get_w():
            raise RuntimeError('Cannot combine matrices of different widths!')
        new_mtx = copy.copy(self)
        start_h = new_mtx.get_h()
        for y in range(other.get_h()):
            for x in range(other.get_w()):
                new_mtx[x, start_h+y] = other[x, y]
        return new_mtx
    def append(self, other):
        """Append one matrix to the end of the other."""
        return self + other

    def paste(self, other, x, y):
        """Paste smaller matrix at the given x, y position in this one."""
        if (other.get_w()+x > self.get_w() or
            other.get_h()+y > self.get_h()):
            raise RuntimeError('Cannot paste matrix (invalid sizes)!')
        for yi in range(other.get_h()):
            for xi in range(other.get_w()):
                self[x+xi, y+yi] = other[xi, yi]

tag_table = {}

class DocHead:
    """The document head. Contains all other elements."""
    def __init__(self, tree):
        self.subs = []
        for branch in tree.data:
            if branch.__class__.__name__ == 'HTMLData':
                raise RuntimeError('Unenclosed data not allowed at top level!')
            else:
                if branch.tag not in tag_table:
                    raise RuntimeError('Unknown tag: {} !'.format(branch.tag))
                self.subs.append(tag_table[branch.tag](branch))

    def draw(self, width):
        """Draw each sub-element with a blank line between them."""
        mtx = Matrix(width)
        for sub in self.subs:
            mtx += sub.draw(width)
            mtx.add_row()
        return mtx

def parse_rich_chars(tree, attr_stack=[],
                     replace_newlines=True):
    chars = []
    for branch in tree.data:
        if branch.__class__.__name__ == 'HTMLData':
            for ch in branch.data:
                if replace_newlines and ch == '\n':
                    ch = ' '
                chars.append(RichChar(ch, copy.copy(attr_stack)))
        else:
            attr_stack.append(branch.tag)
            chars += parse_rich_chars(
                branch, copy.copy(attr_stack), replace_newlines)
    return chars

class Par:
    """<p>...</p>"""
    def __init__(self, tree):
        self.text = parse_rich_chars(tree)
    def draw(self, width):
        """Wraps text very roughly."""
        mtx = Matrix(width)
        offset = 0
        while offset < len(self.text):
            mtx.add_row(self.text[offset:offset+width])
            offset += width
        return mtx

def Header(num):
    """Create a header (Hx) class."""
    class Hx(Par):
        def __init__(self, tree):
            self.text = parse_rich_chars(tree, attr_stack=['h{}'.format(num)])
    Hx.__doc__ = '<h{0}>...</h{0}>'.format(num)
    Hx.__name__ = 'h{}'.format(num)
    return Hx
H1, H2, H3, H4, H5, H6 = (Header(n) for n in range(1, 7))

class CodeBlock:
    """<pre><code>...</code></pre>"""
    def __init__(self, tree):
        text = parse_rich_chars(tree, replace_newlines=False)
        self.lines = []
        curr_start = 0
        for here, rch in enumerate(text):
            if rch.char == '\n':
                self.lines.append(text[curr_start:here])
                curr_start = here+1
        self.lines.append(text[curr_start:])
    def draw(self, width):
        """Wraps text very roughly."""
        mtx = Matrix(width)
        for line in self.lines:
            offset = 0
            while offset < len(line):
                mtx.add_row(line[offset:offset+width])
                offset += width
        return mtx

class HRule:
    """<hr />"""
    def __init__(self, tree):
        pass
    def draw(self, width):
        mtx = Matrix(width)
        mtx.add_row([RichChar('-', ['hr'])]*width)
