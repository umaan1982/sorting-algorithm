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

# just an eample for the structure of the schedule to be returned and to check the frontend and backend connection
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


def ldf_single_node(application_data):
    # Extracting data from the application data, with the identifier being 'task'
    tasks = application_data['tasks']
    # Sorting the tasks using python libs based on the value of the deadline as we are implementing LDF
    tasks_sorted = sorted(tasks, key=lambda x: x['deadline'], reverse=True)
    
    # As we are implementing LDF for single node, it would be wise to assume the node_id to 0 as it is the first node.
    node_id = 0
    
    # Initialize the schedule list and the current start time.
    schedule = []
    current_start_time = 0
    
    # Iterate over sorted tasks and create the schedule for output inserting only neccassary information related to the schedule.
    for task in tasks_sorted:
        # Updating the end time with the task utilized time labelled as 'wcet', providing us information of the total time it took for the algorithm to compute.
        end_time = current_start_time + task['wcet']
        schedule.append({
            'task_id': task['id'],
            'node_id': node_id,
            'start_time': current_start_time,
            'end_time': end_time,
            'deadline': task['deadline']
        })
        # Update the start time for the next task.
        current_start_time = end_time  
    
    # Return the result in the required format that is the list of dictionary.
    result = {
        'name': 'LDF Single Node',
        'schedule': schedule
    }
    
    return result


def edf_single_node(application_data):
    """
    Schedule jobs on single node using the Earliest Deadline First (EDF) strategy.

    This function processes application data to schedule jobs based on the earliest
    deadlines. It builds a dependency graph and schedules accordingly, ensuring that jobs with no predecessors are
    scheduled first, and subsequent jobs are scheduled based on the minimum deadline of available nodes.

    .. todo:: Implement Earliest Deadline First Scheduling (EDF) algorithm for single compute node.

    Args:
        application_data (dict): Job data including dependencies represented by messages between jobs.

    Returns:
        list of dict: Contains the scheduled job details, each entry detailing the node assigned, start and end times,
                      and the job's deadline.
    """

    return {"schedule": example_schedule, "name": "EDF Single Node"}


def ll_multinode(application_data, platform_data):
    """
    Schedule jobs on a distributed system with multiple compute nodes using the Least Laxity (LL) strategy.
    This function schedules jobs based on their laxity, with the job having the least laxity being scheduled first.

    .. todo:: Implement Least Laxity (LL) algorithm to schedule jobs on multiple node in a distributed system.

    Args:
        application_data (dict): Job data including dependencies represented by messages between jobs.

    Returns:
        list of dict: Contains the scheduled job details, each entry detailing the node assigned, start and end times,
                      and the job's deadline.

    """
    return {"schedule": example_schedule, "name": "LL Multi Node"}


def ldf_multinode(application_data, platform_data):
    # Extract tasks and sort them by latest deadline first.
    tasks = application_data['tasks']
    # Sorting the tasks using python libs based on the value of the deadline as we are implementing LDF
    tasks_sorted = sorted(tasks, key=lambda x: x['deadline'], reverse=True)
    
    # Extracting nodes and initializing their availability times as we are dealing with data with multiple nodes
    nodes = platform_data['nodes']
    # Iterating throughtout the data to extract all the nodes
    node_avail_times = {node['id']: 0 for node in nodes}
    
    # Initialize the schedule list
    schedule = []

    # Iterate over sorted tasks and assign them to nodes
    for task in tasks_sorted:
        # Find the node with the earliest available time
        node_id, earliest_time = min(node_avail_times.items(), key=lambda x: x[1])
        
        # Calculate the start and end times for the task
        start_time = earliest_time
        end_time = start_time + task['wcet']
        
        # Append the task to the schedule list 
        schedule.append({
            'task_id': task['id'],
            'node_id': node_id,
            'start_time': start_time,
            'end_time': end_time,
            'deadline': task['deadline']
        })
        
        # Update the availability time for the specific node.
        node_avail_times[node_id] = end_time
    
    # Return the result in the required format.
    result = {
        'name': 'LDF Multi Node',
        'schedule': schedule
    }
    
    return result


def edf_multinode(application_data, platform_data):
    """
    Schedule jobs on a distributed system with multiple compute nodes using the Earliest Deadline First (EDF) strategy.
    This function processes application data to schedule jobs based on the earliest
    deadlines.

    .. todo:: Implement Earliest Deadline First(EDF) algorithm to schedule jobs on multiple nodes in a distributed system.

    Args:
        application_data (dict): Job data including dependencies represented by messages between jobs.
        platform_data (dict): Contains information about the platform, nodes and their types, the links between the nodes and the associated link delay.

    Returns:
        list of dict: Contains the scheduled job details, each entry detailing the node assigned, start and end times,
                      and the job's deadline.

    """
    return {"schedule": example_schedule, "name": "EDF Multi Node"}
