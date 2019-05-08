#!/usr/bin/env python

import re
import sys
from textwrap import dedent

from openstack_schedules.solution import Solution
from openstack_schedules.reporter import Reporter
from openstack_schedules.utils import abort


def by_name_sorter(a, b):
    return cmp(a, b)


def main():
    solver, solution_path, tracks_path, timings_path = sys.argv[1:]

    solution = Solution(solver)

    with open(solution_path) as solution_file:
        if solver == 'cbc':
            solution.parse_cbc(solution_file)
        else:
            abort("Unknown solver type '%s'\n" % solver)

    reporter = Reporter(solution)
    reporter.report()

    if timings_path:
        with open(timings_path) as timings:
            print(timings.readline()),


if __name__ == '__main__':
    main()
