"""
This module contains the scheduling algorithms used in the scheduling API.

It provides implementations for both Least Deadline First (LDF) and Earliest Deadline First (EDF) scheduling strategies, applicable in single-core and multi-core processor environments. Functions within are designed to be called with specific application and platform data structures.

Functions:
- ldf_singlecore: Schedules tasks on a single-core processor using LDF.
- edf_singlecore: Schedules tasks on a single-core processor using EDF.
- rms_singlecore: Schedules tasks on a single-core processor using RMS.
- ll_singlecore: Schedules tasks on a single-core processor using LL.
- ldf_multicore: Schedules tasks on multiple cores using LDF.
- edf_multicore: Schedules tasks on multiple cores using EDF.
"""

__author__ = "Priya Nagar"
__version__ = "1.0.0"


import networkx as nx
from collections import defaultdict, deque

example_schedule = [
    {
        "task_id": 3,
        "node_id": 0,
        "end_time": 20,
        "deadline": 256,
        "start_time": 0,
    },
    {
        "task_id": 2,
        "node_id": 0,
        "end_time": 40,
        "deadline": 300,
        "start_time": 20,
    },
    {
        "task_id": 1,
        "node_id": 0,
        "end_time": 60,
        "deadline": 250,
        "start_time": 40,
    },
    {
        "task_id": 0,
        "node_id": 0,
        "end_time": 80,
        "deadline": 250,
        "start_time": 60,
    },
]

# Implementation done by Usman Ahmed Saeed
def ldf_single_node(application_data):
    # There are two further methods in this method to clearly break down the work that is needed to be done, and increase readibility
    # Extract tasks and messages from the application_data
    tasks = application_data["tasks"]
    messages = application_data["messages"]
    
    # Initialize dictionaries to hold dependencies and in-degrees of tasks (so that the connection between the task is established)
    dependencies = defaultdict(list)
    in_degree = defaultdict(int)
    
    # Build the dependency graph from the messages of each task
    for msg in messages:
        dependencies[msg["sender"]].append(msg["receiver"])
        in_degree[msg["receiver"]] += 1
    
    # Helper function to perform topological sorting on tasks to ensure dependencies are met and are not scheduled before its predecessor
    def topological_sort(tasks, dependencies, in_degree):
        sorted_tasks = []  
        # Queue for tasks with no incoming edges (in-degree of 0)
        zero_in_degree_queue = deque([task["id"] for task in tasks if in_degree[task["id"]] == 0])
        
        while zero_in_degree_queue:
            # Process the task with zero in-degree
            task_id = zero_in_degree_queue.popleft()
            sorted_tasks.append(task_id)
            
            # Decrease the in-degree of dependent tasks
            for dependent in dependencies[task_id]:
                in_degree[dependent] -= 1
                # If a dependent task now has zero in-degree, add it to the queue
                if in_degree[dependent] == 0:
                    zero_in_degree_queue.append(dependent)
        # Returns back all tasks that are sorted so no tasks starts before its predecessor
        return sorted_tasks  
    
    # Here we first the sort the tasks in descending order based on their deadline.
    # Sorting tasks by latest deadline first - LDF
    sorted_tasks_by_deadline = sorted(tasks, key=lambda x: x["deadline"], reverse=True)
    
    # Get the tasks sorted topologically to ensure its dependencies
    topologically_sorted_tasks = topological_sort(sorted_tasks_by_deadline, dependencies, in_degree)
    
    # Helper function to schedule tasks on a single node system
    def schedule_tasks(tasks, task_order):
        schedule = []  
        current_time = 0  

        # Create a map from task IDs to task details for quick lookup
        task_map = {task["id"]: task for task in tasks}
        
        for task_id in task_order:
            # Get task details from the task map
            task = task_map[task_id]  
            # Assuming all tasks are scheduled on node 0 as it is a single node system
            node_id = 0  
            
            # Calculate start and end time of the task
            start_time = current_time
            end_time = current_time + task["wcet"]
            
            # Check if the task can be completed within its deadline
            if end_time > task['deadline']:
                print(f"Task {task['id']} cannot be scheduled within its deadline.")
                # Skip tasks that cannot meet their deadline
                continue  
            
            # Append the task schedule to the schedule list
            schedule.append({
                "task_id": task_id,
                "node_id": node_id,
                "start_time": start_time,
                "end_time": end_time,
                "deadline": task["deadline"]
            })
            # Move the current time forward by the task's execution time
            current_time += task["wcet"]  
        
        return schedule  
    
    # Generate the schedule for the tasks
    schedule = schedule_tasks(tasks, topologically_sorted_tasks)
    
    result = {
        "schedule": schedule, 
        "name": "LDF Single Node"
        } 

    return result 

