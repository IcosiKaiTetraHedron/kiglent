from ctypes import *

import kiglent
import kiglent.util


__all__ = ['link_EGL']

egl_lib = kiglent.lib.load_library('EGL')

# Look for eglGetProcAddress
eglGetProcAddress = getattr(egl_lib, 'eglGetProcAddress')
eglGetProcAddress.restype = POINTER(CFUNCTYPE(None))
eglGetProcAddress.argtypes = [POINTER(c_ubyte)]


def link_EGL(name, restype, argtypes, requires=None, suggestions=None):
    try:
        func = getattr(egl_lib, name)
        func.restype = restype
        func.argtypes = argtypes
        return func
    except AttributeError:
        bname = cast(pointer(create_string_buffer(kiglent.util.asbytes(name))), POINTER(c_ubyte))
        addr = eglGetProcAddress(bname)
        if addr:
            ftype = CFUNCTYPE(*((restype,) + tuple(argtypes)))
            func = cast(addr, ftype)
            return func

    return kiglent.gl.lib.missing_function(name, requires, suggestions)
