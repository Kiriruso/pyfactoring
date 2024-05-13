from pyfactoring.core import action_check, action_format, cache
from pyfactoring.settings import common_settings


def main():
    match common_settings.action:
        case "check":
            action_check()
        case "format":
            action_format()
        case "restore":
            cache.restore()


if __name__ == '__main__':
    main()
