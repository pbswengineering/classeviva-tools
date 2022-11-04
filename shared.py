# -*- coding: utf-8 -*-
#
# Classes and functions for web-based scraping of
# Spaggiari's Classeviva.
#
# The whole scraping is based on the website, even
# though they also have a REST API, since I coudln't
# find any documentation for the latter. Obviously
# this also means that the whole scraper is rather
# fragile, but the thrill is worth it. :-D
#

from datetime import datetime
from typing import Callable, List, Optional, Union

import requests
from bs4 import BeautifulSoup, Tag  # type: ignore

from settings import *


class Subject:
    """
    A subject matter taught on a specific class
    (e.g. Computer Science on 1A).
    """

    def __init__(self):
        self.class_ = ""
        self.class_description = ""
        self.subject = ""
        self.url = ""
        self.url_grades = ""
        self.url_grades_term = []
        self.url_tests_term = []

    def __str__(self) -> str:
        return f"{self.class_} ({self.class_description}) - {self.subject}"


class Class:
    """
    A class (year number and section letter, e.g. 4A)
    """

    def __init__(self):
        self.name = ""
        self.code = ""
    
    def __str(self) -> str:
        return self.name

class Student:
    """
    A student's personal data.
    """

    def __init__(self):
        self.name = ""
        self.birthday = None

    def __str__(self) -> str:
        return f"{self.name} ({self.birthday.strftime('%Y-%m-%d')})"


class Grade:
    """
    A grade in a specific subject.
    """

    subject: str
    grade: Optional[float]

    def __init__(self):
        self.subject = ""
        self.grade = None

    def sanitized_subject(self) -> str:
        if self.subject == "educazione civica":
            return "ed civica"
        if "francese" in self.subject:
            return "francese"
        if "inglese" in self.subject:
            return "inglese"
        if "spagnolo" in self.subject:
            return "spagnolo"
        if "tecnologie informatiche" in self.subject:
            return "lab. informatica"
        if "integrate" in self.subject and "fisica" in self.subject:
            return "fisica"
        if "integrate" in self.subject and "terra" in self.subject:
            return "sc. della terra"
        if "letteratura" in self.subject:
            return "itaiano"
        if "motorie" in self.subject:
            return "ed. fisica"
        if "aziendale" in self.subject:
            return "ec. aziendale"
        if self.subject == "economia politica":
            return "ec. politica"
        if "cattolica" in self.subject:
            return "religione"
        return self.subject


class StudentGrades:
    """
    List of grades of a specific students for a specific subject.
    """

    grades: List[Union[Optional[int], Grade]]

    def __init__(self, student: Student):
        self.student = student
        self.grades = []

    def __str__(self) -> str:
        return f"{self.student.name} -> {' '.join(str(g) for g in self.grades)}"


class CompetenceLevel:
    """
    List of competence levels of a specific class. Each competence level
    is characterized by a name (e.g. "Below sufficiency (<=4)", a function
    int -> bool that tests whether or not a score belongs to this level,
    a counter and a percentage indicator (these two values are meant to
    be managed by a function that computes them).
    """

    def __init__(self, name: str, test_function: Callable[[int], bool]):
        self.name = name
        self.count = 0
        self.perc = 0
        self.test_function = test_function

    def __str__(self):
        return f"{self.name} {self.perc}% ({self.count})"


