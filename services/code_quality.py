import ast
import re

class CodeQualityAnalyzer:
    @classmethod
    def analyze(cls, code: str, language: str = 'python') -> dict:
        language = (language or 'python').lower()
        if language in ['python', 'py']:
            return cls._analyze_python(code)
        else:
            return cls._analyze_generic(code, language)

    @classmethod
    def _analyze_python(cls, code: str) -> dict:
        score = 100
        suggestions = []
        time_complexity = 'O(n)'
        space_complexity = 'O(1)'
        nested_loops = 0
        has_recursion = False
        function_lengths = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                'score': 50,
                'time_complexity': 'Unknown (Syntax Error)',
                'space_complexity': 'Unknown',
                'nested_loops': 0,
                'has_recursion': False,
                'suggestions': [f'Syntax error at line {e.lineno}: {e.msg}'],
                'quality_grade': 'C'
            }

        func_defs = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        for fn in func_defs:
            fn_name = fn.name
            fn_len = len(fn.body)
            function_lengths.append({'name': fn_name, 'length': fn_len})
            if fn_len > 30:
                score -= 10
                suggestions.append(f'Function "{fn_name}" is long ({fn_len} lines). Consider breaking it into smaller helpers.')

            for child in ast.walk(fn):
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == fn_name:
                    has_recursion = True

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                inner_loops = [child for child in ast.walk(node) if isinstance(child, (ast.For, ast.While)) and child is not node]
                if inner_loops:
                    nested_loops = max(nested_loops, len(inner_loops) + 1)

        if nested_loops >= 3:
            time_complexity = 'O(n³)'
            score -= 25
            suggestions.append('Multiple nested loops detected (3+ levels). Look for hash map, dynamic programming, or mathematical optimizations.')
        elif nested_loops == 2:
            time_complexity = 'O(n²)'
            score -= 15
            suggestions.append('Nested loop detected (O(n²)). Consider using a Hash Map or Two-Pointer approach to achieve O(n) or O(n log n).')
        elif has_recursion:
            time_complexity = 'O(2ⁿ) or O(n)'
            space_complexity = 'O(n) (Call Stack)'
            suggestions.append('Recursion detected. Ensure base case is robust and consider memoization (DP) to avoid redundant computations.')
        else:
            time_complexity = 'O(n)'
            space_complexity = 'O(1)'

        for node in ast.walk(tree):
            if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp)):
                space_complexity = 'O(n)'
            elif isinstance(node, ast.Assign):
                if isinstance(node.value, (ast.List, ast.Dict, ast.Set)):
                    space_complexity = 'O(n)'

        comments_count = len(re.findall(r'#.*', code))
        if comments_count == 0 and len(code.splitlines()) > 15:
            score -= 5
            suggestions.append('Add comments explaining key algorithmic decisions.')

        score = max(40, min(100, score))
        grade = 'A+' if score >= 90 else ('A' if score >= 80 else ('B' if score >= 70 else ('C' if score >= 60 else 'D')))

        if not suggestions:
            suggestions.append('Excellent code structure! Time and space complexity are well-balanced.')

        return {
            'score': score,
            'time_complexity': time_complexity,
            'space_complexity': space_complexity,
            'nested_loops': nested_loops,
            'has_recursion': has_recursion,
            'suggestions': suggestions,
            'quality_grade': grade
        }

    @classmethod
    def _analyze_generic(cls, code: str, language: str) -> dict:
        score = 85
        suggestions = []
        nested_loops = len(re.findall(r'for\s*\(.*?\)\s*\{[^{}]*for\s*\(', code)) + len(re.findall(r'while\s*\(.*?\)\s*\{[^{}]*while\s*\(', code))
        time_complexity = 'O(n²)' if nested_loops > 0 else 'O(n)'
        space_complexity = 'O(n)' if ('new ' in code or 'malloc' in code or 'vector' in code or 'ArrayList' in code) else 'O(1)'

        if nested_loops > 0:
            score -= 15
            suggestions.append('Nested loops detected. Check if a hash table or two-pointer approach can reduce time complexity.')
        else:
            suggestions.append('Efficient linear structure detected.')

        return {
            'score': score,
            'time_complexity': time_complexity,
            'space_complexity': space_complexity,
            'nested_loops': nested_loops,
            'has_recursion': 'recur' in code.lower(),
            'suggestions': suggestions,
            'quality_grade': 'A' if score >= 80 else 'B'
        }
