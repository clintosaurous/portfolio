#!/opt/clintosaurous/venv/bin/python3 -Bu

"""
This module provides process multiprocessing operations for the Clintosaurous
tools.

It uses the multiprocessing module to create child processes.
"""


import atexit
import clintosaurous.log as log
import multiprocessing as mp
import time


VERSION = '1.1.0'
LAST_UPDATE = '2022-11-29'


# Store all procs launched for _kill_on_exit()
_all_procs = []


class start:

    """
    Class to start child process.

    Attributes:

        target (obj): Function or class the child processes will execute.
        proc_cnt (int): Number of child processes to launch.
            Default: 4 child processes per system processor.
        names (str): String to prepend process names with. Default: Worker X
        timeout (int): Total run time allowed for the process to run.
            Default: 3600 (1 hour)
    """

    # Default number of child processes to launch if not specified.
    _def_cnt = mp.cpu_count() * 4

    def __init__(
        self, target, proc_cnt: int = _def_cnt, names: str = None,
        timeout: int = 3600
    ):

        """
        Launch the child processes.

            processes = clintosaurous.multiprocessing.start(target)

        All child processes should be exited cleanly. All remaining child
        processes that have not exited cleanly will be terminated on exit. This
        will cause an exception.

        Parameters:

            target (obj): Function or class the child processes will execute.
            proc_cnt (int): Number of child processes to launch.
                Default: 4 child processes per system processor.
            names (str|list): Child process names. These can be string or a
                list. If omitted, the processes will be named 'Worker X',
                where X is the child process number. If a list is supplied,
                the child processes will be named based on the list. If the
                list is not as not long enough to supply all child processes,
                they will be called 'Worker X' again.
            timeout (int): Amount of time in seconds a process is allowed to
                run before clintosaurous.multiprocessing.check() will kill the
                process. Set to 0 for no timeout. Default: 3600 (1 hour)

        Parameters Of Child Process:

            Each child process will have three arguments sent to it.

                def child_proc_func(
                    proc_name, to_parent_pipe, from_parent_pipe
                ):
                    do stuf...

            str: Process name.
            multiprocessing.Pipe: Pipe to receive data from the parent
                process.
            multiprocessing.Pipe: Pipe to send data to the parrent process.

        Return:

            Child process information object.

            Object keys:

                procs (list):  A list of child processes are returned. Each
                element is a list with the following elements:

                    multiprocessing module object: Process object.
                    multiprocessig.Pipe: Pipe to receive data from the child
                        process.
                    multiprocessig.Pipe: Pipe to send data to the child
                        process.
                    int: Process start time in Linux timestamp format.

        Raises:

            TypeError: proc_cnt not an int.
            TypeError: name not a str or list.
            TypeError: timeout not an int.
        """

        # Type hints.
        if not isinstance(proc_cnt, int):
            raise TypeError(
                f'proc_cnt expected `int`, received {type(proc_cnt)}')
        if (
            names is not None and
            not isinstance(names, str) and
            not isinstance(names, list)
        ):
            raise TypeError(
                f'names expected `str` or `list`, received {type(names)}')
        if not isinstance(timeout, int):
            raise TypeError(
                f'proc_cnt expected `int`, received {type(timeout)}')

        atexit.register(_kill_on_exit)

        if names is None:
            names = []
            for i in range(proc_cnt):
                names.append(f'Worker {i}')
        elif isinstance(names, str):
            base_name = names
            names = []
            for i in range(proc_cnt):
                names.append(f'Worker {i}')
        else:
            name_cnt = len(names)
            if name_cnt < proc_cnt:
                for i in range(name_cnt, proc_cnt):
                    names.append(f'Worker {i}')

        self.procs = []
        self.proc_cnt = len(names)
        self.timeout = timeout

        for i in range(len(names)):
            log.log(f'Launching child process {names[i]} ...')
            from_parent_pipe, to_child_pipe = mp.Pipe(False)
            from_child_pipe, to_parent_pipe = mp.Pipe(False)
            child_proc = mp.Process(
                target=target, name=names[i], args=(
                    names[i], from_parent_pipe, to_parent_pipe,
                )
            )
            child_proc.start()
            self.procs.append([
                child_proc, from_child_pipe, to_child_pipe, time.time()
            ])
            _all_procs.append(child_proc)

    def check(self, wait: bool = False) -> int:

        """
        Check the status of child processes.

        Parameters:

            wait (bool): Wait for all processes to exit before returning.

        Return:

            int: The number of still running child process is returned.

        Raises:

            TypeError: wait not a bool.
        """

        if not isinstance(wait, bool):
            raise TypeError(f'wait expected `bool`, received {type(wait)}')

        while len(self.procs):

            for proc_num in reversed(range(len(self.procs))):
                proc_data = self.procs[proc_num]
                proc = proc_data[0]
                if proc.is_alive():
                    if (
                        self.timeout and
                        time.time() - proc_data[3] > self.timeout
                    ):
                        log.warn(f'{proc.name}: Timeout exceeded, killing!')
                        proc.kill()
                else:
                    if proc.exitcode:
                        log.warn(
                            f'{proc.name}: Non-zero exit code: ' +
                            f'{proc.exitcode}'
                        )
                    else:
                        log.log(f'{proc.name}: Process exited.')

                    del self.procs[proc_num]

            proc_cnt = len(self.procs)
            if not wait:
                self.proc_cnt = proc_cnt
                return self.proc_cnt

            if proc_cnt > 0 and proc_cnt != self.proc_cnt:
                log.log(f'Waiting on {proc_cnt} children to exit ...')
                self.proc_cnt = proc_cnt

            if proc_cnt < 0:
                return 0

            time.sleep(2)

    def get_proc_by_name(self, name: str) -> list:

        """
        Retrieve a specific process from the process list based on process
        name.

        Parameters:

            name: Process name to search for.

        Return:

            list: Process data from mp.procs[] for the process. None if
                process is not found.

        Raises:

            TypeError: name not a str.
        """

        if not isinstance(name, str):
            raise TypeError(f'name expected `str`, received {type(name)}')

        for proc in self.procs:
            if proc[0].name == name:
                return proc

        return None


def _kill_on_exit() -> None:

    """
    Kill all running child processes on exit.

    Internal only function and should not be called directly.
    """

    for proc in _all_procs:
        if proc.is_alive():
            proc.kill()
