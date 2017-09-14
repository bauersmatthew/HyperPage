from setuptools import setup, find_packages

setup(
    name="HyperPage",
    version="0.1.0",
    packages=['hyperpage'],
    install_requires=['curtsies>=0.2.10', 'mistune>=0.7.2'],
    entry_points={
        'console_scripts' : ['hpage = hyperpage.run:main']},

    author='Matthew Bauer',
    author_email='bauer.s.matthew@gmail.com',
    description='A hypertext-enabled TUI-based markdown pager.',
    keywords='markdown pager tui hypertext',
    url='https://github.com/bauersmatthew/HyperPage'
)
