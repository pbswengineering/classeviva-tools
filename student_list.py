# -*- coding: utf-8 -*-
#
# List the student names of the specified class
#

import argparse
from datetime import datetime
from sys import exit

from shared import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("section")
    parser.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )
    args = parser.parse_args()
    class_ = args.section.upper()
    cv = ClasseViva(USERNAME, PASSWORD)
    clazz = [c for c in cv.get_all_classes() if c.name == class_]
    if not clazz:
        print("Classe non trovata")
        exit(1)
    today = datetime.now()
    students = cv.get_students_by_class(clazz[0])
    for student in students:
        if args.verbose:
            age = (
                today - student.birthday
            ).days // 365  # Not really pretty, but it works
            print(student.name, age, student.birthday.strftime("%Y-%m-%d"))
        else:
            print(student.name)
