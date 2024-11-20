import heapq
from anytree import Node as TreeNode, RenderTree
import matplotlib.pyplot as plt
import networkx as nx

class Job:
    def __init__(self, id, processing_time, release_date, inventory_change):
        self.id = id
        self.processing_time = processing_time
        self.release_date = release_date
        self.inventory_change = inventory_change

class Node:
    def __init__(self, time, inventory, job_sequence, parent=None):
        self.time = time
        self.inventory = inventory
        self.job_sequence = job_sequence
        self.parent = parent

    def __lt__(self, other):
        return self.time < other.time  # For priority queue sorting

def calculate_lower_bound(jobs, current_time, inventory, remaining_jobs):
    lb = current_time  # Start with the current time
    for job in remaining_jobs:
        lb = max(lb, job.release_date) + job.processing_time
    return lb

def branch_and_bound(jobs, I0, IC):
    n = len(jobs)
    best_makespan = float('inf')
    best_sequence = []

    # Min-heap for exploring nodes with lower bounds first
    min_heap = []
    initial_node = Node(0, I0, [])
    heapq.heappush(min_heap, initial_node)

    # Store tree nodes for plotting
    tree_nodes = {}

    while min_heap:
        current_node = heapq.heappop(min_heap)

        # Create a tree node
        if current_node.job_sequence:
            tree_parent = tree_nodes[tuple(current_node.job_sequence[:-1])]
            tree_node = TreeNode(f"Seq: {current_node.job_sequence}, Time: {current_node.time}, Inventory: {current_node.inventory}", parent=tree_parent)
        else:
            tree_node = TreeNode(f"Root: Time: {current_node.time}, Inventory: {current_node.inventory}")
        
        tree_nodes[tuple(current_node.job_sequence)] = tree_node

        # If the sequence length is equal to the number of jobs, check makespan
        if len(current_node.job_sequence) == n:
            if current_node.time < best_makespan:
                best_makespan = current_node.time
                best_sequence = current_node.job_sequence
            continue

        for j in range(n):
            if j not in current_node.job_sequence:  # If job j is not yet in the sequence
                job = jobs[j]
                # Calculate new state
                time_after_release = max(current_node.time, job.release_date)
                new_inventory = current_node.inventory + job.inventory_change

                # Check inventory bounds
                if 0 <= new_inventory <= IC:
                    new_sequence = current_node.job_sequence + [job.id]
                    new_time = time_after_release + job.processing_time

                    # Calculate lower bound for the new state
                    remaining_jobs = [jobs[k] for k in range(n) if k not in new_sequence]
                    lb = calculate_lower_bound(jobs, new_time, new_inventory, remaining_jobs)

                    # If the lower bound is less than the best makespan, explore further
                    if lb < best_makespan:
                        new_node = Node(new_time, new_inventory, new_sequence)
                        heapq.heappush(min_heap, new_node)

    # Check if the solution is early optimal
    is_early_optimal = check_early_optimal(jobs, best_sequence)

    return best_makespan, best_sequence, is_early_optimal, tree_nodes

def check_early_optimal(jobs, sequence):
    current_time = 0
    for job_id in sequence:
        job = jobs[job_id]
        current_time = max(current_time, job.release_date) + job.processing_time
    
    earliest_possible_time = 0
    for job in jobs:
        earliest_possible_time = max(earliest_possible_time, job.release_date)
        earliest_possible_time += job.processing_time
    
    return current_time == earliest_possible_time

def plot_branch_and_bound_tree(tree_nodes, optimal_sequence):
    # Visualize the tree
    for pre, fill, node in RenderTree(tree_nodes[()]):
        if 'Seq:' in node.name and f"{optimal_sequence}" in node.name:
            print(f"{pre}{node.name} <-- Optimal Solution")
        else:
            print(f"{pre}{node.name}")

# Example usage for branch-and-bound approach
if __name__ == "__main__":
    # Test example parameters
    n = 4  # Number of jobs
    processing_times = [3, 2, 4, 1]  # Processing time for each job
    release_dates = [0, 1, 3, 6]  # Release date for each job
    inventory_modifications = [1, -1, 0, 2]  # Inventory modification for each job
    I0 = 2  # Initial inventory level
    IC = 5  # Inventory capacity

    # Define jobs based on the parameters
    jobs = [Job(i, processing_times[i], release_dates[i], inventory_modifications[i]) for i in range(n)]
    
    optimal_makespan, optimal_sequence, is_early_optimal, tree_nodes = branch_and_bound(jobs, I0, IC)
    
    print("Optimal Makespan:", optimal_makespan)
    print("Optimal Job Sequence:", optimal_sequence)
    print("Is Early Optimal Solution:", is_early_optimal)

    # Plot the branch and bound tree
    plot_branch_and_bound_tree(tree_nodes, optimal_sequence)
