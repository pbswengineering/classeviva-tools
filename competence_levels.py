# -*- coding: utf-8 -*-
#
# Compute the percentages of the competence levels for
# the specified test (0-based counter) of the specified
# term (0-based counter).
#
# Such competence levels are:
#   1) Printed on the console
#   2) Saved into an HTML file
#   3) Saved into several PDF files (one per subject/class)
#

import os
from sys import argv, exit
import webbrowser

from fpdf import FPDF  # type: ignore

from shared import *


if __name__ == "__main__":
    try:
        term_index = int(argv[1])
        test_index = int(argv[2])
    except:
        print("\nUsage: python competence_levels.py TERM_INDEX TEST_INDEX")
        print("\nPlease note that both TERM_INDEX and TEST_INDEX are 0-based indices\n")
        exit(1)
    cv = ClasseViva(USERNAME, PASSWORD)
    subjects = cv.get_subjects()
    out_dir = os.path.join(os.getcwd(), "reports")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    html_file = os.path.join(out_dir, "out.html")
    with open(html_file, "w") as f:
        f.write("<style>td,th{border:1px solid black}</style>")
        f.write("<h1>Competence levels</h1>")
        for subject in subjects:
            f.write(f"<h2>{subject}</h2>")
            students = cv.get_students(subject)
            grades = cv.get_tests(subject, students, term_index)
            competencies = [
                CompetenceLevel("Competenza non sufficiente (<= 4)", lambda x: x <= 4),
                CompetenceLevel("Competenza base (5, 6)", lambda x: x > 4 and x <= 6),
                CompetenceLevel("Competenza intermedia (7, 8)", lambda x: x > 6 and x <= 8),
                CompetenceLevel("Competenza avanzata (9, 10)", lambda x: x > 8),
            ]
            missing = cv.compute_competence_levels(competencies, grades, test_index)

            # Output the result to the screen
            print(subject.class_, "\n")
            print("\n".join(str(c) for c in competencies))
            print("\nMissing students:")
            print("\n".join(s.name for s in missing))
            print(50 * "-")

            # Output the result to an HTML file
            f.write("<table><tr>")
            for c in competencies:
                f.write(f"<th>{c.name}</th>")
            f.write("</tr><tr>")
            for c in competencies:
                f.write(f"<td>{c.perc}%</td>")
            f.write("</tr></table>")
            f.write(f"<strong>Missing students ({len(missing)}):</strong> " + ", ".join(s.name for s in missing))

            # Output the result to a PDF file
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=18)
            # create a cell
            pdf.cell(200, 10, txt=f"Risultati test di ingresso", ln=1, align="L")
            pdf.set_font("Arial", size=14)
            pdf.cell(200, 20, txt=f"{subject.class_} - {subject.subject}", ln=1, align="L")
            for i, c in enumerate(competencies):
                pdf.cell(200, 10, txt=f"{c.name} = {c.perc}%", ln=1, align="L")
            pdf.output(os.path.join(out_dir, f"{subject.subject} - {subject.class_}.pdf"))

            print(f"The competence levels have also been saved in HTML and PDF format in the {out_dir} directory")

    webbrowser.open(f"file://{html_file}")
