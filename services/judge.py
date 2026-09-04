from services.code_executor import CodeExecutor

def normalize_output(text: str) -> str:
    if text is None:
        return ""
    lines = [line.rstrip() for line in text.strip().splitlines()]
    return "\n".join(lines)

class OnlineJudge:
    @classmethod
    def run_custom(cls, language: str, code: str, stdin_data: str) -> dict:
        result = CodeExecutor.execute(language, code, stdin_data)
        return {
            'success': True,
            'status': result['status'],
            'stdout': result['stdout'],
            'stderr': result['stderr'],
            'runtime_ms': result['runtime_ms'],
            'memory_kb': result['memory_kb'],
            'exit_code': result['exit_code']
        }

    @classmethod
    def evaluate_submission(cls, problem, language: str, code: str) -> dict:
        test_cases = problem.test_cases
        if not test_cases:
            res = CodeExecutor.execute(language, code, "")
            return {
                'success': True,
                'status': 'Accepted' if res['status'] == 'Success' else res['status'],
                'passed_testcases': 1 if res['status'] == 'Success' else 0,
                'total_testcases': 1,
                'runtime_ms': res['runtime_ms'],
                'memory_kb': res['memory_kb'],
                'test_results': [{'test_index': 1, 'is_hidden': False, 'passed': res['status'] == 'Success', 'status': res['status'], 'stdout': res['stdout'], 'stderr': res['stderr']}],
                'error_message': res['stderr'] if res['status'] != 'Success' else None
            }

        total_tests = len(test_cases)
        passed_count = 0
        total_runtime = 0.0
        max_memory = 0.0
        test_results = []
        overall_status = 'Accepted'
        error_message = None

        for idx, tc in enumerate(test_cases, start=1):
            res = CodeExecutor.execute(language, code, tc.input_data)
            total_runtime += res['runtime_ms']
            max_memory = max(max_memory, res['memory_kb'])

            if res['status'] in ['Compilation Error', 'Error']:
                overall_status = res['status']
                error_message = res['stderr']
                test_results.append({
                    'test_index': idx,
                    'is_hidden': tc.is_hidden,
                    'passed': False,
                    'status': res['status'],
                    'stderr': res['stderr'] if not tc.is_hidden else 'Compilation/Execution Error'
                })
                break

            if res['status'] == 'Time Limit Exceeded':
                overall_status = 'Time Limit Exceeded'
                error_message = f'Time Limit Exceeded on {"Hidden " if tc.is_hidden else ""}Test #{idx}'
                test_results.append({
                    'test_index': idx,
                    'is_hidden': tc.is_hidden,
                    'passed': False,
                    'status': 'Time Limit Exceeded'
                })
                break

            if res['status'] == 'Runtime Error':
                overall_status = 'Runtime Error'
                error_message = f'Runtime Error on {"Hidden " if tc.is_hidden else ""}Test #{idx}: {res["stderr"]}' if not tc.is_hidden else f'Runtime Error on Hidden Test #{idx}'
                test_results.append({
                    'test_index': idx,
                    'is_hidden': tc.is_hidden,
                    'passed': False,
                    'status': 'Runtime Error',
                    'stderr': res['stderr'] if not tc.is_hidden else ''
                })
                break

            actual = normalize_output(res['stdout'])
            expected = normalize_output(tc.expected_output)

            passed = (actual == expected)
            if passed:
                passed_count += 1
                item = {
                    'test_index': idx,
                    'is_hidden': tc.is_hidden,
                    'passed': True,
                    'status': 'Passed',
                    'runtime_ms': res['runtime_ms']
                }
                if not tc.is_hidden:
                    item['input'] = tc.input_data
                    item['expected'] = tc.expected_output
                    item['actual'] = actual
                test_results.append(item)
            else:
                if overall_status == 'Accepted':
                    overall_status = 'Wrong Answer'
                    if tc.is_hidden:
                        error_message = f'Wrong Answer on Hidden Test #{idx}'
                    else:
                        error_message = f'Wrong Answer on Test #{idx}'

                item = {
                    'test_index': idx,
                    'is_hidden': tc.is_hidden,
                    'passed': False,
                    'status': 'Wrong Answer',
                    'runtime_ms': res['runtime_ms']
                }
                if not tc.is_hidden:
                    item['input'] = tc.input_data
                    item['expected'] = tc.expected_output
                    item['actual'] = actual
                test_results.append(item)

        avg_runtime = total_runtime / max(1, len(test_results))
        return {
            'success': True,
            'status': overall_status,
            'passed_testcases': passed_count,
            'total_testcases': total_tests,
            'runtime_ms': avg_runtime,
            'memory_kb': max_memory,
            'test_results': test_results,
            'error_message': error_message
        }
