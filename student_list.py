# -*- coding: utf-8 -*-
#
# List the student names of the specified class
#

from datetime import datetime
from sys import argv, exit

from shared import *


if __name__ == "__main__":
    try:
        class_ = argv[1].strip()
    except:
        print("\nUsage: python student_list.py CLASS_NAME")
        print("\nClass name is something such as '1A', it must be the same as in the gradebook\n")
        exit(1)
    cv = ClasseViva(USERNAME, PASSWORD)
    subjects = cv.get_subjects()
    for subject in subjects:
        if subject.class_ != class_:
            continue
        students = cv.get_students(subject)
    today = datetime.now()
    for student in students:
        age = (today - student.birthday).days // 365  # Not really pretty, but it works
        print(student.name, age, student.birthday.strftime("%Y-%m-%d"))