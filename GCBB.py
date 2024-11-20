from typing import List, Tuple
import heapq

class Job:
    def __init__(self, job_id, processing_time, release_date, inventory_change):
        self.job_id = job_id
        self.processing_time = processing_time
        self.release_date = release_date
        self.inventory_change = inventory_change

class Node:
    def __init__(self, blocks: List[List[Job]], completion_time: int, inventory_level: int):
        self.blocks = blocks
        self.completion_time = completion_time
        self.inventory_level = inventory_level
        self.lower_bound = float('inf')
    
    def __lt__(self, other):
        return self.lower_bound < other.lower_bound

    def display_blocks(self):
        return [[job.job_id for job in block] for block in self.blocks]

def branch_and_bound(jobs: List[Job], inventory_capacity: int, initial_inventory: int) -> Tuple[int, List[List[Job]]]:
    best_makespan = float('inf')
    best_solution = []
    
    def calculate_lower_bound(node: Node) -> int:
        remaining_jobs = [job for job in jobs if not any(job in block for block in node.blocks)]
        min_release_time = min((job.release_date for job in remaining_jobs), default=0)
        total_processing_time = sum(job.processing_time for job in remaining_jobs)
        lb = max(node.completion_time, min_release_time) + total_processing_time
        return lb

    def calculate_upper_bound(node: Node) -> int:
        if sum(len(block) for block in node.blocks) == len(jobs):
            return node.completion_time
        
        remaining_jobs = [job for job in jobs if not any(job in block for block in node.blocks)]
        
        if remaining_jobs and max(job.release_date for job in remaining_jobs) <= node.completion_time:
            feasible_completion = node.completion_time
            for job in remaining_jobs:
                feasible_completion += job.processing_time
            return feasible_completion
        
        sorted_jobs = sorted(remaining_jobs, key=lambda j: j.release_date)
        feasible_completion = node.completion_time
        for job in sorted_jobs:
            feasible_completion = max(feasible_completion, job.release_date) + job.processing_time
        return feasible_completion

    def is_feasible(node: Node, job: Job, add_to_existing_block=True) -> bool:
        if add_to_existing_block:
            current_block = node.blocks[-1] if node.blocks else []
            last_job_in_block = current_block[-1] if current_block else None
            if last_job_in_block and job.release_date > node.completion_time:
                return False
            new_inventory = node.inventory_level + job.inventory_change
            if not (0 <= new_inventory <= inventory_capacity):
                return False
        else:
            if job.release_date <= node.completion_time:
                return False
            if not (0 <= node.inventory_level + job.inventory_change <= inventory_capacity):
                return False
        return True

    def create_child_node(parent: Node, job: Job, new_block=False) -> Node:
        new_blocks = [block[:] for block in parent.blocks]
        if new_block:
            new_blocks.append([job])
        else:
            new_blocks[-1].append(job)
        
        new_completion_time = max(parent.completion_time, job.release_date) + job.processing_time
        new_inventory_level = parent.inventory_level + job.inventory_change
        child_node = Node(new_blocks, new_completion_time, new_inventory_level)
        child_node.lower_bound = calculate_lower_bound(child_node)
        return child_node

    root_node = Node(blocks=[], completion_time=0, inventory_level=initial_inventory)
    root_node.lower_bound = calculate_lower_bound(root_node)
    nodes_to_explore = [root_node]
    heapq.heapify(nodes_to_explore)
    
    print("Starting Branch and Bound Search")

    while nodes_to_explore:
        current_node = heapq.heappop(nodes_to_explore)
        current_upper_bound = calculate_upper_bound(current_node)

        # Display debug output for the current node
        print(f"\n\nNode Blocks: {current_node.display_blocks()}")
        print(f"Lower Bound: {current_node.lower_bound}\nUpper Bound: {current_upper_bound}")

        # Prune based on lower bound
        if current_node.lower_bound >= best_makespan:
            print(f"Node pruned due to lower bound >= best makespan ({current_node.lower_bound} >= {best_makespan}).")
            continue

        # Prune based on upper bound
        if current_upper_bound >= best_makespan:
            print(f"Node pruned due to upper bound >= best makespan ({current_upper_bound} >= {best_makespan}).")
            continue
        
        # Check if current node represents a complete solution
        if sum(len(block) for block in current_node.blocks) == len(jobs):
            if current_node.completion_time < best_makespan:
                best_makespan = current_node.completion_time
                best_solution = current_node.blocks
                print(f"New best makespan found: {best_makespan}")
            continue

        # Generate child nodes
        for job in jobs:
            if not any(job in block for block in current_node.blocks):
                if current_node.blocks and is_feasible(current_node, job, add_to_existing_block=True):
                    child_node = create_child_node(current_node, job, new_block=False)
                    if child_node.lower_bound < best_makespan:
                        heapq.heappush(nodes_to_explore, child_node)
                
                if is_feasible(current_node, job, add_to_existing_block=False):
                    child_node = create_child_node(current_node, job, new_block=True)
                    if child_node.lower_bound < best_makespan:
                        heapq.heappush(nodes_to_explore, child_node)

    return best_makespan, best_solution

# Example usage
jobs = [
    Job(job_id=1, processing_time=1, release_date=7, inventory_change=-1),
    Job(job_id=2, processing_time=1, release_date=1, inventory_change=-4),
    Job(job_id=3, processing_time=8, release_date=4, inventory_change=-2),
    Job(job_id=4, processing_time=4, release_date=18, inventory_change=5),
    Job(job_id=5, processing_time=8, release_date=14, inventory_change=-2),
]

inventory_capacity = 8
initial_inventory = 6

optimal_makespan, optimal_sequence = branch_and_bound(jobs, inventory_capacity, initial_inventory)

# Print the results
print("Optimal makespan:", optimal_makespan)
print("Optimal job sequence in blocks:", [[job.job_id for job in block] for block in optimal_sequence])
