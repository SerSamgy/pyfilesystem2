from __future__ import print_function
from __future__ import unicode_literals

import errno
import sys

from . import errors as fserrors

from six import reraise


class _ConvertOSErrors(object):
    """Context manager to convert OSErrors in to FS Errors."""

    ERRORS = {
        64: fserrors.RemoteConnectionError,  # ENONET
        errno.ENOENT: fserrors.ResourceNotFound,
        errno.EFAULT: fserrors.ResourceNotFound,
        errno.ESRCH: fserrors.ResourceNotFound,
        errno.ENOTEMPTY: fserrors.DirectoryNotEmpty,
        errno.EEXIST: fserrors.DirectoryExists,
        183: fserrors.DirectoryExists,
        errno.ENOTDIR: fserrors.DirectoryExpected,
        errno.EISDIR: fserrors.DirectoryNotExpected,
        errno.EINVAL: fserrors.ResourceInvalid,
        errno.ENOSPC: fserrors.InsufficientStorage,
        errno.EPERM: fserrors.PermissionDenied,
        errno.ENETDOWN: fserrors.RemoteConnectionError,
        errno.ECONNRESET: fserrors.RemoteConnectionError,
        errno.ENAMETOOLONG: fserrors.PathError,
        errno.EOPNOTSUPP: fserrors.Unsupported,
        errno.ENOSYS: fserrors.Unsupported
    }

    def __init__(self, opname, path):
        self._opname = opname
        self._path = path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type and isinstance(exc_value, EnvironmentError):
            _errno = exc_value.errno
            fserror = self.ERRORS.get(_errno, fserrors.OperationFailed)
            if _errno == errno.EACCES and sys.platform == "win32":
                if getattr(exc_value, 'args', None) == 32:  # pragma: no cover
                    fserror = fserrors.ResourceLocked
            reraise(
                fserror,
                fserror(
                    self._path,
                    opname=self._opname,
                    exc=exc_value
                ),
                traceback
            )

# Stops linter complaining about invalid class name
convert_os_errors = _ConvertOSErrors