class ClasseViva:
    def __init__(self, username: str, password: str):
        self.session = requests.session()
        res = self.session.get("https://web.spaggiari.eu/home/app/default/login.php?target=cvv&mode=")
        res.raise_for_status()
        res = self.session.post(
            "https://web.spaggiari.eu/auth-p7/app/default/AuthApi4.php?a=aLoginPwd",
            data={
                "uid": username,
                "pwd": password,
                "cid": "",
                "pin": "",
                "target": "",
            },
        )
        res.raise_for_status()
        res = self.session.post("https://web.spaggiari.eu/home/app/default/login_ok_redirect.php")
        res.raise_for_status()
    
    def get_classes(self) -> Class:
        """
        Return the list of the classes available for the current login,
        if the login is a coordinator.
        """
        res = self.session.get("https://web.spaggiari.eu/cvv/app/default/gioprof_coordinatore.php")
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        tables = [t for t in soup.find_all("table") if "Valutazioni" in t.get_text()]
        if not tables:
            raise Exception("Table of classes not found")
        rows = tables[0].find_all("tr", {"valign": "top"})[1:]
        classes = []
        for row in rows:
            tds = row.find_all("td")
            c = Class()
            c.name = tds[0].get_text().strip()
            a_chrono = tds[3].find("a")
            # e.g. https://web.spaggiari.eu/cvv/app/default/programma_struttura.php?classe_id=1248202
            c.code = a_chrono["href"].split("=")[1].strip()
            classes.append(c)
        return classes


    def get_subjects(self) -> List[Subject]:
        """
        Return the list of subject available for the current login.
        """
        res = self.session.get("https://web.spaggiari.eu/cvv/app/default/gioprof_selezione.php")
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        tables = [t for t in soup.find_all("table") if "Giornale del professore" in t.get_text()]
        if not tables:
            raise Exception("Table of classes not found")
        rows = tables[0].find_all("tr", {"valign": "top"})[1:]  # The first row is the header
        subjects = []
        for row in rows:
            tds = row.find_all("td")
            s = Subject()
            a_class = tds[0].find("a")
            s.class_ = a_class.get_text().strip()
            s.url = "https://web.spaggiari.eu/cvv/app/default/" + a_class["href"]
            s.url_grades = s.url.replace("/regclasse.php", "/regvoti.php")
            s.class_description = tds[1].find("p")["title"].strip()
            s.subject = tds[2].find("div").find("div").find("div")["title"].strip()
            if not s.class_:
                s.class_ = s.class_description  # Fix for groups such as 3B_AFM, 3B_SIA
            subjects.append(s)
        return subjects
    
    def get_avg_grades(self, class_: Class, term: str) -> List[StudentGrades]:
        res = self.session.get(f"https://web.spaggiari.eu/cvv/app/default/coordinatore_medie.php?classe_id={class_.code}&quad={term}")
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        ths = soup.find_all("th", {"class": "materia"})
        subjects = [th.get_text().strip() for th in ths if isinstance(th, Tag)]
        tables = soup.find_all("table", {"id": "center_table"})
        # Student names
        tbody = tables[0].find("tbody")
        trs = tbody.find_all("tr")
        students = []
        for tr in trs:
            td = tr.find("td")
            s = Student()
            s.name = "".join(c for c in td.get_text() if c.isalpha() or c == " ").strip()
            students.append(s)
        # Grades
        tbody = tables[1].find("tbody")
        trs = tbody.find_all("tr")
        student_grades = []
        for k, tr in enumerate(trs):
            tds = tr.find_all("td", {"class": "registro"})
            if not tds:
                continue
            scores = [td.get_text().strip() for td in tds if isinstance(td, Tag)]
            s = StudentGrades(students[k])
            for i in range(len(subjects)):
                g = Grade()
                g.subject = subjects[i].replace(".", "").strip()
                g.grade = scores[i] and float(scores[i]) or None
                s.grades.append(g)
            student_grades.append(s)
        return student_grades

    def get_students(self, subject: Subject) -> List[Student]:
        """
        Return the list of the students for a specific subject.
        """
        res = self.session.get(subject.url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        students = []
        for td in soup.find_all("td", {"class": "elenco_studenti"}):
            s = Student()
            divs = td.find_all("div")
            s.name = divs[0].get_text().strip()
            bday_str = divs[1].get_text().strip()
            bday_str = bday_str.split(" ")[0]  # Fix for groups such as 3B_SIA, 3B_AFM
            s.birthday = datetime.strptime(bday_str, "%d-%m-%Y")
            students.append(s)
        return students

    def _get_grades_urls(self, subject: Subject):
        """
        Detect the URLs to access the various grade pages for a
        specific subject.
        """
        res = self.session.get(subject.url_grades)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        subject.url_grades_term = []
        for span in soup.find_all("span"):
            try:
                href = span["_href"]
                if not "comp=" in href:
                    url = "https://web.spaggiari.eu/cvv/app/default/" + href
                    subject.url_grades_term.append(url)
                    subject.url_tests_term.append(url.replace("/regvoti.php", "/recuperi_docente.php"))
            except KeyError:
                pass

    def get_tests(self, subject: Subject, students: List[Student], term: int) -> List[StudentGrades]:
        """
        Returns the StudentGrades (list of grades associated to a specific
        student) of each student for a specific test.
        """
        if not subject.url_grades_term or not subject.url_tests_term:
            self._get_grades_urls(subject)
        url = subject.url_tests_term[term]
        res = self.session.get(url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        main_container = soup.find("div", {"class": "main-container"})
        table = main_container.find("table")
        trs = table.find_all("tr")[1:]  # The first row is the header
        tests = []
        for i, tr in enumerate(trs):
            tds = tr.find_all("td")[0:]  # The first cell is the student's name
            grades = StudentGrades(students[i])
            for td in tds:
                p = td.find("p")
                if not p:
                    continue
                try:
                    grade = int(p.get_text())
                    grades.grades.append(grade)
                except ValueError:
                    grades.grades.append(None)
            tests.append(grades)
        return tests

    def compute_competence_levels(
        self,
        competencies: List[CompetenceLevel],
        grades: List[StudentGrades],
        count: int,
    ) -> Optional[List[Student]]:
        """
        Compute score counts and threshold percentages for the specified competencies
        (used to calculate the score levels percentages of the entry tests results).
        Each CompetenceLevel in the competencies argument will be modified with respect to
        the count and perc fields (perc will always be an int and the overall sum will
        always be 100). The function returns the students that didn't take the test.
        """
        tot = 0
        missing_students = []
        for g in grades:
            score = g.grades[count]
            if score is not None:
                tot += 1
                for c in competencies:
                    if c.test_function(score):
                        c.count += 1
            else:
                missing_students.append(g.student)
        if tot == 0:
            return None
        max_perc = 0
        sum_perc = 0
        max_perc_idx = -1
        for i, c in enumerate(competencies):
            c.perc = c.count * 100 // tot
            sum_perc += c.perc
            if c.perc > max_perc:
                max_perc = c.perc
                max_perc_idx = i
        # If the sum isn't exactly 100, adjust the highest percentage
        if sum_perc < 100:
            competencies[max_perc_idx].perc += 100 - sum_perc
        return missing_students
