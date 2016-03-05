__author__ = 'meatpuppet'

from flask import render_template, redirect, abort, url_for, request, session, jsonify
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer, PythonLexer
from flask_bootstrap import Bootstrap

import os
import blessings

from flask import Flask
app = Flask(__name__)
Bootstrap(app)
app.secret_key = os.urandom(24)
from .. import _index, _get_repos, _pull, schema, QueryParser, ContextFragmenter, EmptyIndexError, data_folder, windex

from .forms import SearchForm
term = blessings.Terminal()

import whoosh.highlight as whighlight

class TermFormatter(whighlight.Formatter):
    def format_token(self, text, token, replace=False):
        # Use the get_text function to get the text corresponding to the
        # token
        tokentext = whighlight.get_text(text, token, replace)
        return term.bold(tokentext)

@app.route('/', methods=('GET', 'POST'))
def index():
    results = []
    form = SearchForm()
    if form.validate_on_submit():
        print('searching for %s' % form.search.data)
        results = search(form.search.data)
        print(results)
        pass
    return render_template('index.html', results=results, form=form)


def reindex():
    """re-index all repos"""
    _index()


def search(terms):
    """search for a term"""
    indexdir = data_folder
    try:
        ix = windex.open_dir(indexdir)
    except EmptyIndexError as e:
        print('No Index found! Clone some repos or run index!')
        exit(0)

    with ix.searcher() as searcher:
        query = QueryParser("body", schema).parse(terms)
        results = searcher.search(query, terms=True)
        #hi = whighlight.Highlighter(fragmenter=ContextFragmenter())
        results.fragmenter = ContextFragmenter()
        ret = []
        for result in results:
            print('\n'.join(result['body'].split('\\n')))
            try:
                l = guess_lexer('\n'.join(result['body'].split('\\n')))

            except:
                l = PythonLexer()
            lang = l.aliases[0]
            ret.append({
                'body': highlight(result['body'], lexer=l, formatter=HtmlFormatter()),
                'path': result['path'],
                'lang': lang
            })
        return ret



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


def show(file, copy='copy'):
    """show and highlight file"""
    with open(file, 'r') as f:
        lines = '\n'.join(f.readlines())

    lexer = guess_lexer(lines)
    formatter = TerminalFormatter()
    result = highlight(lines, lexer, formatter)
    print(result)

    if copy:
        pyperclip.copy(lines)
        print(term.bold('[copied to clipboard]'))
    pass