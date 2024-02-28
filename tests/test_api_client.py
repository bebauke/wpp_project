import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from wppproject.poetry_client.api import PoetryDB

def test_get_poems_by_author():
    pdb = PoetryDB()
    author_poems = pdb.get_poems_by_author("Shakespeare")
    assert len(author_poems) > 0
#
def test_get_poems_by_title():
    pdb = PoetryDB()
    title_poem = pdb.get_poems_by_title("Ozymandias")
    assert len(title_poem) > 0

def test_get_random_poems():
    pdb = PoetryDB()
    random_poems = pdb.get_random_poems(1)
    assert len(random_poems) > 0

def test_get_poem_lines_by_title():
    pdb = PoetryDB()
    poem_lines = pdb.get_poem_lines_by_title("Ozymandias")
    assert len(poem_lines) > 0


    