__author__ = 'meatpuppet'

import argparse, logging
import os
import git
import blessings
import whoosh.index as windex
import magic
import codecs
from pygments.lexers import guess_lexer
from pygments import highlight
from pygments.formatters import TerminalFormatter
import pyperclip


term = blessings.Terminal()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

repos_folder = os.path.abspath('repos')

data_folder = os.path.abspath('data')

exclude_dirs = ['.git']
exclude_files = []

from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.analysis import StemmingAnalyzer
from whoosh.qparser import QueryParser
from whoosh.index import EmptyIndexError

schema = Schema(path=ID(stored=True, unique=True), type=TEXT(stored=True), body=TEXT(stored=True), time=STORED)

# todo: incremental indexing https://whoosh.readthedocs.org/en/latest/indexing.html


def search(*args):
    """search for a term"""
    indexdir = data_folder
    try:
        ix = windex.open_dir(indexdir)
    except EmptyIndexError as e:
        print('No Index found! Clone some repos or run index!')
        exit(0)
    with ix.searcher() as searcher:
        query = QueryParser("body", schema).parse(' '.join(args))
        results = searcher.search(query)
        for result in results:
            #print(result)
            print('{:<30}'.format(term.bold("[" + result['type'] + "]")) + result['path'].split(repos_folder)[1])


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


def show(args):
    with open(args.file, 'r') as f:
        lines = '\n'.join(f.readlines())

    lexer = guess_lexer(lines)
    formatter = TerminalFormatter()
    result = highlight(lines, lexer, formatter)
    print(result)

    if args.copy:
        pyperclip.copy(lines)
        print('copied to clipboard')
    pass

def add(args):
    print('this adds a repo some time in the future..')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='cmd')

    search_parser = subparsers.add_parser('search', aliases=['s'], help='search snippets')
    search_parser.add_argument('term')
    search_parser.set_defaults(func=search)

    index_parser = subparsers.add_parser('index', help='')
    index_parser.set_defaults(func=index)

    pull_parser = subparsers.add_parser('pull', help='')
    pull_parser.set_defaults(func=pull)

    show_parser = subparsers.add_parser('show', help='')
    show_parser.add_argument('file')
    show_parser.add_argument('-c', '--copy', action='store_true', help='copy to clipboard (#TODO)')
    show_parser.set_defaults(func=show)

    args = parser.parse_args()
    args.func(args)


