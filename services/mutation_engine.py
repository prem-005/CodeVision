import re


def _flip_comparison(code):
    result = re.sub(r'(?<![><!=])>(?!=)', '<', code, count=1)
    return result if result != code else code


def _flip_comparison_reverse(code):
    result = re.sub(r'(?<![><!=])<(?!=)', '>', code, count=1)
    return result if result != code else code


def _flip_increment(code):
    if '+ 1' in code:
        return code.replace('+ 1', '- 1', 1)
    if '- 1' in code:
        return code.replace('- 1', '+ 1', 1)
    return code


class MutationEngine:

    MUTATION_PATTERNS = [
        {
            'id': 'comparison_flip',
            'name': 'Comparison Operator Flip',
            'description': 'Flips > to < in comparisons, reversing sort order / breaking min/max logic.',
            'mutate': _flip_comparison
        },
        {
            'id': 'off_by_one_boundary',
            'name': 'Loop Boundary Off-by-One',
            'description': 'Changes n-i-1 to n-i, or < len to <= len causing one extra iteration.',
            'mutate': lambda code: (
                code.replace('n - i - 1', 'n - i', 1) if 'n - i - 1' in code else
                code.replace(' < len', ' <= len', 1) if ' < len' in code else
                code.replace(' < n', ' <= n', 1)
            )
        },
        {
            'id': 'return_value_mutation',
            'name': 'Return Base-Case Flip',
            'description': 'Changes return 1 to return 0, breaking recursive base cases.',
            'mutate': lambda code: (
                code.replace('return 1', 'return 0', 1) if 'return 1' in code else
                code.replace('return 0', 'return 1', 1)
            )
        },
        {
            'id': 'increment_decrement',
            'name': 'Increment/Decrement Flip',
            'description': 'Changes +1 step to -1, reversing iteration direction.',
            'mutate': _flip_increment
        },
        {
            'id': 'condition_negation',
            'name': 'Condition Negation',
            'description': 'Negates the first if-condition with "not", inverting branch logic.',
            'mutate': lambda code: re.sub(
                r'if\s+([^:]+):',
                lambda m: 'if not (' + m.group(1).strip() + '):',
                code, count=1
            )
        },
        {
            'id': 'tree_direction_swap',
            'name': 'Tree Pointer Swap',
            'description': 'Swaps .left and .right child pointer references in tree algorithms.',
            'mutate': lambda code: (
                code.replace('.left', '__TMP_LEFT__', 1)
                    .replace('.right', '.left', 1)
                    .replace('__TMP_LEFT__', '.right', 1)
                if '.left' in code and '.right' in code else code
            )
        },
    ]

    @classmethod
    def get_available_mutations(cls, code):
        available = []
        for m in cls.MUTATION_PATTERNS:
            try:
                mutated_code = m['mutate'](code)
                if mutated_code and mutated_code != code:
                    available.append({
                        'id': m['id'],
                        'name': m['name'],
                        'description': m['description'],
                        'mutated_code': mutated_code
                    })
            except Exception:
                pass
        return available

    @classmethod
    def mutate_code(cls, code, mutation_type=None):
        available = cls.get_available_mutations(code)
        if not available:
            mutated = _flip_comparison(code) if '>' in code else _flip_comparison_reverse(code)
            return (mutated or code), 'comparison_flip', 'Comparison Operator Flip'

        if mutation_type:
            selected = next((m for m in available if m['id'] == mutation_type), None)
            if selected:
                return selected['mutated_code'], selected['id'], selected['name']

        preferred = next((m for m in available if m['id'] == 'comparison_flip'), available[0])
        return preferred['mutated_code'], preferred['id'], preferred['name']

    @classmethod
    def compare_traces(cls, original_trace, mutated_trace, original_code, mutated_code, mutation_name):
        orig_steps = original_trace or []
        mut_steps  = mutated_trace  or []
        min_len    = min(len(orig_steps), len(mut_steps))
        divergence_step    = None
        divergence_details = None

        for i in range(min_len):
            s1, s2 = orig_steps[i], mut_steps[i]

            if s1.get('lineno') != s2.get('lineno'):
                divergence_step    = i + 1
                divergence_details = {
                    'type': 'Control Flow Divergence',
                    'original': f"Line {s1.get('lineno')}: {s1.get('code','')}",
                    'mutated':  f"Line {s2.get('lineno')}: {s2.get('code','')}"
                }
                break

            v1, v2 = s1.get('variables', {}), s2.get('variables', {})
            diff_vars = []
            for k in set(v1) | set(v2):
                val1 = (v1.get(k) or {}).get('value')
                val2 = (v2.get(k) or {}).get('value')
                if val1 != val2:
                    diff_vars.append({'var': k, 'original': val1, 'mutated': val2})
            if diff_vars:
                divergence_step    = i + 1
                divergence_details = {'type': 'Variable State Divergence', 'differences': diff_vars}
                break

            if s1.get('stdout') != s2.get('stdout'):
                divergence_step    = i + 1
                divergence_details = {'type': 'Output Divergence', 'original': s1.get('stdout'), 'mutated': s2.get('stdout')}
                break

        if not divergence_step and len(orig_steps) != len(mut_steps):
            divergence_step    = min_len + 1
            divergence_details = {
                'type': 'Execution Length Divergence',
                'original': f"Total steps: {len(orig_steps)}",
                'mutated':  f"Total steps: {len(mut_steps)}"
            }

        orig_out = orig_steps[-1].get('stdout', '') if orig_steps else ''
        mut_out  = mut_steps[-1].get('stdout', '')  if mut_steps  else ''
        out_changed = orig_out != mut_out

        if out_changed or (divergence_step and divergence_step <= 5):
            severity = 'CRITICAL'
        elif divergence_step and divergence_step <= 15:
            severity = 'HIGH'
        elif divergence_step:
            severity = 'MEDIUM'
        else:
            severity = 'LOW'

        explanation = cls._generate_explanation(mutation_name, divergence_step, divergence_details, orig_out, mut_out)

        return {
            'mutation_name':       mutation_name,
            'original_code':       original_code,
            'mutated_code':        mutated_code,
            'divergence_step':     divergence_step,
            'divergence_details':  divergence_details,
            'original_total_steps': len(orig_steps),
            'mutated_total_steps':  len(mut_steps),
            'original_output':     orig_out,
            'mutated_output':      mut_out,
            'severity':            severity,
            'explanation':         explanation
        }

    @classmethod
    def _generate_explanation(cls, mutation_name, divergence_step, details, orig_out, mut_out):
        if not divergence_step:
            return f"The '{mutation_name}' mutation produced identical execution traces and output. The mutation had no observable behavioral effect on this input."

        desc = f"The '{mutation_name}' mutation caused the algorithm to diverge at Step {divergence_step}. "
        if details:
            t = details.get('type', '')
            if t == 'Control Flow Divergence':
                desc += f"Original executed {details.get('original','')}, while Mutated executed {details.get('mutated','')}. "
            elif t == 'Variable State Divergence' and details.get('differences'):
                d = details['differences'][0]
                desc += f"Variable '{d['var']}' diverged: Original='{d['original']}' vs Mutated='{d['mutated']}'. "
            elif t == 'Execution Length Divergence':
                desc += f"{details.get('original','')} vs {details.get('mutated','')}. "

        if orig_out != mut_out:
            desc += f"Final output changed from '{(orig_out or '').strip()}' to '{(mut_out or '').strip()}'."
        else:
            desc += "Final output remained identical despite intermediate execution divergence."
        return desc

    @classmethod
    def calculate_step_diff(cls, step_a, step_b):
        if not step_a or not step_b:
            return {'changes': []}
        changes = []

        if step_a.get('lineno') != step_b.get('lineno'):
            changes.append({'category': 'Line Execution', 'description': f"Line {step_a.get('lineno')} \u2192 Line {step_b.get('lineno')}"})

        va, vb = step_a.get('variables', {}), step_b.get('variables', {})
        for v in set(va) | set(vb):
            val_a = (va.get(v) or {}).get('value')
            val_b = (vb.get(v) or {}).get('value')
            if val_a != val_b:
                if v not in va:   changes.append({'category': 'Variable Created', 'description': f"Created `{v}` = {val_b}"})
                elif v not in vb: changes.append({'category': 'Variable Removed', 'description': f"Removed `{v}`"})
                else:             changes.append({'category': 'Variable Changed',  'description': f"`{v}`: {val_a} \u2192 {val_b}"})

        sa, sb = step_a.get('call_stack', []), step_b.get('call_stack', [])
        if sa != sb:
            if len(sb) > len(sa): changes.append({'category': 'Call Stack Push', 'description': f"Pushed `{sb[-1]}()`"})
            else:                 changes.append({'category': 'Call Stack Pop',  'description': f"Popped frame"})

        if step_a.get('stdout','') != step_b.get('stdout',''):
            changes.append({'category': 'Console Output', 'description': (step_b.get('stdout') or '').strip()[-80:]})

        return {'step_a': step_a.get('step'), 'step_b': step_b.get('step'), 'changes': changes}

    @classmethod
    def extract_variable_history(cls, steps):
        history = {}
        for s in steps:
            step_num = s.get('step')
            for var_name, var_info in (s.get('variables') or {}).items():
                if var_name not in history:
                    history[var_name] = []
                val = (var_info or {}).get('value')
                if not history[var_name] or history[var_name][-1]['value'] != val:
                    history[var_name].append({'step': step_num, 'value': val, 'type': (var_info or {}).get('type')})
        return history
