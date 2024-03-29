# -*- coding: utf-8 -*-
#
# Shows the grades for the students of the specified class
#

import argparse
import os
from sys import exit

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
    bad_grades_by_subject = {}
    for sg in student_grades:
        bg = sg.bad_grades(subject_only=True)
        for subject in bg[1]:
            if subject in bad_grades_by_subject:
                bad_grades_by_subject[subject] += 1
            else:
                bad_grades_by_subject[subject] = 1
    bad_grades_by_subject = dict(reversed(sorted(bad_grades_by_subject.items(), key=lambda item: item[1])))
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
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css">
    <style>
    h1 {{
        margin-top: 1em;
    }}
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
    <h1>Insufficient grades by subject</h1>
    <div class="row row-cols-1 g-4">
        <canvas id="bad-grades-by-subject"></canvas>
    </div>
    <h1>Student performance</h1>
""")
        COLS_PER_ROW = 3
        students = []
        for i, sg in enumerate(student_grades):
            students.append(f"{i+1}. {sg.student.name.upper()}")
            if (i % COLS_PER_ROW) == 0:
                f.write(f'<div class="row row-cols-md-1 row-cols-lg-{COLS_PER_ROW} g-4">')
            css_border = ""
            css_text = ""
            avg = sg.avg()
            if avg is None:
                avg_str = ""
            else:
                avg_str = f"{avg:.1f}"
            bad_str = ""
            bad_grades, bad_subjects = sg.bad_grades(4, 5.5)
            bad_subjects = [bs.replace(" ", "&nbsp;") for bs in bad_subjects]
            if bad_grades is not None and bad_grades > 0:
                css_border = " border-danger"
                css_text = " text-danger"
                bad_str += f"<br>{bad_grades} insufficient grade{bad_grades > 1 and 's' or ''}: {', '.join(bad_subjects)}"
            very_bad_grades, very_bad_subjects = sg.bad_grades(-1, 4)
            very_bad_subjects = [vbs.replace(" ", "&nbsp;") for vbs in very_bad_subjects]
            if very_bad_grades is not None and very_bad_grades > 0:
                css_border = " border-danger"
                css_text = " text-danger"
                bad_str += f"<br>{very_bad_grades} very bad grade{very_bad_grades > 1 and 's' or ''}: {', '.join(very_bad_subjects)}"
            if avg >= 8:
                css_border = " border-success"
                css_text = " text-success"
            f.write(f"""
<div class="col">
    <div class="card{css_border}{css_text}">
        <div class="card-header{css_border}{css_text}">
            {i+1}. {sg.student.name.upper()}
            <i class="bi bi-zoom-in" onclick="zoomGrades({i}, '{i+1}. {sg.student.name.upper()}')"></i>
        </div>
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
        students_js = "[" + ",".join(f'"{x}"' for x in students) + "]";
        f.write("""
</div> <!-- .container -->
<div class="modal fade" id="gradesModal" tabindex="-1" aria-labelledby="gradesModalLabel" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h1 class="modal-title fs-5" id="gradesModalLabel">Modal title</h1>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <div class="dropdown">
        <button class="btn btn-secondary dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
        Compare with...
        </button>&nbsp;&nbsp;&nbsp;<span id="gradesModalCompareLabel"></span>
        <ul class="dropdown-menu">""" +
        "\n".join(f'''<li><a class="dropdown-item" href="#" onclick="compareWith({i}, '{x}')">{x}</a></li>''' for i, x in enumerate(students)) +
        """</ul></div>
        <canvas id="gradesModalCanvas"></canvas>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-OERcA2EqjJCMA+/3y+gxIOqMEjwtxJY7qPCqsdltbNJuaOe923+mo//f6V8Qbsw3" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
let students = """ + students_js + """
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
function studentChart(i, cssId, compare) {
    currentStudent = i;
    let d = JSON.parse(JSON.stringify(data[i])); // deep copy
    d.datasets[0]["pointBackgroundColor"] = gradePointColor;
    d.datasets[0]["pointRadius"] = gradePointRadius;
    if (typeof compare !== "undefined") {
        let newd = JSON.parse(JSON.stringify(data[compare].datasets[0])); // deep copy
        newd["pointBackgroundColor"] = gradePointColor;
        newd["pointRadius"] = gradePointRadius;
        newd["backgroundColor"] = 'rgba(255, 99, 132, 0.2)';
        newd["borderColor"] = 'rgb(255, 99, 132)';
        newd["pointHoverBorderColor"] = 'rgb(255, 99, 132)';
        d.datasets.push(newd);
    }
    let config = {
        type: 'radar',
        data: d,
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
    return new Chart(document.getElementById(cssId), config);
}
function destroyGradesModalChart() {
    if (typeof gradesModalChart !== "undefined")
        gradesModalChart.destroy();
}
function compareWith(i, name) {
    destroyGradesModalChart();
    gradesModalChart = studentChart(currentStudent, "gradesModalCanvas", i);
    let gradesModalCompareLabel = document.getElementById("gradesModalCompareLabel");
    gradesModalCompareLabel.innerHTML = name;
}
function zoomGrades(i, title) {
    destroyGradesModalChart();
    var gradesModal = new bootstrap.Modal(document.getElementById("gradesModal"), {});
    gradesModal.show();
    gradesModalChart = studentChart(i, 'gradesModalCanvas');
    let gradesModalLabel = document.getElementById("gradesModalLabel");
    gradesModalLabel.innerHTML = title;
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
    studentChart(i, 'student_' + i);
})();
new Chart(document.getElementById("bad-grades-by-subject"), {
    type: 'bar',
    data: {
      labels: [""" + ",".join(f'"{x}"' for x in bad_grades_by_subject.keys()) + """],
      datasets: [
        {
          label: "Bad grades",
          backgroundColor: 'rgb(54, 162, 235)',
          data: [""" + ",".join(str(x) for x in bad_grades_by_subject.values()) + """]
        }
      ]
    },
    options: {
      indexAxis: 'y',
      plugins: {
        legend: { display: false },
        title: { display: false },
      }
    }
});
</script></body></html>""")
    print("Output saved as", outfile)
