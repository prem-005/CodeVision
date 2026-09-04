from flask import Blueprint, render_template, request, jsonify
from services.python_tracer import PythonTracer
from services.mutation_engine import MutationEngine

code_lab_bp = Blueprint('code_lab', __name__, url_prefix='/code-lab')


@code_lab_bp.route('')
@code_lab_bp.route('/')
def code_lab_hub():
    return render_template('code_lab/hub.html')


@code_lab_bp.route('/time-machine')
def time_machine_page():
    return render_template('code_lab/time_machine.html')


@code_lab_bp.route('/mutation')
def mutation_lab_page():
    return render_template('code_lab/mutation.html')


@code_lab_bp.route('/api/time-machine/trace', methods=['POST'])
def api_time_machine_trace():
    data = request.get_json() or {}
    code = data.get('code', '')
    stdin_data = data.get('stdin', '')

    if not code:
        return jsonify({'success': False, 'error': 'Code is required'}), 400

    trace_res = PythonTracer.trace_code(code, stdin_data)
    if not trace_res.get('success'):
        return jsonify(trace_res), 400

    steps = trace_res.get('steps', [])
    var_history = MutationEngine.extract_variable_history(steps)

    return jsonify({
        'success': True,
        'total_steps': len(steps),
        'steps': steps,
        'variable_history': var_history,
        'stdout': trace_res.get('stdout', ''),
        'error': trace_res.get('error')
    })


@code_lab_bp.route('/api/time-machine/diff', methods=['POST'])
def api_time_machine_diff():
    data = request.get_json() or {}
    step_a = data.get('step_a')
    step_b = data.get('step_b')

    if not step_a or not step_b:
        return jsonify({'success': False, 'error': 'Both step_a and step_b are required.'}), 400

    diff = MutationEngine.calculate_step_diff(step_a, step_b)
    return jsonify({'success': True, 'diff': diff})


@code_lab_bp.route('/api/mutation/available', methods=['POST'])
def api_mutation_available():
    data = request.get_json() or {}
    code = data.get('code', '')

    if not code:
        return jsonify({'success': False, 'error': 'Code is required'}), 400

    mutations = MutationEngine.get_available_mutations(code)
    return jsonify({'success': True, 'mutations': mutations})


@code_lab_bp.route('/api/mutation/run', methods=['POST'])
def api_mutation_run():
    data = request.get_json() or {}
    code = data.get('code', '')
    mutation_type = data.get('mutation_type')
    stdin_data = data.get('stdin', '')

    if not code:
        return jsonify({'success': False, 'error': 'Code is required'}), 400

    mutated_code, selected_id, mutation_name = MutationEngine.mutate_code(code, mutation_type)

    orig_trace = PythonTracer.trace_code(code, stdin_data)
    mut_trace = PythonTracer.trace_code(mutated_code, stdin_data)

    orig_steps = orig_trace.get('steps', [])
    mut_steps = mut_trace.get('steps', [])

    comparison = MutationEngine.compare_traces(orig_steps, mut_steps, code, mutated_code, mutation_name)

    return jsonify({
        'success': True,
        'original_trace': orig_trace,
        'mutated_trace': mut_trace,
        'comparison': comparison,
        'mutated_code': mutated_code,
        'mutation_name': mutation_name
    })
