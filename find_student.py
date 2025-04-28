# -*- coding: utf-8 -*-
#
# List the student names of the specified class
#

import argparse

from shared import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )
    args = parser.parse_args()
    partial_name = args.name.upper()
    cv = ClasseViva(USERNAME, PASSWORD)
    classes = cv.get_all_classes()
    for c in classes:
        print(c.name)
        students = cv.get_students_by_class(c)
        for s in students:
            if partial_name in s.name:
                print(f"   --->   {s}")
