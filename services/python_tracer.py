import inspect
import io
import sys

PRIMITIVE_TYPES = (type(None), bool, int, float, str, bytes)
REFERENCE_TYPES = (list, dict, set, tuple)


def safe_serialize(value, depth=0, seen=None):
    if seen is None:
        seen = set()
    if depth > 3:
        return '...'
    if isinstance(value, PRIMITIVE_TYPES):
        return value if not isinstance(value, bytes) else value.decode('utf-8', errors='replace')
    identity = id(value)
    if identity in seen:
        return '<circular reference>'
    seen.add(identity)
    if isinstance(value, (list, tuple, set)):
        return [safe_serialize(item, depth + 1, seen) for item in list(value)[:50]]
    if isinstance(value, dict):
        return {str(key): safe_serialize(item, depth + 1, seen) for key, item in list(value.items())[:50]}
    return str(value)[:120]


def extract_type_info(value):
    return type(value).__name__ if value is not None else 'None'


def is_reference_object(value):
    if isinstance(value, PRIMITIVE_TYPES):
        return False
    if inspect.ismodule(value) or inspect.isfunction(value) or inspect.ismethod(value) or inspect.isclass(value):
        return False
    return isinstance(value, REFERENCE_TYPES) or hasattr(value, '__dict__') or hasattr(type(value), '__slots__')


def trace_python_execution(code: str, stdin_data: str = '') -> dict:
    return PythonTracer.trace_code(code, stdin_data)


