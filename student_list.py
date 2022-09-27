# -*- coding: utf-8 -*-
#
# List the student names of the specified class
#

import argparse
from datetime import datetime
from sys import argv, exit

from shared import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("section")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    args = parser.parse_args()
    class_ = args.section
    cv = ClasseViva(USERNAME, PASSWORD)
    subjects = cv.get_subjects()
    for subject in subjects:
        if subject.class_ != class_:
            continue
        students = cv.get_students(subject)
    today = datetime.now()
    for student in students:
        if args.verbose:
            age = (today - student.birthday).days // 365  # Not really pretty, but it works
            print(student.name, age, student.birthday.strftime("%Y-%m-%d"))
        else:
            print(student.name)