from persistent import Persistent
from zope.interface import Interface, implementer
from .interfaces import IDataChunk


@implementer(IDataChunk)
class FileChunk(Persistent):
    """Wrapper for possibly large data
    """
    next = None

    def __init__(self, data):
        self._data = data

    def __getslice__(self, i, j):
        # Deprecated. Is it still necessary ?
        return self._data[i:j]

    def __len__(self):
        data = str(self)
        return len(data)

    def __str__(self):
        next = self.next
        if next is None:
            return self._data

        result = [self._data]
        while next is not None:
            self = next
            result.append(self._data)
            next = self.next

        return ''.join(result)
