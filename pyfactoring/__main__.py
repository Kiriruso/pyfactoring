from pyfactoring.core import action_check, action_format, action_restore
from pyfactoring.settings import common_settings


if __name__ == '__main__':
    match common_settings.action:
        case "check":
            action_check()
        case "format":
            action_format()
        case "restore":
            action_restore()
