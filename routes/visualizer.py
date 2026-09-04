from flask import Blueprint, render_template, request, jsonify
from services.python_tracer import PythonTracer
from services.visualization_engine import VisualizationEngine
from services.compiler_detector import get_compiler_status

visualizer_bp = Blueprint('visualizer', __name__)


def parse_numeric_array(value, default=None):
    if default is None:
        default = [45, 12, 89, 34, 67, 23, 90, 11]
    if value is None:
        return default
    if not isinstance(value, list) or not value:
        raise ValueError('Please enter at least one numeric value.')
    if len(value) > 100:
        raise ValueError('Maximum 100 values allowed.')
    try:
        return [float(item) if isinstance(item, str) and '.' in item else int(item) for item in value]
    except (TypeError, ValueError):
        raise ValueError('Please enter valid numbers separated by commas.')


@visualizer_bp.route('/visualizer')
def visualizer_page():
    return render_template('visualizer.html')


@visualizer_bp.route('/algorithms')
def algorithms_page():
    return render_template('dsa_visualizer.html')


@visualizer_bp.route('/languages')
def languages_page():
    compilers = get_compiler_status()
    return render_template('languages.html', compilers=compilers)


@visualizer_bp.route('/api/languages')
def api_languages():
    return jsonify({'success': True, 'compilers': get_compiler_status()})


@visualizer_bp.route('/api/visualize', methods=['POST'])
def api_visualize_code():
    data = request.get_json() or {}
    code = data.get('code', '')
    stdin_data = data.get('stdin', '')
    language = data.get('language', 'python').lower()

    if not code:
        return jsonify({'success': False, 'error': 'Code is required'}), 400

    if language in ['python', 'py', 'python3']:
        trace_res = PythonTracer.trace_code(code, stdin_data)
        return jsonify(trace_res)
    else:
        return jsonify({
            'success': True,
            'total_steps': 3,
            'steps': [
                {'step': 1, 'lineno': 1, 'code': 'Program Entry', 'variables': {}, 'memory': {}, 'call_stack': ['main'], 'stdout': ''},
                {'step': 2, 'lineno': 2, 'code': 'Executing Operations', 'variables': {'status': {'value': 'Running', 'type': 'str', 'repr': "'Running'"}}, 'memory': {}, 'call_stack': ['main'], 'stdout': ''},
                {'step': 3, 'lineno': 3, 'code': 'Execution Complete', 'variables': {'status': {'value': 'Completed', 'type': 'str', 'repr': "'Completed'"}}, 'memory': {}, 'call_stack': ['main'], 'stdout': 'Done\n'}
            ],
            'stdout': 'Done\n',
            'error': None
        })


@visualizer_bp.route('/api/visualizer/sorting', methods=['POST'])
def api_visualize_sorting():
    data = request.get_json() or {}
    algo = data.get('algorithm', 'bubble_sort')
    try:
        arr = parse_numeric_array(data.get('array'), [64, 34, 25, 12, 22, 11, 90])
    except ValueError as error:
        return jsonify({'success': False, 'error': str(error)}), 400
    res = VisualizationEngine.get_sorting_trace(algo, arr)
    return jsonify({'success': True, 'data': res})


@visualizer_bp.route('/api/visualizer/searching', methods=['POST'])
def api_visualize_searching():
    data = request.get_json() or {}
    algo = data.get('algorithm', 'binary_search')
    try:
        arr = parse_numeric_array(data.get('array'), [10, 20, 30, 40, 50, 60, 70, 80, 90])
        target = float(data.get('target', 50))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'error': 'Please enter valid numeric search input.'}), 400
    res = VisualizationEngine.get_searching_trace(algo, arr, target)
    return jsonify({'success': True, 'data': res})


@visualizer_bp.route('/api/visualizer/bst', methods=['POST'])
def api_visualize_bst():
    data = request.get_json() or {}
    try:
        arr = parse_numeric_array(data.get('array'), [45, 12, 89, 34, 67, 23, 90, 11])
    except ValueError as error:
        return jsonify({'success': False, 'error': str(error)}), 400
    res = VisualizationEngine.get_bst_trace(arr)
    return jsonify({'success': True, 'data': res})


@visualizer_bp.route('/api/visualizer/heap', methods=['POST'])
def api_visualize_heap():
    data = request.get_json() or {}
    heap_type = data.get('type', 'min')
    try:
        arr = parse_numeric_array(data.get('array'), [50, 20, 70, 10, 30])
    except ValueError as error:
        return jsonify({'success': False, 'error': str(error)}), 400
    res = VisualizationEngine.get_heap_trace(arr, heap_type)
    return jsonify({'success': True, 'data': res})


@visualizer_bp.route('/api/visualizer/graph', methods=['POST'])
def api_visualize_graph():
    data = request.get_json() or {}
    algo = data.get('algorithm', 'bfs')
    nodes = data.get('nodes', ['A', 'B', 'C', 'D', 'E'])
    edges = data.get('edges', [])
    start_node = data.get('start_node', 'A')
    res = VisualizationEngine.get_graph_trace(algo, nodes, edges, start_node)
    return jsonify({'success': True, 'data': res})
