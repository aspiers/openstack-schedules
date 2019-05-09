===============================
openstack/schedules
===============================

This repository contains data and algorithms for creating schedules
for events such as the OpenStack PTG.

* Free software: Apache license
* Documentation: https://docs.openstack.org/schedules/latest
* Source: https://opendev.org/openstack/schedules Bugs: https://storyboard.openstack.org/#!/project/schedules

Installation
============

* Install the `COIN-OR Branch-and-Cut solver
  <https://github.com/coin-or/Cbc>`_ under ``solvers/``.

* Modify ``CBC`` and ``CBC_LIBRARY_PATH`` in ``Makefile`` to point to your
  `cbc` installation.

* Make sure you have Python 3 on your ``$PATH``.

* Type ``make prep``.

Usage
=====

* Type ``make``.
