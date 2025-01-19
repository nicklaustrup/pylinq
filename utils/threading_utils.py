import threading
from typing import Any, Optional


def run_in_thread(target, args=None, daemon=True):
    """
    Run a function in a separate thread.

    :param target: The target function to run.
    :param args: Arguments to pass to the target function (default: None).
    :param daemon: Whether the thread should be a daemon thread (default: True).
    :return: The Thread object.
    """
    if args is None:
        args = []

    thread = threading.Thread(target=target, args=args, daemon=daemon)
    thread.start()
    return thread


def run_in_background(target: Any, *args):
    """
    Run a function in the background, keeping the main thread free.

    :param target: The target function to run.
    :param args: Arguments to pass to the target function.
    :return: Thread object.
    """
    return run_in_thread(target, args=args)


def create_thread(target: Any, args=None, daemon=True):
    """
    Create and return a thread but without starting it yet.

    :param target: The target function to run.
    :param args: Arguments to pass to the target function (default: None).
    :param daemon: Whether the thread should be a daemon thread (default: True).
    :return: Thread object.
    """
    if args is None:
        args = []

    return threading.Thread(target=target, args=args, daemon=daemon)


def start_thread(thread: threading.Thread) -> Optional[threading.Thread]:
    """
    Starts a new thread to run the given target function with the provided arguments.

    :param thread: The thread to be started.
    :return: The Thread object that was started.
    """
    if thread.is_alive():
        thread.start()
        return thread


def stop_thread(thread):
    """
    Stop a thread by setting the thread to daemon and allowing it to exit.

    :param thread: The thread to stop.
    """
    if thread.is_alive():
        thread.join()


def run_safely(target, *args):
    """
    Run a function safely in a try/except block to catch any exceptions.

    :param target: The target function to run.
    :param args: Arguments to pass to the target function.
    """
    try:
        target(*args)
    except Exception as e:
        print(f"Error in thread: {e}")
