"""Get environment information useful for debugging.

Intended usage is to create a file for bug reports, e.g.::

    python -m kiglent.info > info.txt

"""

_first_heading = True


def _heading(heading):
    global _first_heading
    if not _first_heading:
        print()
    else:
        _first_heading = False
    print(heading)
    print('-' * 78)


def dump_platform():
    """Dump OS specific """
    import platform
    print('platform: ', platform.platform())
    print('release:  ', platform.release())
    print('machine:  ', platform.machine())


def dump_python():
    """Dump Python version and environment to stdout."""
    import os
    import sys
    import platform
    print('implementation:', platform.python_implementation())
    print('sys.version:', sys.version)
    print('sys.maxint:', sys.maxsize)
    if sys.platform == 'darwin':
        try:
            from objc import __version__ as pyobjc_version
            print('objc.__version__:', pyobjc_version)
        except:
            print('PyObjC not available')
    print('os.getcwd():', os.getcwd())
    for key, value in os.environ.items():
        if key.startswith('PYGLET_'):
            print(f"os.environ['{key}']: {value}")


def dump_kiglent():
    """Dump kiglent version and options."""
    import kiglent
    print('kiglent.version:', kiglent.version)
    print('kiglent.compat_platform:', kiglent.compat_platform)
    print('kiglent.__file__:', kiglent.__file__)
    for key, value in kiglent.options.items():
        print(f"kiglent.options['{key}'] = {value!r}")


def dump_window():
    """Dump display, window, screen and default config info."""
    from kiglent.gl import gl_info
    if not gl_info.have_version(3):
        print(f"Insufficient OpenGL version: {gl_info.get_version_string()}")
        return
    import kiglent.window
    display = kiglent.display.get_display()
    print('display:', repr(display))
    screens = display.get_screens()
    for i, screen in enumerate(screens):
        print(f'screens[{i}]: {screen!r}')
    window = kiglent.window.Window(visible=False)
    for key, value in window.config.get_gl_attributes():
        print(f"config['{key}'] = {value!r}")
    print('context:', repr(window.context))

    _heading('window.context._info')
    dump_gl(window.context)
    window.close()


def dump_gl(context=None):
    """Dump GL info."""
    if context is not None:
        info = context.get_info()
    else:
        from kiglent.gl import gl_info as info
    print('gl_info.get_version():', info.get_version())
    print('gl_info.get_vendor():', info.get_vendor())
    print('gl_info.get_renderer():', info.get_renderer())


def dump_glx():
    """Dump GLX info."""
    try:
        from kiglent.gl import glx_info
    except:
        print('GLX not available.')
        return
    import kiglent
    window = kiglent.window.Window(visible=False)
    print('context.is_direct():', window.context.is_direct())
    window.close()

    if not glx_info.have_version(1, 1):
        print('Version: < 1.1')
    else:
        print('glx_info.get_server_vendor():', glx_info.get_server_vendor())
        print('glx_info.get_server_version():', glx_info.get_server_version())
        print('glx_info.get_server_extensions():')
        for name in glx_info.get_server_extensions():
            print('  ', name)
        print('glx_info.get_client_vendor():', glx_info.get_client_vendor())
        print('glx_info.get_client_version():', glx_info.get_client_version())
        print('glx_info.get_client_extensions():')
        for name in glx_info.get_client_extensions():
            print('  ', name)
        print('glx_info.get_extensions():')
        for name in glx_info.get_extensions():
            print('  ', name)


def dump_media():
    """Dump kiglent.media info."""
    import kiglent.media
    print('audio driver:', kiglent.media.get_audio_driver())


def dump_ffmpeg():
    """Dump FFmpeg info."""
    import kiglent
    kiglent.options['search_local_libs'] = True
    import kiglent.media

    if kiglent.media.have_ffmpeg():
        from kiglent.media.codecs.ffmpeg import get_version
        print('FFmpeg version:', get_version())
    else:
        print('FFmpeg not available.')


def dump_al():
    """Dump OpenAL info."""
    try:
        from kiglent.media.drivers import openal
    except:
        print('OpenAL not available.')
        return
    print('Library:', openal.lib_openal._lib)

    driver = openal.create_audio_driver()
    print('Version: {}.{}'.format(*driver.get_version()))
    print('Extensions:')
    for extension in driver.get_extensions():
        print('  ', extension)


def dump_wintab():
    """Dump WinTab info."""
    try:
        from kiglent.input.win32 import wintab
    except:
        print('WinTab not available.')
        return

    interface_name = wintab.get_interface_name()
    impl_version = wintab.get_implementation_version()
    spec_version = wintab.get_spec_version()

    print('WinTab: {0} {1}.{2} (Spec {3}.{4})'.format(interface_name,
                                                      impl_version >> 8, impl_version & 0xff,
                                                      spec_version >> 8, spec_version & 0xff))


def _try_dump(heading, func):
    _heading(heading)
    try:
        func()
    except:
        import traceback
        traceback.print_exc()


def dump():
    """Dump all information to stdout."""
    _try_dump('Platform', dump_platform)
    _try_dump('Python', dump_python)
    _try_dump('kiglent', dump_kiglent)
    _try_dump('kiglent.window', dump_window)
    _try_dump('kiglent.gl.glx_info', dump_glx)
    _try_dump('kiglent.media', dump_media)
    _try_dump('kiglent.media.ffmpeg', dump_ffmpeg)
    _try_dump('kiglent.media.drivers.openal', dump_al)
    _try_dump('kiglent.input.wintab', dump_wintab)


if __name__ == '__main__':
    dump()
