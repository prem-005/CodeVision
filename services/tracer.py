import sys
import os
import io
import json
import traceback

class CodeTracer:
    def __init__(self, code, max_steps=400):
        self.code = code
        self.max_steps = max_steps
        self.steps = []
        self.output_buffer = io.StringIO()
        self.current_step = 0
        self.call_counter = 0
        self.active_call_ids = []
        self.call_history = {} # call_id -> info
        self.prev_locals = {}

    def trace(self):
        """Execute Python code and capture call, line, and return execution states with rich beginner metadata."""
        try:
            compiled_code = compile(self.code, '<user_code>', 'exec')
        except SyntaxError as se:
            return {
                'success': False,
                'error': f'SyntaxError: {se.msg} at line {se.lineno}',
                'steps': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Compile error: {str(e)}',
                'steps': []
            }

        old_stdout = sys.stdout
        sys.stdout = self.output_buffer
        lines = self.code.splitlines()

        def tracer_func(frame, event, arg):
            if self.current_step >= self.max_steps:
                return None

            # Only trace code running in <user_code>
            if frame.f_code.co_filename != '<user_code>' or frame.f_code.co_name in ('tracer_func', 'trace'):
                return tracer_func

            if event in ('line', 'return', 'call'):
                lineno = frame.f_lineno
                if lineno <= 0:
                    lineno = 1
                line_text = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
                raw_fn_name = frame.f_code.co_name
                is_main = (raw_fn_name == '<module>')
                fn_name = '<main>' if is_main else f"{raw_fn_name}()"

                # Handle call id tracking for recursion tree
                if event == 'call':
                    self.call_counter += 1
                    current_call_id = self.call_counter
                    parent_call_id = self.active_call_ids[-1] if self.active_call_ids else None
                    self.active_call_ids.append(current_call_id)
                    
                    # Extract arguments
                    call_args = {}
                    for k, v in frame.f_locals.items():
                        if not k.startswith('__') and not callable(v):
                            call_args[k] = self._format_value(v)[0]

                    self.call_history[current_call_id] = {
                        'id': current_call_id,
                        'parent_id': parent_call_id,
                        'function': fn_name,
                        'args': call_args,
                        'status': 'active',
                        'return_value': None,
                        'call_line': lineno,
                        'depth': len(self.active_call_ids)
                    }
                else:
                    current_call_id = self.active_call_ids[-1] if self.active_call_ids else 1
                
                # Scope identifier
                raw_locals = frame.f_locals
                clean_locals = {}
                heap_objects = {}
                current_locals_dict = {}

                for k, v in raw_locals.items():
                    if k.startswith('__') and k.endswith('__'):
                        continue
                    if k in ('CodeTracer', 'tracer_func', 'compiled_code'):
                        continue
                    # Omit function declarations from main variable cards to keep it clean for beginners
                    if callable(v) and not isinstance(v, (list, dict, set, tuple)):
                        continue
                    
                    val_str, val_type, heap_repr = self._format_value(v, var_name=k)
                    clean_locals[k] = {
                        'name': k,
                        'value': val_str,
                        'type': val_type,
                        'raw': heap_repr
                    }
                    current_locals_dict[k] = val_str
                    if heap_repr is not None:
                        heap_objects[k] = heap_repr

                # Detect variable changes (diff)
                changed_vars = []
                for k, v_str in current_locals_dict.items():
                    old_v = self.prev_locals.get(k)
                    if old_v is None:
                        changed_vars.append({'name': k, 'action': 'created', 'old': None, 'new': v_str})
                    elif old_v != v_str:
                        changed_vars.append({'name': k, 'action': 'updated', 'old': old_v, 'new': v_str})
                
                self.prev_locals = dict(current_locals_dict)

                # Extract Call Stack
                stack = []
                f = frame
                while f is not None:
                    if f.f_code.co_filename == '<user_code>' and f.f_code.co_name != 'tracer_func':
                        nm = '<main>' if f.f_code.co_name == '<module>' else f"{f.f_code.co_name}()"
                        frame_args = {k: self._format_value(v)[0] for k, v in f.f_locals.items() if not k.startswith('__') and not callable(v)}
                        stack.append({
                            'function': nm,
                            'line': max(1, f.f_lineno),
                            'locals': frame_args
                        })
                    f = f.f_back

                clean_stack = list(reversed(stack))
                if not clean_stack:
                    clean_stack = [{'function': '<main>', 'line': lineno, 'locals': {}}]

                ret_val = None
                if event == 'return':
                    ret_val_str, ret_type, _ = self._format_value(arg)
                    ret_val = {'value': ret_val_str, 'type': ret_type}
                    if current_call_id in self.call_history:
                        self.call_history[current_call_id]['status'] = 'returned'
                        self.call_history[current_call_id]['return_value'] = ret_val_str

                # Build beginner-friendly explanation
                explanation = self._generate_explanation(event, lineno, line_text, fn_name, clean_locals, ret_val, changed_vars)

                # Snapshot of all recursion calls up to this step
                call_tree_snapshot = [dict(v) for v in self.call_history.values()]

                step_data = {
                    'step': len(self.steps) + 1,
                    'event': event,
                    'function': fn_name,
                    'line': lineno,
                    'line_text': line_text.strip(),
                    'return_value': ret_val,
                    'locals': clean_locals,
                    'heap': heap_objects,
                    'stack': clean_stack,
                    'call_tree': call_tree_snapshot,
                    'active_call_id': current_call_id,
                    'changed_vars': changed_vars,
                    'explanation': explanation,
                    'output': self.output_buffer.getvalue()
                }
                self.steps.append(step_data)
                self.current_step += 1

                if event == 'return' and self.active_call_ids:
                    self.active_call_ids.pop()

            return tracer_func

        try:
            sys.settrace(tracer_func)
            exec(compiled_code, {'__name__': '__main__'})
        except Exception as e:
            err_line = 1
            try:
                cl, exc, tb_obj = sys.exc_info()
                while tb_obj.tb_next:
                    tb_obj = tb_obj.tb_next
                if tb_obj.tb_frame.f_code.co_filename == '<user_code>':
                    err_line = tb_obj.tb_lineno
            except Exception:
                pass

            self.steps.append({
                'step': len(self.steps) + 1,
                'event': 'error',
                'function': 'Error',
                'line': max(1, err_line),
                'line_text': f'Runtime Error: {str(e)}',
                'return_value': None,
                'locals': {},
                'heap': {},
                'stack': [{'function': 'Error', 'line': max(1, err_line), 'locals': {}}],
                'call_tree': [dict(v) for v in self.call_history.values()],
                'active_call_id': None,
                'changed_vars': [],
                'explanation': f"⚠️ An error occurred at line {err_line}: {type(e).__name__}: {str(e)}",
                'output': self.output_buffer.getvalue() + f"\nRuntimeError: {str(e)}"
            })
        finally:
            sys.settrace(None)
            sys.stdout = old_stdout

        final_output = self.output_buffer.getvalue()
        
        # Add final completion step
        if self.steps:
            last_step = self.steps[-1]
            if last_step['event'] != 'error':
                self.steps.append({
                    'step': len(self.steps) + 1,
                    'event': 'completed',
                    'function': '<main>',
                    'line': max(1, len(lines)),
                    'line_text': '# Execution Completed Successfully',
                    'return_value': None,
                    'locals': last_step.get('locals', {}),
                    'heap': last_step.get('heap', {}),
                    'stack': [{'function': '<main>', 'line': max(1, len(lines)), 'locals': {}}],
                    'call_tree': [dict(v) for v in self.call_history.values()],
                    'active_call_id': None,
                    'changed_vars': [],
                    'explanation': "🎉 Program finished execution successfully! All operations are complete.",
                    'output': final_output
                })

        return {
            'success': True,
            'total_steps': len(self.steps),
            'steps': self.steps,
            'final_output': final_output
        }

    def _generate_explanation(self, event, lineno, line_text, fn_name, locals_dict, ret_val, changed_vars):
        """Generate clear, simple plain-English explanations for beginners."""
        text = line_text.strip()
        
        if event == 'call':
            args_str = ", ".join([f"{k}={v['value']}" for k, v in locals_dict.items()])
            if fn_name == '<main>':
                return f"🚀 Starting program execution at Line {lineno}."
            return f"📞 Calling function {fn_name} with arguments ({args_str or 'no arguments'}). New stack frame created."

        if event == 'return':
            if ret_val:
                return f"↩️ Function {fn_name} returned value {ret_val['value']} (type: {ret_val['type']}). Frame popped from stack."
            return f"↩️ Exiting {fn_name} (returns None). Frame popped from stack."

        # Line event explanations
        if changed_vars:
            parts = []
            for cv in changed_vars:
                if cv['action'] == 'created':
                    parts.append(f"created `{cv['name']}` = {cv['new']}")
                else:
                    parts.append(f"updated `{cv['name']}`: {cv['old']} ➔ {cv['new']}")
            return f"Line {lineno}: `{text}` ➔ {', '.join(parts)}."

        if text.startswith('if '):
            return f"Line {lineno}: Checking condition `{text}`."
        if text.startswith('for ') or text.startswith('while '):
            return f"Line {lineno}: Loop iteration check `{text}`."
        if text.startswith('print('):
            return f"Line {lineno}: Printing output to console: `{text}`."
        if text.startswith('return '):
            return f"Line {lineno}: Returning result: `{text}`."
        if text.startswith('def '):
            return f"Line {lineno}: Defined function `{text.split('(')[0]}`."

        return f"Line {lineno}: Executing `{text}`."

    def _format_value(self, val, var_name=""):
        """Format Python variables for visualizer representation."""
        t_name = type(val).__name__
        obj_id = f"0x{(id(val) % 65536):04X}"
        
        if isinstance(val, (int, float, bool, str, type(None))):
            return repr(val), t_name, None
        elif isinstance(val, list):
            items = [self._format_value(x)[0] for x in val]
            return f"[{', '.join(items)}]", f"list[{len(val)}]", {
                'address': obj_id,
                'name': var_name or 'list',
                'kind': 'Array',
                'type': f'list[{len(val)}]',
                'length': len(val),
                'elements': items
            }
        elif isinstance(val, dict):
            items = {str(k): self._format_value(v)[0] for k, v in val.items()}
            return f"dict({len(val)})", f"dict[{len(val)}]", {
                'address': obj_id,
                'name': var_name or 'dict',
                'kind': 'Dictionary',
                'type': f'dict[{len(val)}]',
                'size': len(val),
                'entries': items
            }
        elif isinstance(val, set):
            items = [self._format_value(x)[0] for x in val]
            return f"set({len(val)})", f"set[{len(val)}]", {
                'address': obj_id,
                'name': var_name or 'set',
                'kind': 'Set',
                'type': f'set[{len(val)}]',
                'size': len(val),
                'elements': items
            }
        elif isinstance(val, tuple):
            items = [self._format_value(x)[0] for x in val]
            return f"({', '.join(items)})", f"tuple[{len(val)}]", {
                'address': obj_id,
                'name': var_name or 'tuple',
                'kind': 'Tuple',
                'type': f'tuple[{len(val)}]',
                'length': len(val),
                'elements': items
            }
        else:
            return str(val), t_name, {
                'address': obj_id,
                'name': var_name or t_name,
                'kind': 'Object',
                'type': t_name,
                'repr': str(val)
            }

def trace_python_code(code, max_steps=400):
    tracer = CodeTracer(code, max_steps)
    return tracer.trace()

