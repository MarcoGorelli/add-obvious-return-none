import argparse
import sys
import ast

def process_return(node: ast.Return):
    if node is None:
        return None
    elif isinstance(node, ast.Constant):
        return node.value


def process_func_def(node: ast.FunctionDef):
    returns = []
    walk = ast.walk(node)
    next(walk)
    returns.append(process_return(node.returns))
    for _node in walk:
        if isinstance(_node, ast.FunctionDef):
            return
        if isinstance(_node, ast.Return):
            returns.append(process_return(_node.value))
    breakpoint()
    pass

def rewrite(src):
    tree = ast.parse(src)
    for _node in ast.walk(tree):
        if isinstance(_node, ast.FunctionDef):
            process_func_def(_node)
    return False, src


def main(src, file_):
    ret, src = rewrite(src)
    if should_rewrite:
        with open(file_, 'w', encoding='utf-8') as fd:
            fd.write(src)
    return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*')
    args = parser.parse_arguments()
    ret = 0
    for file_ in args.files:
        with open(file_, encoding='utf-8') as fd:
            content = fd.read()
        ret |= main(content, file_)
    sys.exit(exit)

