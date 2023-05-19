import asyncio
from typing import List
from itertools import chain
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


async def _run_tasks_in_excutor(executor, task_func, tasks: List):
    loop = asyncio.get_event_loop()
    _async_tasks = [
        loop.run_in_executor(executor, task_func, task) for task in tasks
    ]
    _tasks_result = await asyncio.wait(_async_tasks)
    return list(chain.from_iterable(_tasks_result))


def async_thread_tasks(task_func, tasks: List):
    executor = ThreadPoolExecutor(max_workers=10)
    event_loop = asyncio.get_event_loop()
    tasks_result = []
    try:
        tasks_result = event_loop.run_until_complete(
            _run_tasks_in_excutor(executor, task_func, tasks))
    finally:
        executor.shutdown(wait=True)
    return tasks_result


def async_process_tasks(task_func, tasks: List):
    executor = ProcessPoolExecutor(max_workers=10)
    event_loop = asyncio.get_event_loop()
    tasks_result = []
    try:
        tasks_result = event_loop.run_until_complete(
            _run_tasks_in_excutor(executor, task_func, tasks))
    finally:
        executor.shutdown(wait=True)
    return tasks_result
