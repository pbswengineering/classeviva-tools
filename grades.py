# -*- coding: utf-8 -*-
#
# Shows the grades for the students of the specified class
#

import argparse
from datetime import datetime
import os
from sys import argv, exit

from shared import *


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("section")
    parser.add_argument("term")
    args = parser.parse_args()
    class_ = args.section
    term = args.term
    cv = ClasseViva(USERNAME, PASSWORD)
    classes = [c for c in cv.get_classes() if c.name == class_]
    if not classes:
        print("Section not found:", class_)
        exit(1)
    c = classes[0]
    student_grades = cv.get_avg_grades(c, term)
    if not os.path.exists("reports"):
        os.mkdir("reports")
    outfile = os.path.join("reports", "grades_" + class_ + ".html")
    with open(outfile, "w") as f:
        f.write(f"""<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{class_} grade charts</title>
    <!-- http://meyerweb.com/eric/tools/css/reset/ -->
    <link rel="stylesheet" href="css/reset/reset.css">
    <!--[if lt IE 9]>
      <script src="//html5shiv.googlecode.com/svn/trunk/html5.js" type="text/javascript"></script>
    <![endif]-->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-Zenh87qX5JnK2Jl0vWa8Ck2rdkQ2Bzep5IDxbcnCeuOxjzrPF/et3URy9Bv1WTRi" crossorigin="anonymous">
    <style>
    .card {{
        margin-top: 1em;
    }}
    </style>
  </head>
  <body> 
<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
  <div class="container">
    <a class="navbar-brand" href="#">
        <img alt="Logo" width="28" height="33" class="d-inline-block align-text-top" src="https://www.bernardi.cloud/school/cc.png">
        {class_} GRADE CHARTS
    </a>
  </div>
</nav>
  <div class="container text-center">
""")
        COLS_PER_ROW = 3
        for i, sg in enumerate(student_grades):
            if (i % COLS_PER_ROW) == 0:
                f.write(f'<div class="row row-cols-md-1 row-cols-lg-{COLS_PER_ROW} g-4">')
            css_border = ""
            css_text = ""
            avg = sg.avg()
            if avg is None:
                avg_str = ""
            else:
                avg_str = f"{avg:.1f}"
            bad_grades, bad_subjects = sg.bad_grades()
            bad_subjects = [bs.replace(" ", "&nbsp;") for bs in bad_subjects]
            if bad_grades is not None and bad_grades > 0:
                css_border = " border-danger"
                css_text = " text-danger"
                bad_str = f"<br>Insufficient grades: {bad_grades} ({', '.join(bad_subjects)})"
            else:
                bad_str = ""
            if avg >= 8:
                css_border = " border-success"
                css_text = " text-success"
            f.write(f"""
<div class="col">
    <div class="card{css_border}{css_text}">
        <div class="card-header{css_border}{css_text}">{i+1}. {sg.student.name.upper()}</div>
        <div class="card-body{css_border}{css_text}"><canvas id="student_{i}"></canvas></div>
        <div class="card-footer{css_border}{css_text}">
        Average: {avg_str}{bad_str} 
        </div>
    </div>
</div>
""")
            if (i % COLS_PER_ROW) == (COLS_PER_ROW - 1):
                f.write("</div>")
        # Close the last row, if needed
        if ((len(student_grades) - 1) % COLS_PER_ROW) != (COLS_PER_ROW - 1):
            f.write("</div>")
        f.write("""
</div> <!-- .container -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-OERcA2EqjJCMA+/3y+gxIOqMEjwtxJY7qPCqsdltbNJuaOe923+mo//f6V8Qbsw3" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
function gradePointColor(ctx) {
    if (ctx.raw > 0 && ctx.raw < 5.5)
        return 'rgb(255, 99, 132)';
    else
        return 'rgb(54, 162, 235)';
}
function gradePointRadius(ctx) {
    if (ctx.raw > 0 && ctx.raw < 5.5)
        return 8;
    else
        return 4;
}
let data = [];
""")
        for i, sg in enumerate(student_grades):
            labels = ['"' + g.sanitized_subject() + '"' for g in sg.grades]
            scores = [f"{g.grade and g.grade or 0}" for g in sg.grades]
            f.write("""
data.push({
    labels: [""" + ",".join(labels) + """],
    datasets: [{
        data: [""" + ",".join(scores) + """],
        fill: true,
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgb(54, 162, 235)',
        pointBackgroundColor: gradePointColor,
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(54, 162, 235)',
        pointRadius: gradePointRadius
    }]
})
""")
        f.write("""
for (let i = 0; i < data.length; ++i) (function () {
    let config = {
        type: 'radar',
        data: data[i],
        options: {
            elements: {line: {borderWidth: 3}},
            plugins: {
                legend: {display: false}
            },
            scales: {
                r: {
                    suggestedMin: 0,
                    suggestedMax: 10
                }
            },
        }
    };
    new Chart(document.getElementById('student_' + i), config);
})();
</script></body></html>""")
    print("Output saved as", outfile)
