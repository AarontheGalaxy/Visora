"""
Single-instance lock — prevents multiple copies of the app from running.
Uses atomic file creation (O_CREAT | O_EXCL) to avoid race conditions,
then fcntl.flock() on Unix for additional safety.
"""

import os
import sys

LOCK_PATH = os.path.join(os.path.expanduser("~"), ".visora", "app.lock")
_lock_fd = None  # held open to keep flock active


def acquire() -> bool:
    """
    Atomically acquire the single-instance lock.
    Returns True if this process is the only running instance.
    Returns False if another instance already holds the lock.
    """
    global _lock_fd  # noqa: PLW0603
    os.makedirs(os.path.dirname(LOCK_PATH), exist_ok=True)

    # --- Unix: atomic create + exclusive flock ---
    # fcntl is Unix-only; do NOT use hasattr(os, "O_CREAT") — that flag
    # exists on Windows too, which would cause an ImportError for fcntl.
    if sys.platform != "win32":
        import fcntl
        try:
            fd = os.open(LOCK_PATH, os.O_CREAT | os.O_WRONLY, 0o600)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            os.write(fd, str(os.getpid()).encode())
            _lock_fd = fd  # keep fd open — flock is released when fd closes
            return True
        except (OSError, BlockingIOError):
            # Another process may hold the flock, or it crashed without cleanup.
            # If the PID in the file is stale, remove it and retry once.
            if _check_stale_pid():
                return acquire()
            return False

    # --- Windows: O_EXCL atomic create ---
    try:
        fd = os.open(LOCK_PATH, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return True
    except FileExistsError:
        if _windows_pid_alive():
            return False
        # Stale lock — remove and retry once
        try:
            os.remove(LOCK_PATH)
        except OSError:
            pass
        return acquire()


def release():
    """Release the lock on clean exit."""
    global _lock_fd  # noqa: PLW0603
    if _lock_fd is not None:
        try:
            import fcntl
            fcntl.flock(_lock_fd, fcntl.LOCK_UN)
            os.close(_lock_fd)
        except OSError:
            pass
        _lock_fd = None
    try:
        os.remove(LOCK_PATH)
    except OSError:
        pass


def _check_stale_pid() -> bool:
    """
    On Unix: verify the locking process is still alive.
    Returns True if the lock was stale and has been removed (caller should retry).
    Returns False if the lock is held by a live process.
    """
    try:
        with open(LOCK_PATH, "rb") as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)  # signal 0 = existence check, raises OSError if dead
        return False  # process is alive — lock is legitimately held
    except (ValueError, OSError):
        try:
            os.remove(LOCK_PATH)
        except OSError:
            pass
        return True  # stale lock removed; caller should retry


def _windows_pid_alive() -> bool:
    """On Windows: read PID from lock file and check if process still runs."""
    try:
        with open(LOCK_PATH, "rb") as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return True
    except (ValueError, OSError):
        return False
