__author__ = 'meatpuppet'

import argparse, logging
import os
import git
import blessings
import whoosh.index as windex
import magic
import codecs
import argh

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

schema = Schema(path=ID(stored=True, unique=True), type=TEXT(stored=True), body=TEXT(stored=True), time=STORED)

# todo: incremental indexing https://whoosh.readthedocs.org/en/latest/indexing.html


def search(*args):
    """search for a term"""
    indexdir = data_folder
    ix = windex.open_dir(indexdir)
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


if __name__ == "__main__":
    parser = argh.ArghParser()
    parser.add_commands([pull, index, search])

    parser.dispatch()
