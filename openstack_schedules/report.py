#!/usr/bin/python

import re
import sys
from textwrap import dedent


def abort(message):
    sys.stderr.write(message)
    sys.exit(1)


def by_name_sorter(a, b):
    return cmp(a, b)


def main():
    solver, solution_path = \
        sys.argv[1:]

    solution = Solution(solver)

    with open(solution_path) as solution_file:
        if solver == 'cbc':
            solution.parse_cbc(solution_file)
        else:
            abort("Unknown solver type '%s'\n" % solver)

    solution.report()

    if timings_path:
        with open(timings_path) as timings:
            print timings.readline(),


class Solution(object):
    def __init__(self, solver, prefs, skill_names, skills, instruments):
        self.solver = solver

        # solution's value of objective function
        self.objective = None

        # Solution breakdown, mapping student -> (teacher, team, score)
        self.track_start = {}

    def start_track(self, track, slot):
        if team not in self.teams:
            self.teams[team] = []
        self.teams[team].append(student)

        if student not in self.scores:
            self.scores[student] = 0
            self.breakdowns[student] = []
        student_prefs = self.prefs.get(student)

        if student_prefs is not None and teacher in student_prefs:
            score = int(student_prefs[teacher])
            self.scores[student] += score
        else:
            score = 0

        self.breakdowns[student].append((teacher, team, score))

        return score

    def parse_lp_solve(self, solution_file):
        mode = 'initial'
        constraints = {}

        for line in solution_file.readlines():
            if 'infeasible' in line:
                abort(line)

            m = re.search('Value of objective function:\s+([\d.]+)$', line)
            if m:
                self.objective = int(float(m.group(1)))
                continue

            if 'Actual values of the variables' in line:
                mode = 'variables'
                self.teams = {}
                self.scores = {}
                self.breakdowns = {}
                self.total_score = 0
                continue
            elif 'Actual values of the constraints' in line:
                mode = 'constraints'
                constraints = {}
                continue
            elif 'Objective function limits' in line:
                mode = 'objective function limits'
                continue
            elif 'Improved solution' in line or 'Suboptimal solution' in line:
                print line
                self.teams = {}
                constraints = {}
                self.scores = {}
                self.breakdowns = {}
                self.total_score = 0
                self.objective = None
                continue
            elif 'Sensitivity unknown' in line:
                continue

            if mode == 'variables':
                if re.match('^\s*$', line):
                    continue
                m = re.match('^([A-Za-z_]+[A-Za-z])_(([A-Za-z]+)\d+)\s+([01])$', line)
                if not m:
                    abort("Couldn't parse variables line:\n" + line)
                student, team, teacher, val = m.groups()
                student = student.replace('_', ' ')
                if val == '1':
                    self.total_score += self.assign(student, teacher, team)
            elif mode == 'constraints':
                if re.match('^\s*$', line):
                    continue
                if re.match('^R', line):
                    continue
                m = re.match('^(\w+)_(\w+)\s+(\d+)$', line)
                if not m:
                    abort("Couldn't parse constraints line:\n" + line)
                constraint, team, val = m.groups()
                if constraint not in constraints:
                    constraints[constraint] = {}
                constraints[constraint][team] = val

                m = re.match("^(\w+)_prefs\s+(\d+)", line)
                if m:
                    student, score = m.groups()
                    student = student.replace('_', ' ')
                    # self.scores[student] = int(score)

        if len(self.teams) == 0:
            abort("No teams found in solution\n")

        if self.total_score != self.objective:
            print("WARNING: Total score %d didn't match "
                  "objective function value %s\n" %
                  (self.total_score,
                   "None" if self.objective is None else self.objective))

    def parse_glpsol(self, solution_file):
        awaiting_assignment_line = False

        for line in solution_file.readlines():
            m = re.match("^Objective:\s+all_prefs = (\d+) ", line)
            if m:
                self.objective = int(m.group(1))

            m = re.match("^\s+\d+\sA\['?([^,']+)'?,([^,]+),(\d+)\]$", line)
            if m:
                student, teacher, team_index = m.groups()
                student = student.replace('_', ' ')
                awaiting_assignment_line = True
                continue

            if re.search("SOLUTION IS INFEASIBLE", line):
                abort("Solution is infeasible\n")

            if awaiting_assignment_line:
                # should immediately follow A[...] line
                awaiting_assignment_line = False

                if re.match("^\s+\*\s+1\s+", line):
                    self.total_score += \
                        self.assign(student, teacher,
                                    teacher_team(teacher, int(team_index)))

    def parse_cbc(self, solution_file):
        for line in solution_file.readlines():
            if 'nfeasible' in line:
                abort(line)

            m = re.match("^Stopped on (?:time|iterations) - "
                         "objective value -(\d+\.\d+)$", line)
            if m:
                self.objective = int(float(m.group(1)))

            m = re.match("^Optimal - objective value -(\d+\.\d+)$", line)
            if m:
                self.objective = int(float(m.group(1)))

            m = re.match("^\s*\d+\s+A\(.+\)", line)
            if not m:
                continue

            m = re.match("^\s*\d+\s+A\('?(.+?)'?,([^,]+),(\d+)\)\s+1\s+-?\d+$",
                         line)
            if not m:
                abort("Weird looking line:\n" + line)

            student, teacher, team_index = m.groups()
            student = student.replace('_', ' ')
            student = student.replace('~', '-')
            student = student.replace("''", "'")
            self.total_score += \
                self.assign(student, teacher,
                            teacher_team(teacher, int(team_index)))

    def parse_scip(self, solution_file):
        for line in solution_file.readlines():
            if 'problem is solved [infeasible]' in line:
                abort(line)

            m = re.match("^objective value:\s+(\d+)$", line)
            if m:
                self.objective = int(float(m.group(1)))

            m = re.match("^A\(.+\)", line)
            if not m:
                continue

            m = re.match("^A\('?(.+?)'?,([^,]+),(\d+)\)\s+1\s+\(obj:\d+\)$",
                         line)
            if not m:
                abort("Weird looking line:\n" + line)

            student, teacher, team_index = m.groups()
            student = student.replace('_', ' ')
            student = student.replace('~', '-')
            student = student.replace("''", "'")
            self.total_score += \
                self.assign(student, teacher,
                            teacher_team(teacher, int(team_index)))

    def report(self):
        print "Report for solver: %s" % self.solver

        self.report_by_name()


if __name__ == '__main__':
    main()
