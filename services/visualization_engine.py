import math

class VisualizationEngine:
    # ===== 1. BST VISUALIZATION & LAYOUT ENGINE =====
    @classmethod
    def get_bst_trace(cls, array: list, operation: str = 'build', target_val: int = None) -> dict:
        values = list(array) if array else [45, 12, 89, 34, 67, 23, 90, 11]
        
        class BSTNode:
            def __init__(self, val, node_id):
                self.val = val
                self.id = node_id
                self.left = None
                self.right = None
                self.x = 0
                self.y = 0

        steps = []
        root = None
        node_counter = [0]

        def serialize_tree(curr):
            if not curr:
                return []
            nodes_list = []
            
            def dfs(n, parent_id=None, is_left=True, depth=0):
                if not n:
                    return
                nodes_list.append({
                    'id': n.id,
                    'val': n.val,
                    'parentId': parent_id,
                    'isLeft': is_left,
                    'depth': depth
                })
                dfs(n.left, n.id, True, depth + 1)
                dfs(n.right, n.id, False, depth + 1)

            dfs(curr, None, False, 0)
            return nodes_list

        def insert(curr, val):
            if not curr:
                node_counter[0] += 1
                new_n = BSTNode(val, f"node-{node_counter[0]}")
                steps.append({
                    'step': len(steps) + 1,
                    'tree': serialize_tree(new_n if not root else root),
                    'action': f"Created new node with value {val}",
                    'highlight': [new_n.id],
                    'inserted_val': val
                })
                return new_n

            steps.append({
                'step': len(steps) + 1,
                'tree': serialize_tree(root),
                'action': f"Comparing {val} with current node {curr.val}",
                'highlight': [curr.id],
                'comparing_val': curr.val
            })

            if val < curr.val:
                steps.append({
                    'step': len(steps) + 1,
                    'tree': serialize_tree(root),
                    'action': f"{val} < {curr.val} → Moving to LEFT subtree of {curr.val}",
                    'highlight': [curr.id]
                })
                curr.left = insert(curr.left, val)
            elif val > curr.val:
                steps.append({
                    'step': len(steps) + 1,
                    'tree': serialize_tree(root),
                    'action': f"{val} > {curr.val} → Moving to RIGHT subtree of {curr.val}",
                    'highlight': [curr.id]
                })
                curr.right = insert(curr.right, val)
            else:
                steps.append({
                    'step': len(steps) + 1,
                    'tree': serialize_tree(root),
                    'action': f"{val} already exists in BST → Skipping duplicate",
                    'highlight': [curr.id]
                })
            return curr

        # Build tree step by step
        for v in values:
            if not root:
                node_counter[0] += 1
                root = BSTNode(v, f"node-{node_counter[0]}")
                steps.append({
                    'step': len(steps) + 1,
                    'tree': serialize_tree(root),
                    'action': f"Inserted {v} as the Root node",
                    'highlight': [root.id]
                })
            else:
                root = insert(root, v)

        # Traversals
        inorder_vals = []
        preorder_vals = []
        postorder_vals = []
        levelorder_vals = []

        def get_inorder(n):
            if n:
                get_inorder(n.left)
                inorder_vals.append(n.val)
                get_inorder(n.right)

        def get_preorder(n):
            if n:
                preorder_vals.append(n.val)
                get_preorder(n.left)
                get_preorder(n.right)

        def get_postorder(n):
            if n:
                get_postorder(n.left)
                get_postorder(n.right)
                postorder_vals.append(n.val)

        def get_levelorder(n):
            if not n:
                return
            q = [n]
            while q:
                curr = q.pop(0)
                levelorder_vals.append(curr.val)
                if curr.left:
                    q.append(curr.left)
                if curr.right:
                    q.append(curr.right)

        get_inorder(root)
        get_preorder(root)
        get_postorder(root)
        get_levelorder(root)

        steps.append({
            'step': len(steps) + 1,
            'tree': serialize_tree(root),
            'action': "BST Build Complete!",
            'highlight': [],
            'inorder': inorder_vals,
            'preorder': preorder_vals,
            'postorder': postorder_vals,
            'levelorder': levelorder_vals
        })

        return {
            'algorithm': 'bst',
            'initial_array': values,
            'final_tree': serialize_tree(root),
            'inorder': inorder_vals,
            'preorder': preorder_vals,
            'postorder': postorder_vals,
            'levelorder': levelorder_vals,
            'total_steps': len(steps),
            'steps': steps
        }

    # ===== 2. HEAP VISUALIZATION =====
    @classmethod
    def get_heap_trace(cls, array: list, heap_type: str = 'min') -> dict:
        arr = list(array) if array else [50, 20, 70, 10, 30]
        steps = []
        heap = []
        is_min = (heap_type.lower() == 'min')

        def heapify_up(idx):
            while idx > 0:
                parent = (idx - 1) // 2
                steps.append({
                    'step': len(steps) + 1,
                    'array': list(heap),
                    'highlight': [idx, parent],
                    'action': f"Heapify Up: Comparing element {heap[idx]} at index {idx} with parent {heap[parent]} at index {parent}"
                })
                should_swap = (heap[idx] < heap[parent]) if is_min else (heap[idx] > heap[parent])
                if should_swap:
                    heap[idx], heap[parent] = heap[parent], heap[idx]
                    steps.append({
                        'step': len(steps) + 1,
                        'array': list(heap),
                        'highlight': [idx, parent],
                        'action': f"Swapped {heap[parent]} and {heap[idx]} to maintain {'Min' if is_min else 'Max'} Heap property"
                    })
                    idx = parent
                else:
                    break

        for val in arr:
            heap.append(val)
            steps.append({
                'step': len(steps) + 1,
                'array': list(heap),
                'highlight': [len(heap) - 1],
                'action': f"Pushed {val} to the end of the Heap"
            })
            heapify_up(len(heap) - 1)

        steps.append({
            'step': len(steps) + 1,
            'array': list(heap),
            'highlight': [],
            'action': f"{'Min' if is_min else 'Max'} Heap construction completed!"
        })

        return {
            'algorithm': f"{heap_type}_heap",
            'initial_array': arr,
            'final_heap': heap,
            'total_steps': len(steps),
            'steps': steps
        }

    # ===== 3. GRAPH VISUALIZATION (BFS / DFS / Dijkstra) =====
    @classmethod
    def get_graph_trace(cls, algorithm: str, nodes: list, edges: list, start_node: str = None) -> dict:
        node_list = nodes if nodes else ['A', 'B', 'C', 'D', 'E']
        edge_list = edges if edges else [
            {'from': 'A', 'to': 'B', 'weight': 4},
            {'from': 'A', 'to': 'C', 'weight': 2},
            {'from': 'B', 'to': 'D', 'weight': 5},
            {'from': 'C', 'to': 'D', 'weight': 1},
            {'from': 'D', 'to': 'E', 'weight': 3}
        ]
        start = start_node if start_node in node_list else node_list[0]
        algo = algorithm.lower()
        steps = []

        adj = {n: [] for n in node_list}
        for e in edge_list:
            u, v, w = e.get('from'), e.get('to'), e.get('weight', 1)
            if u in adj and v in adj:
                adj[u].append((v, w))
                adj[v].append((u, w))

        if 'bfs' in algo:
            visited = set()
            queue = [start]
            visited.add(start)

            while queue:
                curr = queue.pop(0)
                steps.append({
                    'step': len(steps) + 1,
                    'current': curr,
                    'queue': list(queue),
                    'visited': list(visited),
                    'action': f"BFS: Dequeued node {curr}. Visiting neighbors."
                })
                for neighbor, _ in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
                        steps.append({
                            'step': len(steps) + 1,
                            'current': neighbor,
                            'queue': list(queue),
                            'visited': list(visited),
                            'action': f"Discovered neighbor {neighbor}. Added to Queue."
                        })

        elif 'dfs' in algo:
            visited = set()
            stack = [start]

            while stack:
                curr = stack.pop()
                if curr not in visited:
                    visited.add(curr)
                    steps.append({
                        'step': len(steps) + 1,
                        'current': curr,
                        'stack': list(stack),
                        'visited': list(visited),
                        'action': f"DFS: Popped node {curr} from stack. Marking as Visited."
                    })
                    for neighbor, _ in reversed(adj[curr]):
                        if neighbor not in visited:
                            stack.append(neighbor)

        elif 'dijkstra' in algo:
            import heapq
            dist = {n: float('inf') for n in node_list}
            dist[start] = 0
            pq = [(0, start)]
            visited = set()

            while pq:
                d, curr = heapq.heappop(pq)
                if curr in visited:
                    continue
                visited.add(curr)

                steps.append({
                    'step': len(steps) + 1,
                    'current': curr,
                    'distances': {k: (v if v != float('inf') else '∞') for k, v in dist.items()},
                    'visited': list(visited),
                    'action': f"Dijkstra: Extracted node {curr} with minimum distance {d}."
                })

                for neighbor, w in adj[curr]:
                    if dist[curr] + w < dist[neighbor]:
                        dist[neighbor] = dist[curr] + w
                        heapq.heappush(pq, (dist[neighbor], neighbor))
                        steps.append({
                            'step': len(steps) + 1,
                            'current': neighbor,
                            'distances': {k: (v if v != float('inf') else '∞') for k, v in dist.items()},
                            'visited': list(visited),
                            'action': f"Relaxed edge ({curr} → {neighbor}): updated dist[{neighbor}] = {dist[neighbor]}."
                        })

        return {
            'algorithm': algorithm,
            'nodes': node_list,
            'edges': edge_list,
            'start_node': start,
            'total_steps': len(steps),
            'steps': steps
        }

    # ===== 4. SORTING VISUALIZATION ENGINE =====
    @classmethod
    def get_sorting_trace(cls, algorithm: str, array: list) -> dict:
        arr = list(array) if array else [64, 34, 25, 12, 22, 11, 90]
        algo = algorithm.lower().replace(' ', '_').replace('-', '_')
        steps = []
        comparisons = 0
        swaps = 0

        if algo in ['bubble_sort', 'bubble']:
            n = len(arr)
            for i in range(n):
                for j in range(0, n - i - 1):
                    comparisons += 1
                    steps.append({
                        'step': len(steps) + 1,
                        'array': list(arr),
                        'highlight': [j, j + 1],
                        'sorted': list(range(n - i, n)),
                        'action': f"Comparing arr[{j}]={arr[j]} and arr[{j+1}]={arr[j+1]}",
                        'comparisons': comparisons,
                        'swaps': swaps
                    })
                    if arr[j] > arr[j + 1]:
                        arr[j], arr[j + 1] = arr[j + 1], arr[j]
                        swaps += 1
                        steps.append({
                            'step': len(steps) + 1,
                            'array': list(arr),
                            'highlight': [j, j + 1],
                            'sorted': list(range(n - i, n)),
                            'action': f"Swapped arr[{j}] and arr[{j+1}]",
                            'comparisons': comparisons,
                            'swaps': swaps
                        })
            steps.append({
                'step': len(steps) + 1,
                'array': list(arr),
                'highlight': [],
                'sorted': list(range(len(arr))),
                'action': "Array is completely sorted!",
                'comparisons': comparisons,
                'swaps': swaps
            })

        elif algo in ['selection_sort', 'selection']:
            n = len(arr)
            for i in range(n):
                min_idx = i
                for j in range(i + 1, n):
                    comparisons += 1
                    steps.append({
                        'step': len(steps) + 1,
                        'array': list(arr),
                        'highlight': [min_idx, j],
                        'sorted': list(range(i)),
                        'action': f"Finding minimum: comparing arr[{min_idx}]={arr[min_idx]} with arr[{j}]={arr[j]}",
                        'comparisons': comparisons,
                        'swaps': swaps
                    })
                    if arr[j] < arr[min_idx]:
                        min_idx = j
                if min_idx != i:
                    arr[i], arr[min_idx] = arr[min_idx], arr[i]
                    swaps += 1
                    steps.append({
                        'step': len(steps) + 1,
                        'array': list(arr),
                        'highlight': [i, min_idx],
                        'sorted': list(range(i + 1)),
                        'action': f"Placed minimum element {arr[i]} at index {i}",
                        'comparisons': comparisons,
                        'swaps': swaps
                    })
            steps.append({
                'step': len(steps) + 1,
                'array': list(arr),
                'highlight': [],
                'sorted': list(range(len(arr))),
                'action': "Selection Sort completed!",
                'comparisons': comparisons,
                'swaps': swaps
            })

        elif algo in ['insertion_sort', 'insertion']:
            n = len(arr)
            for i in range(1, n):
                key = arr[i]
                j = i - 1
                while j >= 0:
                    comparisons += 1
                    steps.append({
                        'step': len(steps) + 1,
                        'array': list(arr),
                        'highlight': [j, j + 1],
                        'sorted': list(range(i)),
                        'action': f"Comparing key={key} with arr[{j}]={arr[j]}",
                        'comparisons': comparisons,
                        'swaps': swaps
                    })
                    if arr[j] > key:
                        arr[j + 1] = arr[j]
                        swaps += 1
                        j -= 1
                    else:
                        break
                arr[j + 1] = key
                steps.append({
                    'step': len(steps) + 1,
                    'array': list(arr),
                    'highlight': [j + 1],
                    'sorted': list(range(i + 1)),
                    'action': f"Inserted key={key} at index {j+1}",
                    'comparisons': comparisons,
                    'swaps': swaps
                })
            steps.append({
                'step': len(steps) + 1,
                'array': list(arr),
                'highlight': [],
                'sorted': list(range(len(arr))),
                'action': "Insertion Sort completed!",
                'comparisons': comparisons,
                'swaps': swaps
            })

        elif algo in ['quick_sort', 'quick']:
            def quicksort_rec(low, high):
                nonlocal comparisons, swaps
                if low < high:
                    pivot = arr[high]
                    i = low - 1
                    for j in range(low, high):
                        comparisons += 1
                        steps.append({
                            'step': len(steps) + 1,
                            'array': list(arr),
                            'highlight': [j, high],
                            'sorted': [],
                            'action': f"QuickSort: Partitioning around pivot arr[{high}]={pivot}",
                            'comparisons': comparisons,
                            'swaps': swaps
                        })
                        if arr[j] < pivot:
                            i += 1
                            arr[i], arr[j] = arr[j], arr[i]
                            swaps += 1
                    arr[i + 1], arr[high] = arr[high], arr[i + 1]
                    swaps += 1
                    pi = i + 1
                    steps.append({
                        'step': len(steps) + 1,
                        'array': list(arr),
                        'highlight': [pi],
                        'sorted': [pi],
                        'action': f"Pivot {pivot} placed at final index {pi}",
                        'comparisons': comparisons,
                        'swaps': swaps
                    })
                    quicksort_rec(low, pi - 1)
                    quicksort_rec(pi + 1, high)

            quicksort_rec(0, len(arr) - 1)
            steps.append({
                'step': len(steps) + 1,
                'array': list(arr),
                'highlight': [],
                'sorted': list(range(len(arr))),
                'action': "Quick Sort completed!",
                'comparisons': comparisons,
                'swaps': swaps
            })
        elif algo in ['merge_sort', 'merge']:
            def merge_sort_rec(low, high):
                nonlocal comparisons
                if low >= high:
                    return
                middle = (low + high) // 2
                merge_sort_rec(low, middle)
                merge_sort_rec(middle + 1, high)
                left = arr[low:middle + 1]
                right = arr[middle + 1:high + 1]
                left_idx = right_idx = 0
                write_idx = low
                while left_idx < len(left) and right_idx < len(right):
                    comparisons += 1
                    if left[left_idx] <= right[right_idx]:
                        arr[write_idx] = left[left_idx]
                        left_idx += 1
                    else:
                        arr[write_idx] = right[right_idx]
                        right_idx += 1
                    steps.append({
                        'step': len(steps) + 1,
                        'array': list(arr),
                        'highlight': [write_idx],
                        'sorted': [],
                        'action': f"Merging range {low}-{high} at index {write_idx}",
                        'comparisons': comparisons,
                        'swaps': swaps
                    })
                    write_idx += 1
                remainder = left[left_idx:] + right[right_idx:]
                for value in remainder:
                    arr[write_idx] = value
                    steps.append({
                        'step': len(steps) + 1,
                        'array': list(arr),
                        'highlight': [write_idx],
                        'sorted': [],
                        'action': f"Writing {value} into merged range",
                        'comparisons': comparisons,
                        'swaps': swaps
                    })
                    write_idx += 1

            merge_sort_rec(0, len(arr) - 1)
            steps.append({
                'step': len(steps) + 1,
                'array': list(arr),
                'highlight': [],
                'sorted': list(range(len(arr))),
                'action': "Merge Sort completed!",
                'comparisons': comparisons,
                'swaps': swaps
            })
        else:
            arr.sort()
            steps.append({
                'step': 1,
                'array': list(arr),
                'highlight': [],
                'sorted': list(range(len(arr))),
                'action': f"{algorithm} sorted state",
                'comparisons': len(arr),
                'swaps': len(arr) // 2
            })

        return {
            'algorithm': algorithm,
            'initial_array': array,
            'final_array': arr,
            'total_steps': len(steps),
            'steps': steps,
            'time_complexity': 'O(N log N)' if any(name in algo for name in ['quick', 'merge', 'heap']) else 'O(N²)',
            'space_complexity': 'O(1)' if any(name in algo for name in ['bubble', 'selection', 'insertion', 'heap']) else 'O(N)'
        }

    # ===== 5. SEARCHING VISUALIZATION ENGINE =====
    @classmethod
    def get_searching_trace(cls, algorithm: str, array: list, target: float) -> dict:
        arr = list(array) if array else [10, 20, 30, 40, 50, 60, 70, 80, 90]
        algo = algorithm.lower().replace(' ', '_')
        steps = []
        found = False
        target_val = float(target)

        if 'binary' in algo:
            arr.sort()
            low = 0
            high = len(arr) - 1
            while low <= high:
                mid = (low + high) // 2
                is_match = (arr[mid] == target_val)
                steps.append({
                    'step': len(steps) + 1,
                    'array': list(arr),
                    'range': [low, high],
                    'low': low,
                    'mid': mid,
                    'high': high,
                    'current': mid,
                    'target': target_val,
                    'action': f"Binary Search: low={low}, mid={mid} (val={arr[mid]}), high={high}. Target={target_val}.",
                    'found': is_match
                })
                if is_match:
                    found = True
                    break
                elif arr[mid] < target_val:
                    low = mid + 1
                else:
                    high = mid - 1
        else:
            for i, val in enumerate(arr):
                is_match = (val == target_val)
                steps.append({
                    'step': len(steps) + 1,
                    'array': list(arr),
                    'current': i,
                    'target': target_val,
                    'action': f"Linear Search: Checking index {i} (val={val}) against target {target_val}",
                    'found': is_match
                })
                if is_match:
                    found = True
                    break

        return {
            'algorithm': algorithm,
            'array': arr,
            'target': target_val,
            'found': found,
            'total_steps': len(steps),
            'steps': steps,
            'time_complexity': 'O(log N)' if 'binary' in algo else 'O(N)'
        }
