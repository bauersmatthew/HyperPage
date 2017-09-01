import os.path

reg = {}

def reset():
    """Reset the registry and the UID system."""
    global reg, last_uid
    reg = {}
    last_uid = ''

def add_link(addr):
    """Add a link to the link registry.
    
    Addr is the address string (href=addr).
    Returns a UID string (follow hint) for the link."""
    global reg
    # search for if this destination has been linked before
    for uid in reg:
        if reg[uid] == addr:
            return uid
    # not linked before
    uid = gen_uid()
    reg[uid] = addr
    return uid

def get_addr(uid):
    """Get the address associated with a given UID."""
    global reg
    if uid in reg:
        return reg[uid]
    else:
        return None

last_uid = ''
def gen_uid():
    """Generate a new UID."""
    global last_uid
    if last_uid == '':
        last_uid = 'A'
    else:
        tick = last_uid[-1]
        if tick != 'Z':
            last_uid = last_uid[:-1] + chr(ord(tick)+1)
        else:
            last_uid = last_uid + 'A'
    return last_uid

symlink_dests = {}
# dictionary of "fake" addresses; e.g. "file" --> "/dir/path/file.txt.v1"
def resolve_addr(addr):
    global symlink_dests
    if addr in symlink_dests:
        addr = symlink_dests[addr]

    if os.path.isfile(addr):
        return addr
    else:
        return None
