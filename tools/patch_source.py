import os, sys

root = sys.argv[1]
p = os.path.join(root, 'frameworks/native/libs/binder/ndk/ibinder.cpp')
s = open(p).read()
old = 'return ::android::IPCThreadState::self()->getCallingSid();'
if 'u:r:recovery:s0' not in s:
    assert s.count(old) == 1, 'getCallingSid pattern'
    s = s.replace(old, 'const char* sid = ::android::IPCThreadState::self()->getCallingSid();\n    return sid ? sid : "u:r:recovery:s0";')
    open(p, 'w').write(s)
    print('patched', p)
