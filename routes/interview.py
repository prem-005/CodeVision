import json
import os
from flask import Blueprint, render_template, request, jsonify
from models import Problem

interview_bp = Blueprint('interview', __name__)

@interview_bp.route('/interview')
def interview_page():
    return render_template('interview.html')


@interview_bp.route('/companies')
def companies_page():
    return render_template('companies.html')


@interview_bp.route('/learning-path')
def learning_path_page():
    return render_template('learning_path.html')


@interview_bp.route('/api/companies')
def api_get_companies():
    comp_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'companies.json')
    if os.path.exists(comp_file):
        with open(comp_file, 'r', encoding='utf-8') as f:
            return jsonify({'success': True, 'companies': json.load(f)})
    return jsonify({'success': True, 'companies': []})


@interview_bp.route('/api/interview/quiz', methods=['GET'])
def api_get_interview_quiz():
    category = request.args.get('category', 'DSA')
    
    # Curated quiz questions for technical placement prep
    quizzes = {
        'DSA': [
            {'q': 'What is the time complexity of searching in a balanced BST?', 'options': ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)'], 'answer': 1, 'explanation': 'Balanced BSTs divide search space by half at each step.'},
            {'q': 'Which data structure is optimal for implementing LRU Cache?', 'options': ['Array + Queue', 'Hash Map + Doubly Linked List', 'Binary Heap', 'Stack'], 'answer': 1, 'explanation': 'Hash map allows O(1) key lookup, Doubly Linked List allows O(1) node removal and insertion.'},
            {'q': 'What is the worst case time complexity of QuickSort?', 'options': ['O(n log n)', 'O(n)', 'O(n²)', 'O(log n)'], 'answer': 2, 'explanation': 'When the chosen pivot is always the extreme element, recursion depth reaches n resulting in O(n²).'}
        ],
        'OOP': [
            {'q': 'Which OOP principle is demonstrated by method overloading and overriding?', 'options': ['Encapsulation', 'Polymorphism', 'Abstraction', 'Inheritance'], 'answer': 1, 'explanation': 'Polymorphism allows objects to take multiple forms (compile-time overloading, runtime overriding).'},
            {'q': 'What is the primary difference between an Interface and an Abstract Class in Java/C++?', 'options': ['Abstract classes cannot have methods', 'Interfaces cannot store instance states/fields', 'Interfaces are slower', 'Abstract classes cannot be inherited'], 'answer': 1, 'explanation': 'Interfaces define contracts without instance state, while abstract classes can hold state and default implementations.'}
        ],
        'DBMS': [
            {'q': 'Which Normal Form eliminates transitive functional dependencies?', 'options': ['1NF', '2NF', '3NF', 'BCNF'], 'answer': 2, 'explanation': '3NF requires 2NF and no non-prime attribute depends transitively on the primary key.'},
            {'q': 'What does the ACID property Isolation ensure?', 'options': ['Data is permanently stored', 'Concurrent transactions execute as if sequential', 'Total balance is maintained', 'Transactions are all-or-nothing'], 'answer': 1, 'explanation': 'Isolation guarantees intermediate states are invisible to concurrent transactions.'}
        ],
        'OS': [
            {'q': 'What condition is NOT required for a deadlock to occur?', 'options': ['Mutual Exclusion', 'Hold and Wait', 'Preemption Allowed', 'Circular Wait'], 'answer': 2, 'explanation': 'Deadlocks require No Preemption; allowing preemption prevents deadlocks.'}
        ],
        'CN': [
            {'q': 'Which transport protocol guarantees ordered, reliable packet delivery with flow control?', 'options': ['UDP', 'TCP', 'ICMP', 'DNS'], 'answer': 1, 'explanation': 'TCP provides connection-oriented reliability with sequence numbers and acknowledgements.'}
        ]
    }
    
    return jsonify({'success': True, 'category': category, 'questions': quizzes.get(category, quizzes['DSA'])})
