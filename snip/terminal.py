__author__ = 'meatpuppet'

from argh.decorators import aliases, arg

import blessings
import whoosh.highlight as whighlight
from pygments.lexers import guess_lexer
from pygments import highlight
from pygments.formatters import TerminalFormatter
import pyperclip


from . import _index, _get_repos, _pull, schema, QueryParser, ContextFragmenter, EmptyIndexError, data_folder, windex

term = blessings.Terminal()



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
        results.formatter = TermFormatter()
        #hi = whighlight.Highlighter(fragmenter=PinpointFragmenter)
        results.fragmenter = ContextFragmenter()
        for result in results:
            print('{0:-<40}'.format(term.bold(result['path'])))
            print(term.bold("[" + result['type'] + "]") + '--preview:')
            print(result.highlights('body'))
            print('\n')


def index():
    """re-index all repos"""
    _index()


def pull():
    """pull all repos """
    for repo in _get_repos():
        (msg, error) = _pull(repo)
        if not error:
            style = term.bold
        else:
            style = term.bold_red
        print('%s [%s]' % (style('pulling %s:' % repo), msg))

    print("re-indexing...")
    index()


@arg('file')
@arg('-c', '--copy', default=False)
def show(file, copy='copy'):
    """show and highlight file"""
    with open(file, 'r') as f:
        lines = ''.join(f.readlines())

    lexer = guess_lexer(lines)
    formatter = TerminalFormatter()
    result = highlight(lines, lexer, formatter)
    print(result)

    if copy:
        pyperclip.copy(lines)
        print(term.bold('[copied to clipboard]'))
    pass