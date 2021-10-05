<a href="https://www.bernardi.cloud/">
    <img src=".readme-files/classeviva-tools-logo-72.png" alt="ClasseViva Tools logo" title="ClasseViva Tools" align="right" height="72" />
</a>

# ClasseViva Tools
> Command line tools to simplify the work of teachers on the ClasseViva (Spaggiari) online gradebook.

[![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/github/license/pbswengineering/classeviva-tools.svg)](https://opensource.org/licenses/AGPL-3.0)
[![GitHub issues](https://img.shields.io/github/issues/pbswengineering/classeviva-tools.svg)](https://github.com/pbswengineering/classeviva-tools/issues)

## Table of contents

- [Why ClasseViva Tools](#why-classeviva-tools)
- [Usage](#usage)
- [License](#license)

## Why ClasseViva Tools

Because my current main job is teaching. :-)

## Usage

Firstly, create a `settings.py` file by cloning the `settings.py.sample` file and replacing user name and password with your actual credentials.

### Competence Levels

Usage: `python competence_levels.py TERM_INDEX TEST_INDEX`

This tool creates an on-screen, HTML and PDF report of the competence levels for the specified test; the reports are saved in the `reports` directory.

## License

ClasseViva tools is licensed under the terms of the GNU Affero General Public License version 3.

## ACHTUNG

I've implemented ClasseViva tools as a web scraper, rather then using Spaggiari's REST API, as I coulnd't find its documentation (and, honestly, I didn't have much time to guess how it worked). Obviously, this design choice might (will) backfire spectacularly with time. Oh well. :-)
