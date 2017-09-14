"""Implement Document class and current document interface."""
from hyperpage import elements
from hyperpage import markdown
from hyperpage import display

class LinkRegistry:
    """A registry of links in a document."""
    def __init__(self):
        """Initialize an empty registry."""
        self.reg = {}
        self.last_uid = ''

    def add(self, addr):
        """Add a link.

        Addr is the address string (href=addr).
        Returns a UID string (follow hint) for the link."""
        # search for if this addr has been linked before
        for uid in self.reg:
            if self.reg[uid] == addr:
                return uid
        # not linked before
        uid = self.gen_uid()
        self.reg[uid] = addr
        return uid

    def gen_uid(self):
        """Generate a new UID."""
        if self.last_uid == '':
            self.last_uid = 'A'
        else:
            tick = self.last_uid[-1]
            if tick != 'Z':
                self.last_uid = self.last_uid[:-1] + chr(ord(tick)+1)
            else:
                self.last_uid = self.last_uid + 'A'
        return self.last_uid

    def __getitem__(self, uid):
        """Get the address associated with the given UID."""
        if uid in self.reg:
            return self.reg[uid]
        return None

class Document:
    """Document generalization."""
    def __init__(self):
        """Initialize a totally empty document."""
        self.links = LinkRegistry()

    def hold(self, doc):
        """Attaches this document to a DocHead."""
        self.doc = doc
        self.scroll = 0
        self.old_w, self.old_h = display.get_dims()
        self.mtx = self.doc.draw(self.old_w)
        self.draw()

    def draw(self):
        """Draw to screen."""
        w, h = display.get_dims()
        if w != self.old_w:
            # re-render matrix
            self.mtx = self.doc.draw(w)

            # recalculate the scroll value
            self.scroll = self.old_w*self.scroll//w
            self.fix_scroll()

        # draw visible region to screen
        ybegin = self.scroll
        yend = self.scroll + h
        if yend > self.mtx.get_h():
            yend = self.mtx.get_h()
        visible_mtx = self.mtx.y_slice(ybegin, yend)
        display.put(visible_mtx)

        self.old_w = w
        self.old_h = h

    def fix_scroll(self):
        """Check if the scroll is valid; if not, fix it."""
        max_yoff = self.mtx.get_h() - self.old_h
        if self.scroll > max_yoff:
            self.scroll = max_yoff
        elif self.scroll < 0:
            self.scroll = 0
    def scroll_delta(self, delta):
        """Scroll relative to current position."""
        self.scroll += delta
        self.fix_scroll()
    def scroll_top(self):
        """Scroll to the top of the document."""
        self.scroll = 0
    def scroll_bot(self):
        """Scroll to the bottom of the document."""
        self.scroll = self.mtx.get_h() - self.old_h

doc_stack = []
def current():
    """Return the current document."""
    if doc_stack:
        return doc_stack[-1]
    return None

def load_text(text):
    """Load document from markdown text."""
    global doc_stack
    # the Document() must exist BEFORE the DocHead!
    doc_stack.append(Document())
    current().hold(elements.DocHead(markdown.parse(text)))

def load(path):
    """Load document from file."""
    with open(path) as fin:
        load_text(fin.read())

def go_back():
    """Go back one document."""
    global doc_stack
    if len(doc_stack) > 1:
        del doc_stack[-1]
        doc_stack[-1].draw()
