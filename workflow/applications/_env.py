import subprocess
import platform
import os


def get_default_user_environment_windows():
    """Return a dict approximating the default environment the shell/Explorer
    would give to a new process for the current user, without inheriting ours.
    """
    import ctypes
    import ctypes.wintypes
    # Win32 APIs
    userenv = ctypes.WinDLL("userenv", use_last_error=True)
    advapi32 = ctypes.WinDLL("Advapi32", use_last_error=True)

    LPVOID = ctypes.wintypes.LPVOID
    HANDLE = ctypes.wintypes.HANDLE
    PHANDLE = ctypes.POINTER(HANDLE)

    CreateEnvironmentBlock = userenv.CreateEnvironmentBlock
    CreateEnvironmentBlock.argtypes = [
        ctypes.POINTER(LPVOID), HANDLE, ctypes.wintypes.BOOL
    ]
    CreateEnvironmentBlock.restype = ctypes.wintypes.BOOL

    DestroyEnvironmentBlock = userenv.DestroyEnvironmentBlock
    DestroyEnvironmentBlock.argtypes = [LPVOID]
    DestroyEnvironmentBlock.restype = ctypes.wintypes.BOOL

    OpenProcessToken = advapi32.OpenProcessToken
    OpenProcessToken.argtypes = [HANDLE, ctypes.wintypes.DWORD, PHANDLE]
    OpenProcessToken.restype = ctypes.wintypes.BOOL

    GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess

    TOKEN_QUERY = 0x0008

    h_process = GetCurrentProcess()
    h_token = HANDLE()
    if not OpenProcessToken(h_process, TOKEN_QUERY, ctypes.byref(h_token)):
        raise OSError(
            ctypes.get_last_error(),
            "OpenProcessToken failed"
        )

    lpEnv = LPVOID()
    # bInherit = FALSE -> do not inherit from current process; build fresh
    if not CreateEnvironmentBlock(ctypes.byref(lpEnv), h_token, False):
        raise OSError(
            ctypes.get_last_error(),
            "CreateEnvironmentBlock failed"
        )

    try:
        # Cast to a pointer to wide characters
        wchar_ptr = ctypes.cast(lpEnv, ctypes.POINTER(ctypes.c_wchar))
        env = {}
        s_chars = []
        i = 0
        # The block is "key=value\0key=value\0...\0\0"
        while True:
            ch = wchar_ptr[i]
            i += 1
            if ch == "\x00":
                if not s_chars:
                    # Two consecutive NULs -> end of block
                    break
                entry = "".join(s_chars)
                s_chars = []
                if "=" in entry:
                    k, v = entry.split("=", 1)
                    env[k] = v
            else:
                s_chars.append(ch)
        return env
    finally:
        # Always free the environment block
        DestroyEnvironmentBlock(lpEnv)


def _user_identity():
    import pwd

    pw = pwd.getpwuid(os.getuid())
    return {
        "HOME": pw.pw_dir,
        "USER": pw.pw_name,
        "LOGNAME": pw.pw_name,
        "SHELL": pw.pw_shell or "/bin/sh",
    }


def get_default_like_login_env_posix():
    ident = _user_identity()
    shell = ident["SHELL"]

    # Minimal PATH: good defaults per platform
    if platform.system().lower() == "darwin":
        min_path = "/usr/bin:/bin:/usr/sbin:/sbin"
    else:
        min_path = "/usr/bin:/bin"

    base_env = {
        "HOME": ident["HOME"],
        "USER": ident["USER"],
        "LOGNAME": ident["LOGNAME"],
        "SHELL": shell,
        "PATH": min_path,
        # Optional: tame locale to avoid surprises if profiles rely on it
        "LANG": "C",
        "LC_ALL": "C",
    }

    # Run the shell as a login shell (-l) and print env in a parseable form
    if os.path.basename(shell) == "zsh":
        args = [shell, "-l", "-c", "printenv -0"]
    else:
        # Fallback to POSIX sh behavior
        args = [shell, "-l", "-c", "env -0"]

    # No inheritance: we pass only base_env
    out = subprocess.check_output(args, env=base_env)

    # Parse NUL-separated KEY=VALUE entries
    env_dict = {}
    for entry in out.split(b"\x00"):
        if not entry:
            continue
        k, _, v = entry.partition(b"=")
        key = k.decode("utf-8", "replace")
        value = v.decode("utf-8", "replace")
        env_dict[key] = value
    return env_dict


def get_default_user_environment():
    if platform.system().lower() == "windows":
        return get_default_user_environment_windows()
    return get_default_like_login_env_posix()


def get_clean_envs():
    env = get_default_user_environment()
    for key, value in os.environ.items():
        if key.startswith("AYON_"):
            env[key] = os.environ[key]
    return env