# Implementation done by Adnan Akin Okcu using ldf_singlenode with non-reverse sorting
def edf_single_node(application_data):
   # There are two further methods in this method to clearly break down the work that is needed to be done, and increase readibility
    # Extract tasks and messages from the application_data
    tasks = application_data["tasks"]
    messages = application_data["messages"]
    
    # Initialize dictionaries to hold dependencies and in-degrees of tasks (so that the connection between the task is established)
    dependencies = defaultdict(list)
    in_degree = defaultdict(int)
    
    # Build the dependency graph from the messages of each task
    for msg in messages:
        dependencies[msg["sender"]].append(msg["receiver"])
        in_degree[msg["receiver"]] += 1
    
    # Helper function to perform topological sorting on tasks to ensure dependencies are met and are not scheduled before its predecessor
    def topological_sort(tasks, dependencies, in_degree):
        sorted_tasks = []  
        # Queue for tasks with no incoming edges (in-degree of 0)
        zero_in_degree_queue = deque([task["id"] for task in tasks if in_degree[task["id"]] == 0])
        
        while zero_in_degree_queue:
            # Process the task with zero in-degree
            task_id = zero_in_degree_queue.popleft()
            sorted_tasks.append(task_id)
            
            # Decrease the in-degree of dependent tasks
            for dependent in dependencies[task_id]:
                in_degree[dependent] -= 1
                # If a dependent task now has zero in-degree, add it to the queue
                if in_degree[dependent] == 0:
                    zero_in_degree_queue.append(dependent)
        # Returns back all tasks that are sorted so no tasks starts before its predecessor
        return sorted_tasks  
    
    # Here we first the sort the tasks in ascending order based on their deadline.
    # Sorting tasks by earliest deadline first - EDF
    sorted_tasks_by_deadline = sorted(tasks, key=lambda x: x["deadline"], reverse=False)
    
    # Get the tasks sorted topologically to ensure its dependencies
    topologically_sorted_tasks = topological_sort(sorted_tasks_by_deadline, dependencies, in_degree)
    
    # Helper function to schedule tasks on a single node system
    def schedule_tasks(tasks, task_order):
        schedule = []  
        current_time = 0  

        # Create a map from task IDs to task details for quick lookup
        task_map = {task["id"]: task for task in tasks}
        
        for task_id in task_order:
            # Get task details from the task map
            task = task_map[task_id]  
            # Assuming all tasks are scheduled on node 0 as it is a single node system
            node_id = 0  
            
            # Calculate start and end time of the task
            start_time = current_time
            end_time = current_time + task["wcet"]
            
            # Check if the task can be completed within its deadline
            if end_time > task['deadline']:
                print(f"Task {task['id']} cannot be scheduled within its deadline.")
                # Skip tasks that cannot meet their deadline
                continue  
            
            # Append the task schedule to the schedule list
            schedule.append({
                "task_id": task_id,
                "node_id": node_id,
                "start_time": start_time,
                "end_time": end_time,
                "deadline": task["deadline"]
            })
            # Move the current time forward by the task's execution time
            current_time += task["wcet"]  
        
        return schedule  
    
    # Generate the schedule for the tasks
    schedule = schedule_tasks(tasks, topologically_sorted_tasks)
    
    result = {
        "schedule": schedule, 
        "name": "EDF Single Node"
        } 

    return result 

# Implementation done by Safouane Chahid
def ll_multinode(application_data, platform_data):
 
    tasks = application_data['tasks']
    nodes = platform_data['nodes']
    node_availability = {node['id']: 0 for node in nodes}

    # Create a directed graph for task dependencies
    task_graph = nx.DiGraph()
    for task in tasks:
        task_graph.add_node(task['id'], wcet=task['wcet'], deadline=task['deadline'])

    for message in application_data.get('messages', []):
        task_graph.add_edge(message['sender'], message['receiver'])

    if not nx.is_directed_acyclic_graph(task_graph):
        raise ValueError("The task dependency graph has cycles, which is not supported.")

    # Compute topological ordering to ensure tasks are scheduled in dependency order
    sorted_tasks = list(nx.topological_sort(task_graph))

    schedule = {}
    for task_id in sorted_tasks:
        task = task_graph.nodes[task_id]
        wcet = task['wcet']
        deadline = task['deadline']

        # Determine the earliest time the task can start by checking the end times of all predecessors
        earliest_start_time = max((schedule[pred]['end_time'] for pred in task_graph.predecessors(task_id) if pred in schedule), default=0)

        # Find the earliest available node after the last predecessor has finished
        node_id = min(nodes, key=lambda n: max(earliest_start_time, node_availability[n['id']]))['id']

        start_time = max(earliest_start_time, node_availability[node_id])
        end_time = start_time + wcet

        if end_time > deadline:
            raise Exception(f"Task {task_id} cannot meet its deadline. Scheduling failed.")

        schedule[task_id] = {
            "task_id": task_id,
            "node_id": node_id,
            "start_time": start_time,
            "end_time": end_time,
            "deadline": deadline
        }
        node_availability[node_id] = end_time  # Update the node's availability

    return {
        "schedule": list(schedule.values()),
        "name": "LL Multi Node"
    }

