#!/usr/bin/env python
import os
import sys

from core.boot import fix_path
fix_path(include_dev_libs=True)


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.local')

    from djangae.core.management import execute_from_command_line
    from djangae.core.management import test_execute_from_command_line

    if 'test' in sys.argv:
        test_execute_from_command_line(sys.argv)
    else:
        execute_from_command_line(sys.argv)
