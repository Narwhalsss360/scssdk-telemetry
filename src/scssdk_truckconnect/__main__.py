from typing import Callable
from sys import argv, stderr
from scssdk_truckconnect import (
    truckconnect,
    cpp,
    csharp,
    py
)


MAINS: dict[str, Callable] = {
    "truckconnect": truckconnect.main,
    "cpp": cpp.main,
    "csharp": csharp.main,
    "py": py.main
}


if len(argv) == 1:
    print(f"Commands:")
    for main in MAINS:
        print(main)
    exit()


if not (main := MAINS.get(argv.pop(1))):
    print(f"Commands:", file=stderr)
    for main in MAINS:
        print(main, file=stderr)
    exit()


main()
