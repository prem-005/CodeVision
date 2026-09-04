import subprocess
import shutil
import sys

def get_compiler_status():
    compilers = {}
    
    # Python
    compilers['python'] = {
        'language': 'Python 3',
        'command': sys.executable,
        'installed': True,
        'version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }

    # JavaScript / Node.js
    node_path = shutil.which('node')
    if node_path:
        try:
            res = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=2)
            version = res.stdout.strip()
            compilers['javascript'] = {'language': 'JavaScript (Node.js)', 'command': node_path, 'installed': True, 'version': version}
        except Exception:
            compilers['javascript'] = {'language': 'JavaScript (Node.js)', 'command': None, 'installed': False, 'version': None, 'message': 'Node.js is not installed or not available in PATH.'}
    else:
        compilers['javascript'] = {'language': 'JavaScript (Node.js)', 'command': None, 'installed': False, 'version': None, 'message': 'Node.js is not installed or not available in PATH.'}

    # Java / Javac
    javac_path = shutil.which('javac')
    java_path = shutil.which('java')
    if javac_path and java_path:
        try:
            res = subprocess.run(['javac', '-version'], capture_output=True, text=True, timeout=2)
            ver = res.stdout.strip() or res.stderr.strip()
            compilers['java'] = {'language': 'Java', 'command': java_path, 'installed': True, 'version': ver}
        except Exception:
            compilers['java'] = {'language': 'Java', 'command': None, 'installed': False, 'version': None, 'message': 'Java is not installed or not available in PATH.'}
    else:
        compilers['java'] = {'language': 'Java', 'command': None, 'installed': False, 'version': None, 'message': 'Java is not installed or not available in PATH.'}

    # C++ (g++ or clang++)
    gpp_path = shutil.which('g++') or shutil.which('clang++')
    if gpp_path:
        try:
            res = subprocess.run([gpp_path, '--version'], capture_output=True, text=True, timeout=2)
            first_line = res.stdout.splitlines()[0] if res.stdout else 'Available'
            compilers['cpp'] = {'language': 'C++ (g++)', 'command': gpp_path, 'installed': True, 'version': first_line}
        except Exception:
            compilers['cpp'] = {'language': 'C++', 'command': None, 'installed': False, 'version': None, 'message': 'C++ compiler (g++) is not installed or not available in PATH.'}
    else:
        compilers['cpp'] = {'language': 'C++', 'command': None, 'installed': False, 'version': None, 'message': 'C++ compiler (g++) is not installed or not available in PATH.'}

    # C (gcc or clang)
    gcc_path = shutil.which('gcc') or shutil.which('clang')
    if gcc_path:
        try:
            res = subprocess.run([gcc_path, '--version'], capture_output=True, text=True, timeout=2)
            first_line = res.stdout.splitlines()[0] if res.stdout else 'Available'
            compilers['c'] = {'language': 'C (gcc)', 'command': gcc_path, 'installed': True, 'version': first_line}
        except Exception:
            compilers['c'] = {'language': 'C', 'command': None, 'installed': False, 'version': None, 'message': 'C compiler (gcc) is not installed or not available in PATH.'}
    else:
        compilers['c'] = {'language': 'C', 'command': None, 'installed': False, 'version': None, 'message': 'C compiler (gcc) is not installed or not available in PATH.'}

    return compilers