# Implementation done by Usman Ahmed Saeed
def ldf_multinode(application_data, platform_data):
    # As in the Single node LDF method, there are also two methods or helper function you say to provide better readibility to the code base
    # Extract tasks and messages from the application_data as provided
    tasks = application_data["tasks"]
    messages = application_data["messages"]

    # Extract compute nodes and initialize their availability times from the platform_data
    nodes = platform_data['nodes']
    compute_nodes = {node['id']: 0 for node in nodes if node['type'] == 'compute'}

    # Initialize dictionaries to hold dependencies and in-degrees of tasks for their relationships
    dependencies = defaultdict(list)
    in_degree = defaultdict(int)

    # Build the dependency graph based on messages so relationship between each task is established
    for msg in messages:
        dependencies[msg["receiver"]].append(msg["sender"])
        in_degree[msg["receiver"]] += 1

    # Helper function to perform topological sorting on tasks to ensure dependencies are met
    def topological_sort(tasks, dependencies, in_degree):
        sorted_tasks = [] 
        # Queue for tasks with no incoming edges (in-degree of 0)
        zero_in_degree_queue = deque([task["id"] for task in tasks if in_degree[task["id"]] == 0])

        while zero_in_degree_queue:
            # Process the task with zero in-degree
            task_id = zero_in_degree_queue.popleft()
            sorted_tasks.append(task_id)

            # Decrease the in-degree of dependent tasks
            for dependent in dependencies[task_id]:
                in_degree[dependent] -= 1
                # If a dependent task now has zero in-degree, add it to the queue
                if in_degree[dependent] == 0:
                    zero_in_degree_queue.append(dependent)

        if len(sorted_tasks) != len(tasks):
            # This if condition handles any tasks which have multiple dependencies that needs to be taken care of such as Task 1 depends task 2, and task 3, and task 0 depends on task 1.
            remaining_tasks = {task["id"] for task in tasks if task["id"] not in sorted_tasks}
            while remaining_tasks:
                for task_id in list(remaining_tasks):
                    # Check if all dependencies of the task are already in sorted_tasks
                    if all(dep in sorted_tasks for dep in dependencies[task_id]):
                        sorted_tasks.append(task_id)
                        remaining_tasks.remove(task_id)
        # Return the topologically sorted task IDs
        return sorted_tasks 

    # Sort tasks by latest deadline first (LDF algorithm)
    sorted_tasks_by_deadline = sorted(tasks, key=lambda x: x["deadline"], reverse=True)

    # Debugging information to check if the dependencies are correctly identified.
    print(dependencies)
    # Get topologically sorted tasks to ensure every dependency is met of those tasks.
    topologically_sorted_tasks = topological_sort(tasks, dependencies, in_degree)

    # Debugging information to check if the sorting is done correctly
    print(topologically_sorted_tasks)
    # Initialize the schedule list
    schedule = []
    # Track completion times of tasks so that any task that is dependent on a particular task does not start before its predecessor where we maintain 
    # this completion times list to track every end time of a task.
    completion_times = {}

    # Schedule tasks on multi-node system
    for task_id in topologically_sorted_tasks:
        # Gets the next task in order
        task = next(task for task in tasks if task['id'] == task_id)

        # Gets the end time of the prodecessors on which the current task is dependent on so that it does not start before it.
        predecessors_end_times = [completion_times.get(predecessor, 0) for predecessor in dependencies[task_id]]
        # Extracting value of the end time and checking if the end time is there or assign 0 as the end time where there are no dependency on the current task.
        max_predecessor_end_time = max(predecessors_end_times) if predecessors_end_times else 0

        # Find the node with the earliest available time
        node_id = min(compute_nodes, key=compute_nodes.get)
        earliest_time = compute_nodes[node_id]

        # Ensure the task starts only after its predecessor has completed and the node is available
        start_time = max(max_predecessor_end_time, earliest_time)
        end_time = start_time + task['wcet']

        # Check if the task can be completed within its deadline
        if end_time > task['deadline']:
            print(f"Task {task['id']} cannot be scheduled within its deadline.")
            continue  

        # Append the task to the schedule list
        schedule.append({
            'task_id': task['id'],
            'node_id': node_id,
            'start_time': start_time,
            'end_time': end_time,
            'deadline': task['deadline']
        })

        # Update the completion time for the task
        completion_times[task_id] = end_time

        # Update the availability time for the specific node
        compute_nodes[node_id] = end_time

    # Return the result in the required format
    result = {
        'name': 'LDF Multi Node',
        'schedule': schedule
    }

    return result

