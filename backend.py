"""Backend for the SMCII Grade Calculation Performance System."""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "smcii_data.json")

TERM_NAMES = ["Prelim", "Midterm", "Semifinal", "Finals"]

ASSESSMENT_NAMES = [
    "activities",
    "quizzes",
    "performance_tasks",
    "exams",
]

ASSESSMENT_LABELS = {
    "activities": "Activities",
    "quizzes": "Quizzes",
    "performance_tasks": "Performance Tasks",
    "exams": "Exams",
}


def empty_store():
    return {"users": [], "grades": []}


def load_data():
    if not os.path.exists(DATA_FILE):
        return empty_store()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            saved_data = json.load(file)

        if not isinstance(saved_data, dict):
            return empty_store()

        users = saved_data.get("users", [])
        grades = saved_data.get("grades", [])

        if not isinstance(users, list):
            users = []

        if not isinstance(grades, list):
            grades = []

        return {
            "users": users,
            "grades": grades
        }

    except (OSError, json.JSONDecodeError):
        return empty_store()


data_store = load_data()


def save_data():
    temporary_file = DATA_FILE + ".tmp"

    with open(temporary_file, "w", encoding="utf-8") as file:
        json.dump(
            data_store,
            file,
            indent=4,
            ensure_ascii=False
        )

    os.replace(temporary_file, DATA_FILE)


def next_id(items):
    ids = [
        item.get("id", 0)
        for item in items
        if isinstance(item, dict)
        and isinstance(item.get("id", 0), int)
    ]

    return max(ids, default=0) + 1


def create_default_user(username, password, role, full_name):
    for user in data_store["users"]:
        if user.get("username", "").lower() == username.lower():
            return

    user = {
        "id": next_id(data_store["users"]),
        "username": username,
        "password": password,
        "role": role,
        "full_name": full_name
    }

    data_store["users"].append(user)

    try:
        save_data()
    except OSError:
        data_store["users"].remove(user)
        raise


def ensure_default_users():
    defaults = [
        (
            "admin",
            "admin123",
            "Admin",
            "System Administrator"
        ),
        (
            "teacher",
            "teacher123",
            "Teacher",
            "SMCII Teacher"
        ),
        (
            "student",
            "student123",
            "Student",
            "Sample Student"
        )
    ]

    for username, password, role, full_name in defaults:
        create_default_user(
            username,
            password,
            role,
            full_name
        )


def authenticate_user(username, password, role):
    username = username.strip().lower()
    password = password.strip()
    role = role.strip().lower()

    for user in data_store["users"]:
        if (
            user.get("username", "").lower() == username
            and user.get("password", "") == password
            and user.get("role", "").lower() == role
        ):
            return user

    return None


def add_user(username, password, full_name, role):
    username = username.strip()
    password = password.strip()
    full_name = full_name.strip()
    role = role.strip()

    if not username or not password or not full_name or not role:
        return False, "Please complete all account fields."

    if role not in ("Admin", "Teacher", "Student"):
        return False, "Please select a valid account role."

    for user in data_store["users"]:
        if user.get("username", "").lower() == username.lower():
            return False, "This username already exists."

    new_user = {
        "id": next_id(data_store["users"]),
        "username": username,
        "password": password,
        "full_name": full_name,
        "role": role
    }

    data_store["users"].append(new_user)

    try:
        save_data()
        return True, "Account created successfully."

    except OSError as error:
        data_store["users"].remove(new_user)
        return False, f"Unable to save account: {error}"


def validate_assessments(assessments):
    if not isinstance(assessments, dict):
        return None, "Assessment scores are missing."

    cleaned = {}

    for term in TERM_NAMES:
        term_data = assessments.get(term)

        if not isinstance(term_data, dict):
            return None, f"Missing assessment scores for {term}."

        cleaned[term] = {}

        for key in ASSESSMENT_NAMES:
            try:
                score = float(term_data[key])
            except (KeyError, TypeError, ValueError):
                return None, (
                    f"Enter a valid {ASSESSMENT_LABELS[key]} "
                    f"score for {term}."
                )

            if score < 0 or score > 100:
                return None, (
                    f"{ASSESSMENT_LABELS[key]} scores "
                    "must be between 0 and 100."
                )

            cleaned[term][key] = score

        cleaned[term]["term_grade"] = round(
            sum(
                cleaned[term][key]
                for key in ASSESSMENT_NAMES
            ) / len(ASSESSMENT_NAMES),
            2
        )

    return cleaned, None


def add_grade(
    student_username,
    subject,
    assessments,
    teacher_username=""
):
    student_username = student_username.strip()
    subject = subject.strip()

    if not student_username or not subject:
        return False, "Enter the student username and subject."

    student = next(
        (
            user for user in data_store["users"]
            if user.get("username", "").lower()
            == student_username.lower()
            and user.get("role", "").lower() == "student"
        ),
        None
    )

    if student is None:
        return False, "Student account not found."

    cleaned, error = validate_assessments(assessments)

    if error:
        return False, error

    overall_grade = round(
        sum(
            cleaned[term]["term_grade"]
            for term in TERM_NAMES
        ) / len(TERM_NAMES),
        2
    )

    record = {
        "id": next_id(data_store["grades"]),
        "student_username": student["username"],
        "subject": subject,
        "teacher_username": teacher_username.strip(),
        "terms": cleaned,
        "final_grade": overall_grade
    }

    data_store["grades"].append(record)

    try:
        save_data()
        return True, (
            "Grades saved successfully.\n"
            f"Overall grade: {overall_grade:.2f}"
        )

    except OSError as error:
        data_store["grades"].remove(record)
        return False, f"Unable to save grades: {error}"


def grades_for_student(username):
    return sorted(
        [
            grade for grade in data_store["grades"]
            if grade.get("student_username", "").lower()
            == username.lower()
        ],
        key=lambda grade: grade.get("id", 0),
        reverse=True
    )


def grades_for_teacher(username):
    return sorted(
        [
            grade for grade in data_store["grades"]
            if grade.get("teacher_username", "").lower()
            == username.lower()
        ],
        key=lambda grade: grade.get("id", 0),
        reverse=True
    )


ensure_default_users()