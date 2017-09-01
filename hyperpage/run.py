import elements
import markdown
import display
import input
import settings
import sys

readme = None
with open(sys.argv[1]) as fin:
    readme = fin.read()

html_tree = markdown.parse(readme)
doc = elements.DocHead(html_tree)

try:
    display.init()
    input.init()
    settings.init(sys.argv[2])

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
