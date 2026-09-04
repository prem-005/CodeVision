import ast
import re

class ComplexityAnalyzer:
    @classmethod
    def analyze(cls, code, language='python'):
        return analyze_code_complexity(language, code)

    @classmethod
    def analyze_complexity(cls, code, language='python'):
        return analyze_code_complexity(language, code)

def analyze_code_complexity(language, code):
    lang = language.lower().strip()
    if lang in ('py', 'python', 'python3'):
        return _analyze_python_ast(code)
    else:
        return _analyze_regex_fallback(code)

def _analyze_python_ast(code):
    try:
        tree = ast.parse(code)
    except Exception:
        return _analyze_regex_fallback(code)

    class ComplexityVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_loop_depth = 0
            self.max_loop_depth = 0
            self.fn_defs = set()
            self.rec_calls = 0
            self.has_sort = False
            self.has_dict_or_set = False
            self.has_array_allocation = False

        def visit_FunctionDef(self, node):
            self.fn_defs.add(node.name)
            self.generic_visit(node)

        def visit_For(self, node):
            self.current_loop_depth += 1
            if self.current_loop_depth > self.max_loop_depth:
                self.max_loop_depth = self.current_loop_depth
            self.generic_visit(node)
            self.current_loop_depth -= 1

        def visit_While(self, node):
            self.current_loop_depth += 1
            if self.current_loop_depth > self.max_loop_depth:
                self.max_loop_depth = self.current_loop_depth
            self.generic_visit(node)
            self.current_loop_depth -= 1

        def visit_Dict(self, node):
            self.has_dict_or_set = True
            self.generic_visit(node)

        def visit_Set(self, node):
            self.has_dict_or_set = True
            self.generic_visit(node)

        def visit_ListComp(self, node):
            self.has_array_allocation = True
            self.generic_visit(node)

        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                if node.func.id in self.fn_defs:
                    self.rec_calls += 1
                if node.func.id in ('sorted', 'heapq'):
                    self.has_sort = True
                if node.func.id in ('set', 'dict'):
                    self.has_dict_or_set = True
                if node.func.id == 'list':
                    self.has_array_allocation = True
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr == 'sort':
                    self.has_sort = True
            self.generic_visit(node)

    visitor = ComplexityVisitor()
    try:
        visitor.visit(tree)
    except Exception:
        return _analyze_regex_fallback(code)

    if visitor.rec_calls > 1:
        time_c = 'O(2^N)'
        reason = 'Recursive branching: multiple recursive calls per frame'
        space_c = 'O(N)'
    elif visitor.rec_calls == 1:
        time_c = 'O(N)'
        reason = 'Linear recursion: single recursive call chain'
        space_c = 'O(N)'
    elif visitor.has_sort and visitor.max_loop_depth == 0:
        time_c = 'O(N log N)'
        reason = 'Efficient comparison sorting detected'
        space_c = 'O(N)' if visitor.has_array_allocation else 'O(1)'
    elif visitor.max_loop_depth == 0:
        time_c = 'O(1)'
        reason = 'Direct sequential statements without iterative loops'
        space_c = 'O(1)'
    elif visitor.max_loop_depth == 1:
        time_c = 'O(N)'
        reason = 'Single linear loop iterating through inputs'
        space_c = 'O(N)' if (visitor.has_dict_or_set or visitor.has_array_allocation) else 'O(1)'
    elif visitor.max_loop_depth == 2:
        time_c = 'O(N^2)'
        reason = 'Double nested loops (quadratic time complexity)'
        space_c = 'O(N)' if (visitor.has_dict_or_set or visitor.has_array_allocation) else 'O(1)'
    else:
        time_c = f'O(N^{visitor.max_loop_depth})'
        reason = f'{visitor.max_loop_depth} nested loops detected'
        space_c = 'O(N)' if (visitor.has_dict_or_set or visitor.has_array_allocation) else 'O(1)'

    return {
        'time_complexity': time_c,
        'space_complexity': space_c,
        'reason': reason,
        'max_loop_depth': visitor.max_loop_depth,
        'has_recursion': (visitor.rec_calls > 0)
    }

def _analyze_regex_fallback(code):
    try:
        lines = code.splitlines()
        nested_depth = 0
        current_depth = 0

        for line in lines:
            trimmed = line.strip()
            if re.search(r'\b(for|while)\b', trimmed):
                current_depth += 1
                if current_depth > nested_depth:
                    nested_depth = current_depth
            if '}' in trimmed and current_depth > 0:
                current_depth -= 1

        if nested_depth == 0:
            time_c = 'O(1)'
            reason = 'Direct sequential execution'
        elif nested_depth == 1:
            time_c = 'O(N)'
            reason = 'Single linear loop iterating through inputs'
        elif nested_depth == 2:
            time_c = 'O(N^2)'
            reason = 'Double nested loops (quadratic time complexity)'
        else:
            time_c = f'O(N^{nested_depth})'
            reason = f'{nested_depth} nested loops detected'

        has_rec = False
        try:
            fn_matches = re.findall(r'\b([a-zA-Z_]\w*)\s*\(', code)
            if fn_matches:
                counts = {}
                for fn in fn_matches:
                    if fn not in ('print', 'println', 'printf', 'scanf', 'main', 'System', 'Scanner', 'cin', 'cout', 'parseInt', 'parseFloat'):
                        counts[fn] = counts.get(fn, 0) + 1
                        if counts[fn] >= 2:
                            has_rec = True
                            break
        except Exception:
            has_rec = False

        return {
            'time_complexity': 'O(2^N)' if has_rec and nested_depth == 0 else time_c,
            'space_complexity': 'O(N)' if ('new ' in code or 'malloc' in code or has_rec) else 'O(1)',
            'reason': reason,
            'max_loop_depth': nested_depth,
            'has_recursion': has_rec
        }
    except Exception:
        return {
            'time_complexity': 'O(N)',
            'space_complexity': 'O(1)',
            'reason': 'Linear iteration over inputs',
            'max_loop_depth': 1,
            'has_recursion': False
        }
