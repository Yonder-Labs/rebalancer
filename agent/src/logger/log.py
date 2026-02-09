# TODO: Expand logger functionality (e.g., log levels, formatting)
class Logger:
    @staticmethod
    def _print(msg: str):
        print(msg)

    @staticmethod
    def _file(msg: str):
        with open("app.log", "a", encoding="utf-8") as f:
            f.write(msg + "\n")


    _transports = {
        "print": _print.__func__,
        "file": _file.__func__,
    }

    _active_transport = _print.__func__
    _initialized = False

    @classmethod
    def initialize(cls, transport: str):
        if cls._initialized:
            return

        if transport not in cls._transports:
            raise ValueError(f"Unknown logger transport: {transport}")

        cls._active_transport = cls._transports[transport]
        cls._initialized = True

    @classmethod
    def log(cls, msg: str):
        cls._active_transport(msg)