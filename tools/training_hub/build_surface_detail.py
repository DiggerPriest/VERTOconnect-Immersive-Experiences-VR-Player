"""Original deterministic repeated surface texture; no external image sources."""
import math
from pathlib import Path
import random
import struct
import zlib

size = 512
rng = random.Random(421)
scanlines = bytearray()
for y in range(size):
    scanlines.append(0)
    for x in range(size):
        value = int(128 + 16 * math.sin(x * math.tau * 7 / size) * math.sin(y * math.tau * 11 / size) + rng.uniform(-32, 32))
        scanlines.extend((value, value, value))

def chunk(kind, payload):
    return struct.pack('!I', len(payload)) + kind + payload + struct.pack('!I', zlib.crc32(kind + payload) & 0xffffffff)

path = Path(__file__).resolve().parents[2] / 'app/godot/environments/training_hub/surface_detail.png'
path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', size, size, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(bytes(scanlines))) + chunk(b'IEND', b''))
print(path)
