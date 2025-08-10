try:
    from .scssdk_dataclasses import main
except ImportError:
    from scssdk_dataclasses import main

if __name__ == "__main__":
    main()
