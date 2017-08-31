import elements
import markdown
import display
from time import sleep
import sys
from curtsies import Input
import input

readme = None
with open(sys.argv[1]) as fin:
    readme = fin.read()

html_tree = markdown.parse(readme)
doc = elements.DocHead(html_tree)

try:
    display.init()
    input.init()

    display.hold(doc)

    while True:
        input.handle_next()
except input.ExitException:
    sys.exit(0)
except:
    raise
finally:
    display.exit()
    input.exit()
