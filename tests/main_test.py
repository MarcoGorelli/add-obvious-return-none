from add_obvious_return_types import rewrite

def test_no_return_stmt():
    src = (
        'def foo():\n'
        '    a + b\n'
    )
    expected = (
        'def foo() -> None:\n'
        '    a + b\n'
    )
    ret, result  = rewrite(src)
    assert result == expected
    assert not ret

def test_simple():
    src = (
        'def foo():\n'
        '    a + b\n'
        '    if True:\n'
        '        return\n'
        '    else:\n'
        '        return None\n'
    )
    expected = (
        'def foo() -> None:\n'
        '    a + b\n'
        '    if True:\n'
        '        return\n'
        '    else:\n'
        '        return None\n'
    )
    ret, result  = rewrite(src)
    assert result == expected
    assert ret