class PythonTracer:
    @classmethod
    def trace_code(cls, code: str, stdin_data: str = '') -> dict:
        frames = []
        stdout_capture = io.StringIO()
        old_stdout = sys.stdout
        old_stdin = sys.stdin
        object_numbers = {}
        next_object_number = [1]
        max_steps = 300
        step_count = [0]
        code_lines = code.splitlines() if code else []

        # Recursion Tree Tracker
        call_tree_nodes = {}
        frame_call_ids = {}
        call_id_counter = [0]

        if stdin_data:
            sys.stdin = io.StringIO(stdin_data)

        def object_id_for(value):
            identity = id(value)
            if identity not in object_numbers:
                object_numbers[identity] = f'obj-{next_object_number[0]}'
                next_object_number[0] += 1
            return object_numbers[identity]

        def reference_state(value):
            if not is_reference_object(value):
                return {'kind': 'primitive', 'value': safe_serialize(value), 'type': extract_type_info(value)}
            return {'kind': 'reference', 'objectId': object_id_for(value)}

        def inspect_object(value, depth=0, active=None):
            active = set() if active is None else active
            object_id = object_id_for(value)
            result = {
                'objectId': object_id,
                'label': f'Object #{object_id.split("-")[-1]}',
                'type': type(value).__name__.upper() if not hasattr(value, '__dict__') else type(value).__name__,
                'kind': 'object',
                'elements': [],
                'fields': {},
                'references': []
            }
            if id(value) in active or depth > 4:
                return result
            active = active | {id(value)}
            if isinstance(value, (list, tuple, set)):
                result['type'] = type(value).__name__.upper()
                for index, item in enumerate(list(value)[:50]):
                    state = reference_state(item)
                    result['elements'].append({'index': index, 'value': state})
                    if state['kind'] == 'reference':
                        result['references'].append({'label': f'[{index}]', 'objectId': state['objectId']})
            elif isinstance(value, dict):
                result['type'] = 'DICT'
                for key, item in list(value.items())[:50]:
                    state = reference_state(item)
                    result['fields'][str(key)] = state
                    if state['kind'] == 'reference':
                        result['references'].append({'label': str(key), 'objectId': state['objectId']})
            else:
                try:
                    attributes = vars(value)
                except (TypeError, AttributeError):
                    attributes = {}
                for name, item in list(attributes.items())[:50]:
                    state = reference_state(item)
                    result['fields'][name] = state
                    if state['kind'] == 'reference':
                        result['references'].append({'label': name, 'objectId': state['objectId']})
            return result

        def collect_state(frame):
            visible_frames = []
            current = frame
            while current and current.f_code.co_filename == '<user_code>':
                visible_frames.append(current)
                current = current.f_back
            visible_frames.reverse()
            variables = {}
            roots = []
            for scope_frame in visible_frames:
                for name, value in scope_frame.f_locals.items():
                    if name.startswith('__') or inspect.ismodule(value) or inspect.isfunction(value) or inspect.isclass(value):
                        continue
                    roots.append(value)
                    if name in variables:
                        continue
                    state = reference_state(value)
                    if state['kind'] == 'reference':
                        label = f'Object #{state["objectId"].split("-")[-1]}'
                        variables[name] = {'value': label, 'type': extract_type_info(value), 'repr': label, 'reference': state['objectId']}
                    else:
                        variables[name] = {'value': state['value'], 'type': state['type'], 'repr': str(value)[:80], 'reference': None}

            objects = {}
            pending = list(roots)
            visited = set()
            while pending and len(visited) < 150:
                value = pending.pop(0)
                if not is_reference_object(value) or id(value) in visited:
                    continue
                visited.add(id(value))
                object_record = inspect_object(value)
                objects[object_record['objectId']] = object_record
                if isinstance(value, (list, tuple, set)):
                    pending.extend(list(value)[:50])
                elif isinstance(value, dict):
                    pending.extend(list(value.values())[:50])
                else:
                    try:
                        pending.extend(list(vars(value).values())[:50])
                    except (TypeError, AttributeError):
                        pass

            for object_record in objects.values():
                object_record['referenceCount'] = sum(
                    1 for variable in variables.values() if variable.get('reference') == object_record['objectId']
                ) + sum(
                    1 for parent in objects.values() for reference in parent['references']
                    if reference['objectId'] == object_record['objectId']
                )
            return variables, {'objects': list(objects.values()), 'objectCount': len(objects)}

        def format_call_signature(frame):
            fn_name = frame.f_code.co_name
            args = []
            for arg_name in frame.f_code.co_varnames[:frame.f_code.co_argcount]:
                val = frame.f_locals.get(arg_name)
                args.append(f"{safe_serialize(val)}")
            return f"{fn_name}({', '.join(args)})"

        def get_tree_snapshot():
            return [
                {
                    'id': node['id'],
                    'label': node['label'],
                    'parentId': node['parentId'],
                    'depth': node['depth'],
                    'status': node['status'],
                    'returnVal': node['returnVal'],
                    'fnName': node['fnName']
                }
                for node in call_tree_nodes.values()
            ]

        def trace_handler(frame, event, arg):
            if step_count[0] >= max_steps:
                return None
            if frame.f_code.co_filename != '<user_code>':
                return trace_handler

            fn_name = frame.f_code.co_name

            if event == 'call' and fn_name != '<module>':
                call_id_counter[0] += 1
                node_id = f"call_{call_id_counter[0]}"
                frame_call_ids[id(frame)] = node_id

                parent_frame = frame.f_back
                parent_node_id = None
                while parent_frame:
                    if id(parent_frame) in frame_call_ids:
                        parent_node_id = frame_call_ids[id(parent_frame)]
                        break
                    parent_frame = parent_frame.f_back

                depth = (call_tree_nodes[parent_node_id]['depth'] + 1) if parent_node_id and parent_node_id in call_tree_nodes else 0
                call_tree_nodes[node_id] = {
                    'id': node_id,
                    'label': format_call_signature(frame),
                    'parentId': parent_node_id,
                    'depth': depth,
                    'status': 'calling',
                    'returnVal': None,
                    'fnName': fn_name
                }

            elif event == 'return' and id(frame) in frame_call_ids:
                node_id = frame_call_ids[id(frame)]
                if node_id in call_tree_nodes:
                    call_tree_nodes[node_id]['status'] = 'returned'
                    call_tree_nodes[node_id]['returnVal'] = safe_serialize(arg)

            variables, memory = collect_state(frame)
            call_stack = []
            current = frame
            while current and current.f_code.co_filename == '<user_code>':
                call_stack.append(current.f_code.co_name)
                current = current.f_back
            call_stack.reverse()
            lineno = frame.f_lineno

            active_call_id = frame_call_ids.get(id(frame))

            frames.append({
                'step': step_count[0] + 1,
                'event': event,
                'lineno': lineno,
                'code': code_lines[lineno - 1] if 0 < lineno <= len(code_lines) else '',
                'variables': variables,
                'memory': memory,
                'call_stack': call_stack,
                'recursion_tree': get_tree_snapshot(),
                'active_call_id': active_call_id,
                'stdout': stdout_capture.getvalue()
            })
            step_count[0] += 1
            return trace_handler

        sys.stdout = stdout_capture
        exec_error = None
        try:
            compiled = compile(code, '<user_code>', 'exec')
            sys.settrace(trace_handler)
            exec(compiled, {'__name__': '__main__'})
        except Exception as error:
            exec_error = f'{type(error).__name__}: {error}'
            last_frame = frames[-1] if frames else None
            frames.append({
                'step': len(frames) + 1,
                'event': 'exception',
                'lineno': last_frame['lineno'] if last_frame else 1,
                'code': 'Exception occurred',
                'variables': last_frame['variables'] if last_frame else {},
                'memory': last_frame['memory'] if last_frame else {'objects': [], 'objectCount': 0},
                'call_stack': last_frame['call_stack'] if last_frame else ['main'],
                'recursion_tree': get_tree_snapshot(),
                'active_call_id': None,
                'stdout': stdout_capture.getvalue(),
                'error': exec_error
            })
        finally:
            sys.settrace(None)
            sys.stdout = old_stdout
            sys.stdin = old_stdin
        return {'success': True, 'total_steps': len(frames), 'steps': frames, 'stdout': stdout_capture.getvalue(), 'error': exec_error}