# Implementation done by Adnan Akin Okcu using ldf_multinode with non-reverse sorting
def edf_multinode(application_data, platform_data):
   # As in the Single node LDF method, there are also two methods or helper function you say to provide better readibility to the code base
    # Extract tasks and messages from the application_data as provided
    tasks = application_data["tasks"]
    messages = application_data["messages"]

    # Extract compute nodes and initialize their availability times from the platform_data
    nodes = platform_data['nodes']
    compute_nodes = {node['id']: 0 for node in nodes if node['type'] == 'compute'}

    # Initialize dictionaries to hold dependencies and in-degrees of tasks for their relationships
    dependencies = defaultdict(list)
    in_degree = defaultdict(int)

    # Build the dependency graph based on messages so relationship between each task is established
    for msg in messages:
        dependencies[msg["receiver"]].append(msg["sender"])
        in_degree[msg["receiver"]] += 1

    # Helper function to perform topological sorting on tasks to ensure dependencies are met
    def topological_sort(tasks, dependencies, in_degree):
        sorted_tasks = [] 
        # Queue for tasks with no incoming edges (in-degree of 0)
        zero_in_degree_queue = deque([task["id"] for task in tasks if in_degree[task["id"]] == 0])

        while zero_in_degree_queue:
            # Process the task with zero in-degree
            task_id = zero_in_degree_queue.popleft()
            sorted_tasks.append(task_id)

            # Decrease the in-degree of dependent tasks
            for dependent in dependencies[task_id]:
                in_degree[dependent] -= 1
                # If a dependent task now has zero in-degree, add it to the queue
                if in_degree[dependent] == 0:
                    zero_in_degree_queue.append(dependent)

        if len(sorted_tasks) != len(tasks):
            # This if condition handles any tasks which have multiple dependencies that needs to be taken care of such as Task 1 depends task 2, and task 3, and task 0 depends on task 1.
            remaining_tasks = {task["id"] for task in tasks if task["id"] not in sorted_tasks}
            while remaining_tasks:
                for task_id in list(remaining_tasks):
                    # Check if all dependencies of the task are already in sorted_tasks
                    if all(dep in sorted_tasks for dep in dependencies[task_id]):
                        sorted_tasks.append(task_id)
                        remaining_tasks.remove(task_id)
        # Return the topologically sorted task IDs
        return sorted_tasks 

    # Sort tasks by latest deadline first (LDF algorithm)
    sorted_tasks_by_deadline = sorted(tasks, key=lambda x: x["deadline"], reverse=False)

    # Debugging information to check if the dependencies are correctly identified.
    print(dependencies)
    # Get topologically sorted tasks to ensure every dependency is met of those tasks.
    topologically_sorted_tasks = topological_sort(tasks, dependencies, in_degree)

    # Debugging information to check if the sorting is done correctly
    print(topologically_sorted_tasks)
    # Initialize the schedule list
    schedule = []
    # Track completion times of tasks so that any task that is dependent on a particular task does not start before its predecessor where we maintain 
    # this completion times list to track every end time of a task.
    completion_times = {}

    # Schedule tasks on multi-node system
    for task_id in topologically_sorted_tasks:
        # Gets the next task in order
        task = next(task for task in tasks if task['id'] == task_id)

        # Gets the end time of the prodecessors on which the current task is dependent on so that it does not start before it.
        predecessors_end_times = [completion_times.get(predecessor, 0) for predecessor in dependencies[task_id]]
        # Extracting value of the end time and checking if the end time is there or assign 0 as the end time where there are no dependency on the current task.
        max_predecessor_end_time = max(predecessors_end_times) if predecessors_end_times else 0

        # Find the node with the earliest available time
        node_id = min(compute_nodes, key=compute_nodes.get)
        earliest_time = compute_nodes[node_id]

        # Ensure the task starts only after its predecessor has completed and the node is available
        start_time = max(max_predecessor_end_time, earliest_time)
        end_time = start_time + task['wcet']

        # Check if the task can be completed within its deadline
        if end_time > task['deadline']:
            print(f"Task {task['id']} cannot be scheduled within its deadline.")
            continue  

        # Append the task to the schedule list
        schedule.append({
            'task_id': task['id'],
            'node_id': node_id,
            'start_time': start_time,
            'end_time': end_time,
            'deadline': task['deadline']
        })

        # Update the completion time for the task
        completion_times[task_id] = end_time

        # Update the availability time for the specific node
        compute_nodes[node_id] = end_time

    # Return the result in the required format
    result = {
        'name': 'EDF Multi Node',
        'schedule': schedule
    }

    return result
