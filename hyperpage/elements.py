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
import links

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
        return len(self)//self.get_w()

    def add_row(self, contents=None):
        """Add one row to the end of the matrix."""
        height = self.get_h()
        for x in range(self.get_w()):
            self[x, height] = None
        if contents:
            for x, cell in enumerate(contents):
                self[x, height] = cell
    def add_rows(self, num):
        for _ in range(num):
            self.add_row()

    def del_row(self):
        """Remove one row from the end of the matrix."""
        height = self.get_h()-1
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

    def subset(self, x0, y0, x1, y1):
        """Get a sub-matrix with the given coords.

        x0 and y0 are inclusive; x1 and y1 are exclusive."""
        if x1 < x0 or y1 < y0 or x0 < 0 or x1 > self.get_w() or \
           y0 < 0 or y1 > self.get_h():
            raise RuntimeError('Invalid subset coordinates.')
        new = Matrix(x1-x0)
        for y in range(y1-y0):
            new.add_row()
            for x in range(x1-x0):
                new[x, y] = self[x0+x, y0+y]
        return new

    def y_slice(self, y0, y1):
        return self.subset(0, y0, self.get_w(), y1)

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
            astack_copy = copy.copy(attr_stack)
            astack_copy.append(branch.tag)
            chars += parse_rich_chars(
                branch, astack_copy, replace_newlines)
            if branch.tag == 'a':
                # is a link; add to link table
                link_uid = links.add_link(branch.attrs['href'])
                hint_stack = copy.copy(astack_copy)+['hint']
                chars.append(RichChar(' ', astack_copy))
                chars.append(RichChar('[', hint_stack))
                for ch in link_uid:
                    chars.append(RichChar(ch, hint_stack))
                chars.append(RichChar(']', hint_stack))
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
        mtx.add_row([RichChar('━', ['hr'])]*width)
        return mtx

class BlockQuote(DocHead):
    """<blockquote>...</blockquote>"""
    def draw(self, width):
        content = super().draw(width-1)
        mtx = Matrix(width, content.get_h())
        # add bar on the side
        for y in range(mtx.get_h()):
            mtx[0, y] = RichChar('┃', ['bq'])
        # paste in content
        mtx.paste(content, 1, 0)
        return mtx

class List:
    """List base; <ol> or <ul>"""
    def __init__(self, tree):
        self.items = []
        self.tag = tree.tag
        # extract each item as a paragraph
        for branch in tree.data:
            if branch.tag != 'li':
                raise RuntimeError('list must only contain li elements!')
            self.items.append(Par(branch))
    def draw(self, width):
        labels = list(self.get_labels())
        # find string length of largest label
        req_len = max([len(lbl) for lbl in labels])
        par_wid = width-req_len
        mtx = Matrix(width)
        # add each item
        for num, item in enumerate(self.items):
            par_content = item.draw(par_wid)
            paste_y = mtx.get_h()
            mtx.add_rows(par_content.get_h()+1)
            # add labeling
            for x, c in enumerate(labels[num]):
                mtx[x, paste_y] = RichChar(c, [self.tag])
            # add content
            mtx.paste(par_content, req_len, paste_y)
            mtx.del_row() # remove spacing lines added by Par
        return mtx
    def get_labels(self):
        """Overridable. Return a list of labels to be used."""
        yield from ['']*len(self.items)

class OList(List):
    """<ol>...</ol>"""
    def get_labels(self):
        # get str len of largest number
        num_len = len(str(len(self.items)))
        # compose list
        for n in range(len(self.items)):
            yield '{{:>{}}}. '.format(num_len).format(n+1)

class UList(List):
    """<ul>...</ul>"""
    def get_labels(self):
        yield from ['• ']*len(self.items)

tag_table = {
    'p' : Par,
    'h1' : H1,
    'h2' : H2,
    'h3' : H3,
    'h4' : H4,
    'h5' : H5,
    'h6' : H6,
    'pre' : CodeBlock,
    'hr' : HRule,
    'blockquote' : BlockQuote,
    'ol' : OList,
    'ul' : UList
    }
