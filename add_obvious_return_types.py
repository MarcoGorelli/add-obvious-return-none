import argparse
import re
import sys
import ast
from tokenize_rt import tokens_to_src, src_to_tokens


def _find_start_token(tokens, lineno, col_offset):
    iter_tokens = iter(tokens)
    for token in iter_tokens:
        if token.line == lineno and token.utf8_byte_offset == col_offset:
            break
    else:
        pass
    return list(iter_tokens)


def _find_closing_paren(tokens):
    iter_tokens = iter(tokens)
    for token in iter_tokens:
        if token.name == 'OP' and token.src == '(':
            break
    else:
        pass
    stack = 1
    for token in iter_tokens:
        if token.name == 'OP' and token.src == '(':
            stack += 1
        elif token.name == 'OP' and token.src == ')':
            stack -= 1
        if stack == 0:
            return token.line, token.utf8_byte_offset
    else:
        pass

def process_return(node: ast.Return):
    if node is None:
        return 'None'
    elif isinstance(node, ast.Constant) and node.value is None:
        return 'None'

def might_be_abstract_method(node, decorator_list):
    if isinstance(node, ast.Raise):
        return True
    for _node in decorator_list:
        if isinstance(_node, ast.Name) and _node.id == 'abstractmethod':
            return True
        if isinstance(_node, ast.Attribute) and _node.attr == 'abstractmethod':
            return True
    return False

def might_be_docstring(node):
    return (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
    )


def process_func_def(node: ast.FunctionDef):
    if node.returns is not None:
        # already has return type, no need to add one
        return None
    returns = []
    walk = list(ast.walk(node))[1:]
    if len(node.body) == 1 and might_be_abstract_method(node.body[0], node.decorator_list):
        # might be an abstract method that needs overriding
        return
    if (
            len(node.body) == 2
            and might_be_docstring(node.body[0])
            and might_be_abstract_method(node.body[1], node.decorator_list)
    ):
        # might be abstract method with docstring
        return

    for _node in walk:
        if isinstance(_node, (ast.FunctionDef, ast.Yield, ast.YieldFrom)):
            # don't rewrite functions with nested functions inside them,
            # nor functions with yield or yield from
            return
        if isinstance(_node, ast.Return):
            returns.append(process_return(_node.value))
    if not returns or all(i == 'None' for i in returns):
        return node
    return None

def rewrite_return_type(src, name, lineno, col_offset, tokens):
    lines = src.splitlines(keepends=True)
    before = ''.join(lines[:lineno-1])
    after = ''.join(lines[lineno-1:])
    tokens = _find_start_token(tokens, lineno, col_offset)
    line_, col_offset_ = _find_closing_paren(tokens)
    after_before = ''.join(after.splitlines(keepends=True)[:line_])[:col_offset_]
    after_after = ''.join(after.splitlines(keepends=True)[line_-1:])[col_offset_:]
    pattern = fr'^(\)\s*)(:)'
    rewrite = re.sub(pattern, '\\1 -> None:', after_after)
    src = before + after[:col_offset] + after_before + rewrite
    return src



def rewrite(src):
    tree = ast.parse(src)
    to_rewrite = []
    for _node in ast.walk(tree):
        if isinstance(_node, ast.FunctionDef):
            _to_rewrite = process_func_def(_node)
            if _to_rewrite is not None:
                to_rewrite.append(_to_rewrite)
    if not to_rewrite:
        return False, src
    tokens = src_to_tokens(src)
    for node in to_rewrite:
        src = rewrite_return_type(src, node.name, node.lineno, node.col_offset, tokens)
    return True, src


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

