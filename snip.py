#!/usr/bin/python3
__author__ = 'meatpuppet'

import logging
from argh import ArghParser
from argh.decorators import aliases, arg
from argh.completion import autocomplete
import os
import git
import blessings
import whoosh.index as windex
import whoosh.highlight as whighlight
from whoosh.highlight import ContextFragmenter
import magic
import codecs
from pygments.lexers import guess_lexer
from pygments import highlight
from pygments.formatters import TerminalFormatter
import pyperclip


term = blessings.Terminal()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

skript_path = os.path.dirname(os.path.realpath(__file__))

repos_folder = os.path.join(skript_path, 'repos')

data_folder = os.path.join(skript_path, 'data')

exclude_dirs = ['.git']
exclude_files = []

from whoosh.fields import Schema, TEXT, ID, STORED, NUMERIC
from whoosh.qparser import QueryParser
from whoosh.index import EmptyIndexError

schema = Schema(path=ID(stored=True, unique=True), type=TEXT(stored=True), body=TEXT(stored=True, chars=True), time=STORED)

# todo: incremental indexing https://whoosh.readthedocs.org/en/latest/indexing.html

class TermFormatter(whighlight.Formatter):
    def format_token(self, text, token, replace=False):
        # Use the get_text function to get the text corresponding to the
        # token
        tokentext = whighlight.get_text(text, token, replace)
        return term.bold(tokentext)

@arg('terms', nargs='+')
@aliases('s')
def search(terms):
    """search for a term"""
    indexdir = data_folder
    try:
        ix = windex.open_dir(indexdir)
    except EmptyIndexError as e:
        print('No Index found! Clone some repos or run index!')
        exit(0)
    with ix.searcher() as searcher:
        query = QueryParser("body", schema).parse(' '.join(terms))
        results = searcher.search(query, terms=True)
        termformat = TermFormatter()
        results.formatter = termformat

        #hi = whighlight.Highlighter(fragmenter=PinpointFragmenter)
        results.fragmenter = ContextFragmenter()

        for result in results:
            print('{0:-<40}'.format(term.bold(result['path'])))
            print(term.bold("[" + result['type'] + "]") + '--preview:')

            print(result.highlights('body'))
            print('\n')


def index():
    """re-index all repos"""
    indexdir = data_folder
    ix = windex.create_in(indexdir, schema=schema)
    writer = ix.writer()

    for root, dirs, files in os.walk(repos_folder, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        #for dir in dirs:
        #    if '.git' not in os.path.split(root):
        #        print(os.path.join(root, dir))
        files[:] = [f for f in files if f not in exclude_files]
        for file in files:
            #writer.update_document(
            #    print(os.path.join(root, file))
            mimetype_split = magic.from_file(os.path.join(root, file), mime=True).decode().split('/', maxsplit=1)
            #print(mimetype_split[0])
            if mimetype_split[0] == 'text':
                #print('indexing %s ' % os.path.join(root, file))
                with codecs.open(os.path.join(root, file), "r", errors='surrogateescape') as raw:
                    try:
                        content = raw.read()
                        writer.add_document(path=os.path.join(root, file), type=mimetype_split[1], body=content)
                    except Exception as e:
                        logger.error('cant index %s: %s' % (os.path.join(root, file), e))
    writer.commit(optimize=True)


def pull():
    """pull all repos """
    for folder in next(os.walk(repos_folder))[1]:
        g = git.cmd.Git(os.path.join(repos_folder, folder))
        try:
            msg = g.pull()
            style = term.bold
        except Exception as e:
            msg = e
            style = term.bold_red
        print('%s [%s]' % (style('pulling %s:' % folder), msg))

    print("re-indexing...")
    index()

@arg('file')
@arg('-c', '--copy', default=False)
def show(file, copy='copy'):
    """show and highlight file"""
    with open(os.path.join(repos_folder, file), 'r') as f:
        lines = '\n'.join(f.readlines())

    lexer = guess_lexer(lines)
    formatter = TerminalFormatter()
    result = highlight(lines, lexer, formatter)
    print(result)

    if copy:
        pyperclip.copy(lines)
        print(term.bold('[copied to clipboard]'))
    pass


if __name__ == "__main__":
    parser = ArghParser()
    parser.add_commands([pull, show, search, index])
    autocomplete(parser)
    parser.dispatch()



