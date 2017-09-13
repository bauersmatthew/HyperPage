from curtsies import Input
import copy
import sys
from hyperpage import links
from hyperpage import display
from hyperpage import markdown

class ExitException(Exception):
    pass
def hdl_exit(_):
    raise ExitException()

def hdl_scroll(k):
    dyoff = None
    if k == 'j':
        dyoff = 1
    elif k == 'J':
        dyoff = 5
    elif k == 'k':
        dyoff = -1
    elif k == 'K':
        dyoff = -5
    elif k == 'g':
        display.scroll_top()
        return
    elif k == 'G':
        display.scroll_bottom()
        return
    display.scroll_delta(dyoff)

class LinkHandler:
    class FakeReg:
        def __init__(self, lhdl):
            self.link_handler = lhdl
        def __contains__(self, _):
            return True
        def __getitem__(self, _):
            return self.link_handler.handle
    def __enter__(self, *args):
        global hdl_reg
        self.backup_reg = copy.copy(hdl_reg)
        hdl_reg = self.FakeReg(self)
        self.growing_chain = ''
        return self
    def __exit__(self, a, b, c):
        global hdl_reg
        hdl_reg = self.backup_reg
        return True
    def handle(self, k):
        k = k.upper()
        self.growing_chain += k
        if k != 'Z':
            # end of the chain
            addr = links.get_addr(self.growing_chain)
            if addr is not None:
                path = links.resolve_addr(addr)
                if path is not None:
                    links.reset()
                    display.hold(markdown.load(path))
            self.__exit__(None, None, None)
        else:
            # chain continues
            pass
link_handler = LinkHandler()

hdl_reg = {}
def reg(keys, hdl):
    global hdl_reg
    for key in keys:
        hdl_reg[key] = hdl
reg(('q', 'Q'), hdl_exit)
reg(('j', 'k', 'J', 'K', 'g', 'G'), hdl_scroll)
reg(('f',), link_handler.__enter__)
    
inp_gen = None
def init():
    global inp_gen
    inp_gen = Input().__enter__()

def exit():
    global inp_gen
    inp_gen.__exit__(None, None, None)

def handle(inp):
    if inp is None:
        return
    global hdl_reg
    if inp in hdl_reg:
        hdl_reg[inp](inp)

def handle_next():
    inp = inp_gen.next()
    handle(inp)
