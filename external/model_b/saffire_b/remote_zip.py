"""Read selected NASA ZIP members using authenticated-by-URL HTTP byte ranges.

Only public NASA-provided temporary URLs are used. URLs are never stored in outputs.
ZIP CRC verification and per-member SHA256 retain content integrity without downloading
multiple gigabytes of duplicate image encodings.
"""
import io
from urllib.request import Request, urlopen


class RangeReader(io.RawIOBase):
    def __init__(self, url, size):
        self.url, self.size, self.position = url, size, 0
        self.cache = []

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        self.position = offset if whence == 0 else self.position + offset if whence == 1 else self.size + offset
        if self.position < 0:
            raise ValueError('Negative byte offset')
        return self.position

    def read(self, size=-1):
        if size < 0:
            size = self.size - self.position
        if size == 0 or self.position >= self.size:
            return b''
        begin, end = self.position, min(self.position + size, self.size)
        for a, b, data in self.cache:
            if a <= begin and end <= b:
                self.position = end
                return data[begin-a:end-a]
        # Cache central-directory tail plus local headers/member payloads.
        a, b = begin, min(self.size, max(end, begin+65536))
        req = Request(self.url, headers={'Range': f'bytes={a}-{b-1}'})
        with urlopen(req, timeout=90) as response:
            if response.status != 206:
                raise IOError('Server must support byte-range reads')
            data = response.read()
        if len(data) != b-a:
            raise IOError('Truncated byte-range response')
        self.cache.append((a,b,data))
        self.position = end
        return data[:end-begin]
