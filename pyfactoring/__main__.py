from pyfactoring.core import check, format, restore
from pyfactoring.settings import common_settings


if __name__ == '__main__':
    match common_settings.action:
        case "check":
            check()
        case "format":
            format()
        case "restore":
            restore()
        case _:
            print("Invalid action")
