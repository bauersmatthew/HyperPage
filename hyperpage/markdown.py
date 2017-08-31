"""An interface for generic markdown parsing."""
from mistune import markdown
from html.parser import HTMLParser
from html import unescape
from collections import namedtuple
import elements

HTMLDataNT = namedtuple('HTMLData', ('data',))
HTMLData = lambda d: HTMLDataNT(unescape(d))
HTMLNode = namedtuple('HTMLNode', ('tag', 'attrs', 'data'))
# Object model: tree of HTMLNodes with each branch ending at a HTMLData.

class HTMLTreeLoader(HTMLParser):
    """Parser that fills an HTML tree."""
    def __init__(self, root):
        """Initialize the parser with a root node to grow."""
        super().__init__()
        self.stack = [root]
    def handle_starttag(self, tag, attrs):
        new_node = HTMLNode(tag, dict(attrs), [])
        self.stack[-1].data.append(new_node)
        self.stack.append(new_node)
    def handle_data(self, data):
        if data.strip():
            self.stack[-1].data.append(HTMLData(data))
    def handle_endtag(self, tag):
        del self.stack[-1]

def parse(text):
    """Parse markdown text.

    Returns a tuple of blocks and statics."""
    html_raw = markdown(text, use_xhtml=True)
    html = HTMLNode('html', {}, [])
    html_parser = HTMLTreeLoader(html)
    html_parser.feed(html_raw)
    return html

def load(path):
    """Load a markdown file from a path."""
    with open(path) as fin:
        return elements.DocHead(parse(fin.read()))
