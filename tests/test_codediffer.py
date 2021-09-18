import pytest
from ploomber.codediffer import (CodeDiffer, normalize_python,
                                 _delete_python_comments)

fn_w_docsting = '''
def x():
    """This is some docstring
    """
    pass
'''

fn_w_docsting_v2 = '''
def x():
    """This is a docstring and should be ignored
    """
    pass
'''


def test_python_differ_ignores_docstrings():

    differ = CodeDiffer()
    res, _ = differ.is_different(a=fn_w_docsting,
                                 b=fn_w_docsting_v2,
                                 a_source_tree={},
                                 b_source_tree={},
                                 a_params={},
                                 b_params={},
                                 extension='py')
    assert not res


def test_python_differ_ignores_comments():

    a = '''
def x():
    # this is a comment
    # another comment
    var = 100
'''

    b = '''
def x():
    # one comment
    var = 100 # this is a comment
'''

    differ = CodeDiffer()
    res, _ = differ.is_different(a=a,
                                 b=b,
                                 a_source_tree={},
                                 b_source_tree={},
                                 a_params={},
                                 b_params={},
                                 extension='py')
    assert not res


def test_sql_is_normalized():
    a = """
    SELECT * FROM TABLE
    """

    b = """
    SELECT *
    FROM table
    """
    differ = CodeDiffer()
    different, _ = differ.is_different(a=a,
                                       b=b,
                                       a_source_tree={},
                                       b_source_tree={},
                                       a_params={},
                                       b_params={},
                                       extension='sql')
    assert not different


@pytest.mark.parametrize('extension', ['py', 'sql', None])
def test_get_diff(extension):
    differ = CodeDiffer()
    a = 'some code...'
    b = 'some other code...'
    differ.get_diff(a=a, b=b, extension=extension)


fn = '''
def x():
    """docstring
    """
    pass
'''

fn_no_doc = """
def x():
    pass
"""

fn_decorated = '''
@decorator
def x():
    """docstring
    """
    pass
'''

fn_decorated_no_doc = """
@decorator
def x():
    pass
"""

fn_double_decorated = '''
@decorator
@another
def x():
    """Some docstring
    """
    pass
'''

fn_double_decorated_no_doc = """
@decorator
@another
def x():
    pass
"""


@pytest.mark.parametrize(
    'code, expected',
    [
        [fn, fn_no_doc],
        [fn_no_doc, fn_no_doc],
        [fn_decorated, fn_decorated_no_doc],
        [fn_decorated_no_doc, fn_decorated_no_doc],
        [fn_double_decorated, fn_double_decorated_no_doc],
        [fn_double_decorated_no_doc, fn_double_decorated_no_doc],
    ],
)
def test_normalize_python(code, expected):
    assert normalize_python(code) == expected


def test_different_params():
    differ = CodeDiffer()
    res, _ = differ.is_different(a='some code',
                                 b='some code',
                                 a_source_tree={},
                                 b_source_tree={},
                                 a_params={'a': 1},
                                 b_params={'a': 2},
                                 extension='py')
    assert res


def test_different_source_tree():
    differ = CodeDiffer()
    res, _ = differ.is_different(a='some code',
                                 b='some code',
                                 a_source_tree={'z': 'code'},
                                 b_source_tree={'z': 'another code'},
                                 a_params={'a': 1},
                                 b_params={'a': 1},
                                 extension='py')
    assert res


def test_normalizes_source_tree():
    a_code = '''
def x():
    """
    """
    pass
'''

    b_code = '''
def x():
    """another
    """
    pass
'''

    differ = CodeDiffer()
    res, _ = differ.is_different(a='some code',
                                 b='some code',
                                 a_source_tree={'mod.fn': a_code},
                                 b_source_tree={'mod.fn': b_code},
                                 a_params={'a': 1},
                                 b_params={'a': 1},
                                 extension='py')
    assert not res


def test_delete_python_comments():
    code = """\
# a comment
function.something()\
"""
    assert _delete_python_comments(code) == '           \nfunction.something()'
