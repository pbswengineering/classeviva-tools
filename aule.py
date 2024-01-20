from datetime import datetime
import os
import json
from sys import argv, exit
from time import time

from pdf2image import convert_from_path
from pytesseract import image_to_string


def import_pdf(pdf_file):
    """
    Import a PDF school class timetable.
    """

    DPI = 300
    SCALE = DPI / 100
    TOP = (76 * SCALE, 95 * SCALE)
    SIZE = ((255 - 76 + 1) * SCALE, (210 - 95 + 1) * SCALE)
    DAYS = 6
    HOURS = 13
    TOP_ROOM = (128 * SCALE, 46 * SCALE)
    SIZE_ROOM = (170 * SCALE, 14 * SCALE)

    start = time()
    print("Importing PDF timetable...")
    images = convert_from_path(pdf_file, dpi=DPI)
    end = time()
    print(f"Timetable imported in {end - start:.1f} seconds.")

    start = time()
    print("Parsing PDF pages...")
    rooms = {}
    for i, image in enumerate(images):
        print("PDF page", i)
        room_img = image.crop((TOP_ROOM[0], TOP_ROOM[1], TOP_ROOM[0] + SIZE_ROOM[0], TOP_ROOM[1] + SIZE_ROOM[1]))
        room_str = image_to_string(room_img).strip()
        day_list = []
        for day in range(DAYS):
            hour_list = []
            for hour in range(HOURS):
                x1 = TOP[0] + SIZE[0] * day
                y1 = TOP[1] + SIZE[1] * hour
                x2 = x1 + SIZE[0]
                y2 = y1 + SIZE[1]
                cell = image.crop((x1 + 1, y1 + 1, x2 - 1, y2 - 1))   # Account for the black border
                cell_str = image_to_string(cell).strip()
                hour_list.append(cell_str)
            day_list.append(hour_list)
        rooms[room_str] = day_list
    end = time()
    print(f"Pages parsed in {end - start:.1f} seconds.")
    return rooms

def get_hour(dt):
    """
    Convert a timestamp in a school hour (0 - first, 1 - second, 2 third...)
    """
    mi = dt.hour * 60 + dt.minute
    if 8 * 60 <= mi < 9 * 60:
        return 0
    elif 9 * 60 <= mi < 10 * 60:
        return 1
    elif 10 * 60 <= mi < 11 * 60:
        return 2
    elif 11 * 60 <= mi < 12 * 60:
        return 3
    elif 12 * 60 <= mi < 13 * 60:
        return 4
    elif 13 * 60 <= mi < 13 * 60 + 50:
        return 5
    else:
        return -1

def find_free_room(timetable, day, hour):
    """
    Find a free class on the specified day and time
    """
    found = []
    for room, days in timetable.items():
        if "" == days[day][hour]:
            found.append(room)
    return found


def find_matches(timetable, day, hour, text):
    """
    Find a class whose description contains the given text
    """
    found = []
    now_wday = datetime.now().weekday()
    for room, days in timetable.items():
        for h in range(6):
            if text.lower() in days[day][h].lower():
                cls = days[day][h].split("\n")[0]
                if h == hour and day == now_wday:
                    found.append(f"{h+1} {room} {cls} <---")
                else:
                    found.append(f"{h+1} {room} {cls}")
    return found


if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    if not os.path.exists("timetable.json"):
        print("timetable.json doesn't exist, it must be created from scratch.")
        pdf_file = input("PDF FILE: ")
        timetable = import_pdf(pdf_file)
        with open("timetable.json", "w") as f:
            json.dump(timetable, f)
    else:
        print("timetable.json found.")
        with open("timetable.json", "r") as f:
            timetable = json.load(f)
    
    if len(argv) == 1:
        print("Usage: aule.py <COMMAND>")
        print('\n   COMMAND: <"some prof. name"> [day 1-6]')
        print('   COMMAND: free [day 1-6] [hh:mm]\n')
        exit(1)
    
    command = argv[1]
    now = datetime.now()
    if len(argv) == 4:
        user_time = datetime.strptime(argv[3], "%H:%M")
        now = now.replace(hour=user_time.hour, minute=user_time.minute)
    hour = get_hour(now)
    if len(argv) == 3:
        day = int(argv[2]) - 1
    else:
        day = now.weekday()
    if command == "free":
        free_rooms = find_free_room(timetable, day, hour)
        print("\n".join(sorted(free_rooms)))
    else:
        text = argv[1]
        matches = find_matches(timetable, day, hour, text)
        if matches:
            print("\n".join(sorted(matches)))
        else:
            print("Not found.")
