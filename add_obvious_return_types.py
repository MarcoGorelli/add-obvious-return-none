import argparse
import re
import sys
import ast

def process_return(node: ast.Return):
    if node is None:
        return 'None'
    elif isinstance(node, ast.Constant) and node.value is None:
        return 'None'


def process_func_def(node: ast.FunctionDef):
    if node.returns is not None:
        # already has return type, no need to add one
        return None
    returns = []
    walk = list(ast.walk(node))[1:]
    if len(node.body) == 1 and isinstance(node.body[0], ast.Raise):
        # might be an abstract method that needs overriding
        return
    if (
            len(node.body) == 2
            and isinstance(node.body[1], ast.Raise)
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)
            and isinstance(node.body[0].value.value, str)
    ):
        # might be abstract method with docstring
        return

    for _node in walk:
        if isinstance(_node, ast.FunctionDef):
            return
        if isinstance(_node, ast.Return):
            returns.append(process_return(_node.value))
    if not returns or all(i == 'None' for i in returns):
        return node
    return None

def rewrite_return_type(src, name, lineno, col_offset):
    lines = src.splitlines(keepends=True)
    before = ''.join(lines[:lineno-1])
    after = ''.join(lines[lineno-1:])
    pattern = fr'^(def\s+{name}\(.*\)\s*)(:)'
    rewrite = re.sub(pattern, '\\1 -> None:', after[col_offset:])
    src = before + after[:col_offset] + rewrite
    return src



def rewrite(src):
    tree = ast.parse(src)
    to_rewrite = []
    for _node in ast.walk(tree):
        if isinstance(_node, ast.FunctionDef):
            _to_rewrite = process_func_def(_node)
            if _to_rewrite is not None:
                to_rewrite.append(_to_rewrite)
    for node in to_rewrite:
        src = rewrite_return_type(src, node.name, node.lineno, node.col_offset)
    if to_rewrite:
        return True, src
    return False, src


def main(src, file_):
    ret, src = rewrite(src)
    if ret:
        with open(file_, 'w', encoding='utf-8') as fd:
            fd.write(src)
    return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*')
    args = parser.parse_args()
    ret = 0
    for file_ in args.files:
        with open(file_, encoding='utf-8') as fd:
            content = fd.read()
        ret |= main(content, file_)
    sys.exit(ret)

