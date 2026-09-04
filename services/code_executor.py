import os
import sys
import time
import tempfile
import subprocess
import shutil

class CodeExecutor:
    TIMEOUT_SECONDS = 5.0
    MAX_OUTPUT_BYTES = 50000

    @classmethod
    def execute(cls, language: str, code: str, stdin_data: str = "") -> dict:
        language = (language or "").lower().strip()
        start_time = time.perf_counter()

        temp_dir = tempfile.mkdtemp(prefix="cv_run_")
        try:
            if language in ['python', 'py', 'python3']:
                return cls._run_python(temp_dir, code, stdin_data, start_time)
            elif language in ['javascript', 'js', 'node']:
                return cls._run_javascript(temp_dir, code, stdin_data, start_time)
            elif language in ['java']:
                return cls._run_java(temp_dir, code, stdin_data, start_time)
            elif language in ['cpp', 'c++']:
                return cls._run_cpp(temp_dir, code, stdin_data, start_time)
            elif language in ['c']:
                return cls._run_c(temp_dir, code, stdin_data, start_time)
            else:
                return {
                    'status': 'Error',
                    'stdout': '',
                    'stderr': f'Unsupported language: {language}',
                    'runtime_ms': 0.0,
                    'memory_kb': 0.0,
                    'exit_code': 1
                }
        finally:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    @classmethod
    def _run_python(cls, temp_dir, code, stdin_data, start_time):
        file_path = os.path.join(temp_dir, 'solution.py')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)

        try:
            proc = subprocess.Popen(
                [sys.executable, file_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=temp_dir
            )
            stdout, stderr = proc.communicate(input=stdin_data, timeout=cls.TIMEOUT_SECONDS)
            runtime_ms = (time.perf_counter() - start_time) * 1000.0

            if proc.returncode != 0:
                return {
                    'status': 'Runtime Error',
                    'stdout': stdout[:cls.MAX_OUTPUT_BYTES],
                    'stderr': stderr[:cls.MAX_OUTPUT_BYTES],
                    'runtime_ms': runtime_ms,
                    'memory_kb': 12000.0,
                    'exit_code': proc.returncode
                }
            return {
                'status': 'Success',
                'stdout': stdout[:cls.MAX_OUTPUT_BYTES],
                'stderr': stderr[:cls.MAX_OUTPUT_BYTES],
                'runtime_ms': runtime_ms,
                'memory_kb': 12000.0,
                'exit_code': 0
            }
        except subprocess.TimeoutExpired:
            proc.kill()
            return {
                'status': 'Time Limit Exceeded',
                'stdout': '',
                'stderr': f'Execution timed out after {cls.TIMEOUT_SECONDS}s',
                'runtime_ms': cls.TIMEOUT_SECONDS * 1000.0,
                'memory_kb': 0.0,
                'exit_code': 124
            }
        except Exception as e:
            return {
                'status': 'Runtime Error',
                'stdout': '',
                'stderr': str(e),
                'runtime_ms': (time.perf_counter() - start_time) * 1000.0,
                'memory_kb': 0.0,
                'exit_code': 1
            }

    @classmethod
    def _run_javascript(cls, temp_dir, code, stdin_data, start_time):
        node_path = shutil.which('node')
        if not node_path:
            return {'status': 'Error', 'stdout': '', 'stderr': 'Node.js is not installed or not available in PATH.', 'runtime_ms': 0.0, 'memory_kb': 0.0, 'exit_code': 1}

        file_path = os.path.join(temp_dir, 'solution.js')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)

        try:
            proc = subprocess.Popen([node_path, file_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=temp_dir)
            stdout, stderr = proc.communicate(input=stdin_data, timeout=cls.TIMEOUT_SECONDS)
            runtime_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                'status': 'Success' if proc.returncode == 0 else 'Runtime Error',
                'stdout': stdout[:cls.MAX_OUTPUT_BYTES],
                'stderr': stderr[:cls.MAX_OUTPUT_BYTES],
                'runtime_ms': runtime_ms,
                'memory_kb': 25000.0,
                'exit_code': proc.returncode
            }
        except subprocess.TimeoutExpired:
            proc.kill()
            return {'status': 'Time Limit Exceeded', 'stdout': '', 'stderr': 'Execution timed out', 'runtime_ms': cls.TIMEOUT_SECONDS * 1000.0, 'memory_kb': 0.0, 'exit_code': 124}

    @classmethod
    def _run_java(cls, temp_dir, code, stdin_data, start_time):
        javac_path = shutil.which('javac')
        java_path = shutil.which('java')
        if not javac_path or not java_path:
            return {'status': 'Error', 'stdout': '', 'stderr': 'Java is not installed or not available in PATH.', 'runtime_ms': 0.0, 'memory_kb': 0.0, 'exit_code': 1}

        import re
        match = re.search(r'public\s+class\s+([A-Za-z0-9_]+)', code)
        class_name = match.group(1) if match else 'Solution'
        file_path = os.path.join(temp_dir, f'{class_name}.java')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)

        compile_proc = subprocess.run([javac_path, file_path], capture_output=True, text=True, cwd=temp_dir, timeout=8.0)
        if compile_proc.returncode != 0:
            return {'status': 'Compilation Error', 'stdout': '', 'stderr': compile_proc.stderr[:cls.MAX_OUTPUT_BYTES], 'runtime_ms': 0.0, 'memory_kb': 0.0, 'exit_code': compile_proc.returncode}

        try:
            run_proc = subprocess.Popen([java_path, class_name], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=temp_dir)
            stdout, stderr = run_proc.communicate(input=stdin_data, timeout=cls.TIMEOUT_SECONDS)
            runtime_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                'status': 'Success' if run_proc.returncode == 0 else 'Runtime Error',
                'stdout': stdout[:cls.MAX_OUTPUT_BYTES],
                'stderr': stderr[:cls.MAX_OUTPUT_BYTES],
                'runtime_ms': runtime_ms,
                'memory_kb': 35000.0,
                'exit_code': run_proc.returncode
            }
        except subprocess.TimeoutExpired:
            run_proc.kill()
            return {'status': 'Time Limit Exceeded', 'stdout': '', 'stderr': 'Execution timed out', 'runtime_ms': cls.TIMEOUT_SECONDS * 1000.0, 'memory_kb': 0.0, 'exit_code': 124}

    @classmethod
    def _run_cpp(cls, temp_dir, code, stdin_data, start_time):
        gpp_path = shutil.which('g++') or shutil.which('clang++')
        if not gpp_path:
            return {'status': 'Error', 'stdout': '', 'stderr': 'C++ compiler (g++) is not installed or not available in PATH.', 'runtime_ms': 0.0, 'memory_kb': 0.0, 'exit_code': 1}

        src_path = os.path.join(temp_dir, 'solution.cpp')
        exe_path = os.path.join(temp_dir, 'solution.exe' if os.name == 'nt' else 'solution.out')
        with open(src_path, 'w', encoding='utf-8') as f:
            f.write(code)

        compile_proc = subprocess.run([gpp_path, '-O2', src_path, '-o', exe_path], capture_output=True, text=True, cwd=temp_dir, timeout=8.0)
        if compile_proc.returncode != 0:
            return {'status': 'Compilation Error', 'stdout': '', 'stderr': compile_proc.stderr[:cls.MAX_OUTPUT_BYTES], 'runtime_ms': 0.0, 'memory_kb': 0.0, 'exit_code': compile_proc.returncode}

        try:
            run_proc = subprocess.Popen([exe_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=temp_dir)
            stdout, stderr = run_proc.communicate(input=stdin_data, timeout=cls.TIMEOUT_SECONDS)
            runtime_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                'status': 'Success' if run_proc.returncode == 0 else 'Runtime Error',
                'stdout': stdout[:cls.MAX_OUTPUT_BYTES],
                'stderr': stderr[:cls.MAX_OUTPUT_BYTES],
                'runtime_ms': runtime_ms,
                'memory_kb': 8000.0,
                'exit_code': run_proc.returncode
            }
        except subprocess.TimeoutExpired:
            run_proc.kill()
            return {'status': 'Time Limit Exceeded', 'stdout': '', 'stderr': 'Execution timed out', 'runtime_ms': cls.TIMEOUT_SECONDS * 1000.0, 'memory_kb': 0.0, 'exit_code': 124}

    @classmethod
    def _run_c(cls, temp_dir, code, stdin_data, start_time):
        gcc_path = shutil.which('gcc') or shutil.which('clang')
        if not gcc_path:
            return {'status': 'Error', 'stdout': '', 'stderr': 'C compiler (gcc) is not installed or not available in PATH.', 'runtime_ms': 0.0, 'memory_kb': 0.0, 'exit_code': 1}

        src_path = os.path.join(temp_dir, 'solution.c')
        exe_path = os.path.join(temp_dir, 'solution.exe' if os.name == 'nt' else 'solution.out')
        with open(src_path, 'w', encoding='utf-8') as f:
            f.write(code)

        compile_proc = subprocess.run([gcc_path, '-O2', src_path, '-o', exe_path], capture_output=True, text=True, cwd=temp_dir, timeout=8.0)
        if compile_proc.returncode != 0:
            return {'status': 'Compilation Error', 'stdout': '', 'stderr': compile_proc.stderr[:cls.MAX_OUTPUT_BYTES], 'runtime_ms': 0.0, 'memory_kb': 0.0, 'exit_code': compile_proc.returncode}

        try:
            run_proc = subprocess.Popen([exe_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=temp_dir)
            stdout, stderr = run_proc.communicate(input=stdin_data, timeout=cls.TIMEOUT_SECONDS)
            runtime_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                'status': 'Success' if run_proc.returncode == 0 else 'Runtime Error',
                'stdout': stdout[:cls.MAX_OUTPUT_BYTES],
                'stderr': stderr[:cls.MAX_OUTPUT_BYTES],
                'runtime_ms': runtime_ms,
                'memory_kb': 5000.0,
                'exit_code': run_proc.returncode
            }
        except subprocess.TimeoutExpired:
            run_proc.kill()
            return {'status': 'Time Limit Exceeded', 'stdout': '', 'stderr': 'Execution timed out', 'runtime_ms': cls.TIMEOUT_SECONDS * 1000.0, 'memory_kb': 0.0, 'exit_code': 124}
