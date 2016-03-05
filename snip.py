#!/usr/bin/python3
__author__ = 'meatpuppet'

import logging
from argh import ArghParser
from snip import terminal
from argh.completion import autocomplete

# todo: incremental indexing https://whoosh.readthedocs.org/en/latest/indexing.html


def web():
    from snip.web import web
    import webbrowser
    webbrowser.open('http://localhost:5000')
    web.app.run()


if __name__ == "__main__":
    parser = ArghParser()
    parser.add_commands([terminal.pull, terminal.show, terminal.search, terminal.index, web])
    autocomplete(parser)
    parser.dispatch()



