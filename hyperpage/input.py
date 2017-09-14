import copy
import sys
import os.path
from curtsies import Input
from hyperpage import display
from hyperpage import markdown
from hyperpage import document

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
        document.current().scroll_top()
        return
    elif k == 'G':
        document.current().scroll_bot()
        return
    document.current().scroll_delta(dyoff)

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
            addr = document.current().links[self.growing_chain]
            if addr is not None:
                path = addr if os.path.isfile(addr) else None
                if path is not None:
                    document.load(path)
            self.__exit__(None, None, None)
        else:
            # chain continues
            pass
link_handler = LinkHandler()

def hdl_back(_):
    document.go_back()

hdl_reg = {}
def reg(keys, hdl):
    global hdl_reg
    for key in keys:
        hdl_reg[key] = hdl
reg(('q', 'Q'), hdl_exit)
reg(('j', 'k', 'J', 'K', 'g', 'G'), hdl_scroll)
reg(('f',), link_handler.__enter__)
reg(('H',), hdl_back)
    
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
