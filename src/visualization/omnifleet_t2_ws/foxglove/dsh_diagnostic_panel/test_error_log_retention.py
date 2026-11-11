from collections import deque
from types import SimpleNamespace
import threading
from diagnostic_node import Diagnostics
fake=SimpleNamespace(lock=threading.Lock(),logs=deque(maxlen=20))
Diagnostics.on_log(fake,SimpleNamespace(name='controller_server',level=40,msg='Failed to make progress'))
for _ in range(100):Diagnostics.on_log(fake,SimpleNamespace(name='controller_server',level=30,msg='[follow_path] [ActionServer] Aborting handle.'))
assert len(fake.logs)==2
assert any(e['message']=='Failed to make progress' for e in fake.logs)
print('PASS: repeated aborts do not evict the distinct underlying error')
