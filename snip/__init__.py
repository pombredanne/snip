__author__ = 'meatpuppet'

from whoosh.fields import Schema, TEXT, ID, STORED, NUMERIC
import logging
import os
import whoosh.index as windex
from whoosh.highlight import ContextFragmenter

from whoosh.qparser import QueryParser
from whoosh.index import EmptyIndexError

import codecs
import magic
import git

schema = Schema(path=ID(stored=True, unique=True), type=TEXT(stored=True), body=TEXT(stored=True, chars=True), time=STORED)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

skript_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)

repos_folder = os.path.join(skript_path, 'repos')

data_folder = os.path.join(skript_path, 'data')


exclude_dirs = ['.git']
exclude_files = []

def _index():
    """
    todo: this currently only indexes the repos folder, should index per path in the future (so that we can add repos anywhere in the filesystem)
    :return:
    """
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


def _get_repos():
    repos = []
    for folder in next(os.walk(repos_folder))[1]:
        repos.append(os.path.join(repos_folder, folder))
    return repos


def _pull(repo):
    g = git.cmd.Git(repo)
    try:
        msg = g.pull()
        error = False
    except Exception as e:
        msg = e
        error = True
    return (msg, error)

from . import terminal
