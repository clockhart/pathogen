
from glob import glob
from itertools import product
import os


class Path:
    """
    A way to hold a path (as a string) but retain metadata.
    """

    __slots__ = ('_pathname', '_metadata')

    def __init__(self, pathname, **metadata):
        if isinstance(pathname, Path):
            metadata = pathname._metadata
            pathname = pathname._pathname

        self._pathname = pathname
        self._metadata = metadata

    def __repr__(self):
        return self._pathname

    def __fspath__(self):
        return self._pathname

    @property
    def metadata(self):
        return self._metadata


# Variable glob
def vglob(pathname, errors='raise', **kwargs):
    """
    Variable glob.

    Parameters
    ----------
    pathname : str
        The variable `pathname` is used to match :ref:`glob`.
    errors : str
        How to handle errors? Currently only 'raise' is supported.

    Returns
    -------
    list
    """

    # Where any kwargs supplied? If not, short-circuit and glob
    if len(kwargs) == 0:
        return glob(pathname)

    # Variables to iterate
    keys = kwargs.keys()
    if errors.lower() in 'raise':
        for key in keys:
            if key not in pathname:
                raise AttributeError('{' + f'{key}' + '}' + f' not in pathname="{pathname}"')

    # Values
    def _convert_to_list(value):
        # BUGFIX https://github.com/LockhartLab/molecular/issues/2#issue-838289328
        if not isinstance(value, range) and not hasattr(value, '__getitem__'):
            value = [value]
        return value

    values = map(_convert_to_list, kwargs.values())

    # Go through each set of values and
    files = []
    for value_set in product(*values):
        fmt = {key: value_set[i] for i, key in enumerate(keys)}
        fname = pathname.format(**fmt)
        if errors.lower() in 'raise' and not os.path.exists(fname):
            raise FileNotFoundError(fname)
        files.append(Path(fname, **fmt))

    # Return
    return files
