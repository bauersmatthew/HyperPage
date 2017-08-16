"""An interface for generic markdown parsing."""
from collections import namedtuple
from enum import Enum

class Attr(Enum):
    """An inline text attribute."""
    NORMAL, LINK, EMPH1, EMPH2, CODE = range(5)

# A snippet of text.
# 'text' is a string for all attributes except LINK, where it is a tuple of two
# strings.
Snippet = namedtuple('Snippet', ('attr', 'text'))

class BlockType(Enum):
    """A blocked text type."""
    PAR, QUOTE, CODE, \
        H1, H2, H3, H4, H5, H6, \
        ULIST, OLIST, LISTITEM, \
        TABLE, TABLECOL, TABLEROW \
        = range(15)

# A block of text.
# Contents is...
# PAR: A tuple of snippets.
# QUOTE: A tuple of blocks.
# CODE: A tuple of strings (lines).
# H*: A tuple of snippets.
# *LIST: A tuple of LISTITEMs
# LISTITEM: A tuple of blocks.
# TABLE: A tuple of TABLECOLs
# TABLECOL: A tuple of TABLEROWs
# TABLEROW: A tuple of snippets and statics.
Block = namedtuple('Block', ('type', 'contents'))

class StaticType(Enum):
    """A static element type."""
    HRULE, = range(1)

# A static element.
Static = namedtuple('Static', 'type')

def parse(text):
    """Parse markdown text.

    Returns a tuple of blocks and statics."""
    pass # TODO
