import os
import sys
import tempfile
from pathlib import Path

_FILES = []

def _inject(vm):
    from genlayer.py import calldata
    from genlayer.py.types import Address
    conv = lambda value: Address(value) if isinstance(value, bytes) else value
    message = {"contract_address":conv(vm._contract_address),"sender_address":conv(vm.sender),"origin_address":conv(vm.origin),"stack":[],"value":vm._value,"datetime":vm._datetime,"is_init":False,"chain_id":vm._chain_id,"entry_kind":0,"entry_data":b"","entry_stage_data":None}
    fd, path = tempfile.mkstemp(prefix="gmee-")
    _FILES.append(Path(path)); os.write(fd, calldata.encode(message)); os.lseek(fd,0,os.SEEK_SET)
    vm._original_stdin_fd=os.dup(0); os.dup2(fd,0); os.close(fd)

def pytest_configure():
    if sys.platform == "win32":
        from gltest.direct import loader
        loader._inject_message_to_fd0 = _inject

def pytest_sessionfinish():
    for path in _FILES:
        try: path.unlink(missing_ok=True)
        except PermissionError: pass
