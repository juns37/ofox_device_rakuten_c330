import struct, sys

p = sys.argv[1]
ver = [int(x) for x in sys.argv[2].split('.')]
y, m = [int(x) for x in sys.argv[3].split('-')[:2]]
b = bytearray(open(p, 'rb').read())
assert b[:8] == b'ANDROID!'
assert struct.unpack_from('<I', b, 40)[0] == 0
v = (ver[0] << 25) | (ver[1] << 18) | (ver[2] << 11) | ((y - 2000) << 4) | m
struct.pack_into('<I', b, 44, v)
open(p, 'wb').write(b)
print('os_version %s patch %d-%02d -> 0x%08x' % (sys.argv[2], y, m, v))
