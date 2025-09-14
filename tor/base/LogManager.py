import logging
import logging.config
import sys
import os
import yaml

# Cross-platform main script detection
MAIN_SCRIPT = os.path.splitext(os.path.basename(sys.argv[0]))[0]


def setupLogging(config_file):
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)


def getLogger(module_name=None):
    # Returns a logger with dynamic hierarchical name:
    caller = sys._getframe(1).f_globals.get("__name__", "__main__")

    if caller == "__main__":  # main script
        # Use module_name if given, else just main script name
        logger_name = MAIN_SCRIPT if module_name is None else f"{MAIN_SCRIPT} - {module_name}"
    else:
        # imported module, prefix with main script
        logger_name = f"{MAIN_SCRIPT} - {module_name}"

    return logging.getLogger(logger_name)