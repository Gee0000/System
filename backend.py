"""Backend for the SMCII Grade Calculation Performance System."""

import hashlib
import hmac
import json
import os
from datetime import datetime

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
    "activities": "Activity",
    "quizzes": "Quiz",
    "performance_tasks": "Performance Task",
    "exams": "Exam",
}

ASSESSMENT_ITEM_COUNTS = {
    "activities": 1,
    "quizzes": 1,
    "performance_tasks": 1,
    "exams": 1,
}

ASSESSMENT_WEIGHTS = {
    "written_works": 0.30,
    "exams": 0.30,
    "performance_tasks": 0.40,
}

ASSESSMENT_WEIGHT_LABELS = {
    "written_works": "Activities + Quizzes",
    "exams": "Exam",
    "performance_tasks": "Performance Task",
}

ASSESSMENT_ITEMS = [
    (
        key,
        index,
        (
            f"{ASSESSMENT_LABELS[key]} {index + 1}"
            if ASSESSMENT_ITEM_COUNTS[key] > 1
            else ASSESSMENT_LABELS[key]
        ),
    )
    for key in ASSESSMENT_NAMES
    for index in range(ASSESSMENT_ITEM_COUNTS[key])
]


def assessment_label(key, index):
    """Return the display label of a single assessment input."""

    if ASSESSMENT_ITEM_COUNTS.get(key, 1) > 1:
        return f"{ASSESSMENT_LABELS[key]} {index + 1}"

    return ASSESSMENT_LABELS[key]


def assessment_item_count(key):
    """Return how many inputs an assessment type needs per term."""

    return ASSESSMENT_ITEM_COUNTS.get(key, 1)

ROLES = ["Admin", "Teacher", "Student"]

PASSING_GRADE = 75.0

DEFAULT_SUBJECTS = [
    "Mathematics",
    "English",
    "Science",
    "Filipino",
    "Social Studies",
    "Computer",
]

PROTECTED_USERNAMES = ("admin", "teacher", "student")

MAX_ACTIVITY_ENTRIES = 500

MAX_ANNOUNCEMENTS = 100

ANNOUNCEMENT_AUDIENCES = ("Everyone", "Students", "Teachers")


def empty_store():
    return {
        "users": [],
        "grades": [],
        "subjects": list(DEFAULT_SUBJECTS),
        "activity_log": [],
        "announcements": [],
        "settings": {
            "theme": "light"
        }
    }


def normalize_term_block(block):
    """Convert a stored term block into the current list based format."""

    if not isinstance(block, dict):
        return None

    normalized = {}

    for key in ASSESSMENT_NAMES:
        value = block.get(key)

        if isinstance(value, (int, float)):
            normalized[key] = [float(value)]

        elif isinstance(value, (list, tuple)):
            normalized[key] = [
                float(item)
                for item in value
                if isinstance(item, (int, float))
            ]

        else:
            normalized[key] = []

    term_grade = block.get("term_grade")

    if isinstance(term_grade, (int, float)):
        normalized["term_grade"] = float(term_grade)

    return normalized


def normalize_grade_record(record):
    """Migrate a stored grade record to the current structure."""

    if not isinstance(record, dict):
        return record

    stored_terms = record.get("terms")

    if not isinstance(stored_terms, dict):
        record["terms"] = {}
        return record

    terms = {}

    for term, block in stored_terms.items():
        normalized = normalize_term_block(block)

        if normalized is not None:
            terms[term] = normalized

    record["terms"] = terms

    return record


def load_data():
    if not os.path.exists(DATA_FILE):
        return empty_store()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            saved_data = json.load(file)

    except (OSError, json.JSONDecodeError):
        return empty_store()

    if not isinstance(saved_data, dict):
        return empty_store()

    users = saved_data.get("users", [])
    grades = saved_data.get("grades", [])
    subjects = saved_data.get("subjects", [])
    activity_log = saved_data.get("activity_log", [])
    announcements = saved_data.get("announcements", [])
    settings = saved_data.get("settings", {})

    if not isinstance(users, list):
        users = []

    if not isinstance(grades, list):
        grades = []

    if not isinstance(subjects, list):
        subjects = []

    if not isinstance(activity_log, list):
        activity_log = []

    if not isinstance(announcements, list):
        announcements = []

    if not isinstance(settings, dict):
        settings = {}

    for user in users:
        if not isinstance(user, dict):
            continue

        user.setdefault("active", True)
        user.setdefault(
            "protected",
            user.get("username", "").lower() in PROTECTED_USERNAMES
        )

        user.setdefault("student_id", "")

        if not isinstance(user.get("subjects"), list):
            user["subjects"] = []

    grades = [
        normalize_grade_record(grade)
        for grade in grades
        if isinstance(grade, dict)
    ]

    cleaned_announcements = []

    for entry in announcements:
        if not isinstance(entry, dict):
            continue

        audience = entry.get("audience")

        cleaned_announcements.append({
            "id": entry.get("id", 0),
            "title": str(entry.get("title", "")),
            "body": str(entry.get("body", "")),
            "audience": (
                audience
                if audience in ANNOUNCEMENT_AUDIENCES
                else "Everyone"
            ),
            "author": str(entry.get("author", "")),
            "timestamp": str(entry.get("timestamp", ""))
        })

    announcements = cleaned_announcements

    if not subjects:
        subjects = list(DEFAULT_SUBJECTS)

    settings.setdefault("theme", "light")

    return {
        "users": users,
        "grades": grades,
        "subjects": subjects,
        "activity_log": activity_log,
        "announcements": announcements,
        "settings": settings
    }


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


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def hash_password(password):
    salt = os.urandom(16).hex()

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120000
    ).hex()

    return f"pbkdf2_sha256$120000${salt}${digest}"


def verify_password(stored_password, password):
    if not isinstance(stored_password, str):
        return False

    if stored_password.startswith("pbkdf2_sha256$"):
        try:
            algorithm, iterations, salt, digest = stored_password.split("$")
        except ValueError:
            return False

        if algorithm != "pbkdf2_sha256":
            return False

        try:
            rounds = int(iterations)
        except ValueError:
            return False

        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            rounds
        ).hex()

        return hmac.compare_digest(candidate, digest)

    try:
        return hmac.compare_digest(stored_password, password)
    except TypeError:
        return False


def log_activity(action, detail, actor="system"):
    entry = {
        "id": next_id(data_store["activity_log"]),
        "timestamp": timestamp(),
        "actor": actor or "system",
        "action": action,
        "detail": detail
    }

    data_store["activity_log"].append(entry)

    if len(data_store["activity_log"]) > MAX_ACTIVITY_ENTRIES:
        del data_store["activity_log"][:-MAX_ACTIVITY_ENTRIES]

    return entry


def activity_entries(limit=400):
    return list(reversed(data_store["activity_log"][-limit:]))


def commit_activity(action, detail, actor="system"):
    entry = log_activity(action, detail, actor)

    try:
        save_data()
    except OSError:
        data_store["activity_log"].remove(entry)

    return entry


def clear_activity_log(actor="system"):
    removed = len(data_store["activity_log"])

    data_store["activity_log"].clear()

    try:
        save_data()
    except OSError as error:
        return False, f"Unable to clear the activity log: {error}"

    commit_activity(
        "Activity log cleared",
        f"{removed} entries removed",
        actor
    )

    return True, "Activity log cleared."


def announcement_audience_for_role(role):
    normal = (role or "").strip().lower()

    if normal == "student":
        return "Students"

    if normal == "teacher":
        return "Teachers"

    return ""


def all_announcements():
    """Return every announcement, newest first."""

    return sorted(
        data_store["announcements"],
        key=lambda entry: entry.get("id", 0),
        reverse=True
    )


def announcements_for(role=""):
    """Return the announcements visible to a role, newest first."""

    audience = announcement_audience_for_role(role)

    entries = all_announcements()

    if not audience:
        return entries

    return [
        entry for entry in entries
        if entry.get("audience") in ("Everyone", audience)
    ]


def add_announcement(title, body, audience="Everyone", actor="system"):
    title = (title or "").strip()
    body = (body or "").strip()

    if not title:
        return False, "Enter an announcement title."

    if len(title) > 90:
        return False, "Titles must be 90 characters or fewer."

    if not body:
        return False, "Write the announcement message."

    if len(body) > 2000:
        return False, "Messages must be 2000 characters or fewer."

    if audience not in ANNOUNCEMENT_AUDIENCES:
        audience = "Everyone"

    entry = {
        "id": next_id(data_store["announcements"]),
        "title": title,
        "body": body,
        "audience": audience,
        "author": actor or "system",
        "timestamp": timestamp()
    }

    data_store["announcements"].append(entry)

    overflow = []

    if len(data_store["announcements"]) > MAX_ANNOUNCEMENTS:
        overflow = data_store["announcements"][:-MAX_ANNOUNCEMENTS]
        del data_store["announcements"][:-MAX_ANNOUNCEMENTS]

    try:
        save_data()
        commit_activity(
            "Announcement posted",
            f"{title} ({audience})",
            actor
        )

        return True, f"Announcement '{title}' posted."

    except OSError as error:
        data_store["announcements"].remove(entry)
        data_store["announcements"][0:0] = overflow

        return False, f"Unable to save the announcement: {error}"


def delete_announcement(announcement_id, actor="system"):
    target = next(
        (
            entry for entry in data_store["announcements"]
            if str(entry.get("id", "")) == str(announcement_id)
        ),
        None
    )

    if target is None:
        return False, "That announcement no longer exists."

    position = data_store["announcements"].index(target)
    data_store["announcements"].remove(target)

    try:
        save_data()
        commit_activity(
            "Announcement removed",
            target.get("title", ""),
            actor
        )

        return True, "Announcement deleted."

    except OSError as error:
        data_store["announcements"].insert(position, target)

        return False, f"Unable to delete the announcement: {error}"


def create_default_user(
    username,
    password,
    role,
    full_name,
    student_id=""
):
    existing = next(
        (
            user for user in data_store["users"]
            if user.get("username", "").lower() == username.lower()
        ),
        None
    )

    if existing is not None:
        if (
            role == "Student"
            and student_id
            and not existing.get("student_id")
        ):
            existing["student_id"] = student_id

            try:
                save_data()
            except OSError:
                pass

        return

    user = {
        "id": next_id(data_store["users"]),
        "username": username,
        "password": hash_password(password),
        "role": role,
        "full_name": full_name,
        "active": True,
        "protected": username.lower() in PROTECTED_USERNAMES,
        "student_id": student_id if role == "Student" else "",
        "subjects": []
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
            "System Administrator",
            ""
        ),
        (
            "teacher",
            "teacher123",
            "Teacher",
            "SMCII Teacher",
            ""
        ),
        (
            "student",
            "student123",
            "Student",
            "Sample Student",
            "2024-0001"
        )
    ]

    for username, password, role, full_name, student_id in defaults:
        create_default_user(
            username,
            password,
            role,
            full_name,
            student_id
        )


def find_user(username):
    return next(
        (
            user for user in data_store["users"]
            if user.get("username", "").lower() == username.lower()
        ),
        None
    )


def users_by_role(role):
    return sorted(
        [
            user for user in data_store["users"]
            if user.get("role", "").lower() == role.lower()
        ],
        key=lambda user: user.get("full_name", "").lower()
    )


def admin_count():
    return len(users_by_role("Admin"))


def is_admin_account(user):
    return user.get("role", "").lower() == "admin"


def authenticate_user(username, password, role):
    username = username.strip().lower()
    password = password.strip()
    role = role.strip().lower()

    for user in data_store["users"]:
        if user.get("username", "").lower() != username:
            continue

        if user.get("role", "").lower() != role:
            continue

        if not verify_password(user.get("password", ""), password):
            continue

        if not user.get("active", True):
            return None

        if not user.get("password", "").startswith("pbkdf2_sha256$"):
            user["password"] = hash_password(password)

            try:
                save_data()
            except OSError:
                pass

        return user

    return None


def add_user(
    username,
    password,
    full_name,
    role,
    actor="system",
    subjects=None,
    student_id=""
):
    username = username.strip()
    password = password.strip()
    full_name = full_name.strip()
    role = role.strip()

    if not username or not password or not full_name or not role:
        return False, "Please complete all account fields."

    if role not in ROLES:
        return False, "Please select a valid account role."

    if len(username) < 3:
        return False, "Usernames must be at least 3 characters long."

    if len(password) < 6:
        return False, "Passwords must be at least 6 characters long."

    if role == "Admin":
        return False, (
            "This system allows only one administrator account. "
            "The existing administrator cannot be replaced."
        )

    for user in data_store["users"]:
        if user.get("username", "").lower() == username.lower():
            return False, "This username already exists."

    if role == "Student":
        cleaned_id, error = clean_student_id(student_id)

        if error:
            return False, error

        if student_id_taken(cleaned_id):
            return False, (
                f"ID number '{cleaned_id}' is already used "
                "by another student."
            )

    else:
        cleaned_id = ""

    assigned = clean_subject_list(subjects)

    new_user = {
        "id": next_id(data_store["users"]),
        "username": username,
        "password": hash_password(password),
        "full_name": full_name,
        "role": role,
        "active": True,
        "protected": False,
        "student_id": cleaned_id,
        "subjects": assigned if role == "Teacher" else []
    }

    data_store["users"].append(new_user)

    try:
        save_data()
        commit_activity(
            "Account created",
            f"{full_name} ({username}) added as {role}",
            actor
        )

        if cleaned_id:
            commit_activity(
                "Student ID number assigned",
                f"{username} uses ID number {cleaned_id}",
                actor
            )

        if assigned:
            commit_activity(
                "Subject assigned",
                f"{username} assigned to {', '.join(assigned)}",
                actor
            )

        return True, "Account created successfully."

    except OSError as error:
        data_store["users"].remove(new_user)
        return False, f"Unable to save account: {error}"


def clean_subject_list(subjects):
    """Return a clean list of unique subject names."""

    cleaned = []

    if isinstance(subjects, str):
        subjects = [subjects]

    if not isinstance(subjects, (list, tuple)):
        return cleaned

    for subject in subjects:
        name = str(subject).strip()

        if not name:
            continue

        if any(
            item.lower() == name.lower()
            for item in cleaned
        ):
            continue

        cleaned.append(name)

    return cleaned


def subjects_for_teacher(username):
    """Return the subjects assigned to a teacher account."""

    user = find_user(username)

    if user is None:
        return []

    return clean_subject_list(user.get("subjects", []))


def teachers_for_subject(subject):
    """Return the teacher usernames assigned to a subject."""

    subject = subject.strip().lower()

    return sorted(
        [
            user.get("username", "")
            for user in data_store["users"]
            if user.get("role", "").lower() == "teacher"
            and any(
                name.strip().lower() == subject
                for name in user.get("subjects", [])
            )
        ],
        key=lambda name: name.lower()
    )


def teacher_assignments():
    """Return every teacher and subject assignment in the system."""

    assignments = []

    for user in data_store["users"]:
        if user.get("role", "").lower() != "teacher":
            continue

        for subject in clean_subject_list(user.get("subjects", [])):
            assignments.append({
                "teacher_username": user.get("username", ""),
                "teacher_name": user.get("full_name", ""),
                "subject": subject,
                "records": len([
                    grade for grade in data_store["grades"]
                    if grade.get("teacher_username", "").lower()
                    == user.get("username", "").lower()
                    and grade.get("subject", "").strip().lower()
                    == subject.lower()
                ])
            })

    return sorted(
        assignments,
        key=lambda item: (
            item["teacher_name"].lower(),
            item["subject"].lower()
        )
    )


def assign_subject_to_teacher(
    teacher_username,
    subject,
    actor="system"
):
    """Assign a subject to a teacher account."""

    teacher = find_user(teacher_username)

    if teacher is None:
        return False, "Teacher account not found."

    if teacher.get("role", "").lower() != "teacher":
        return False, "Only teacher accounts can be assigned subjects."

    subject = subject.strip()

    if not subject:
        return False, "Enter a subject name."

    known_subjects = [
        item.strip().lower()
        for item in data_store["subjects"]
    ]

    if subject.lower() not in known_subjects:
        return False, (
            f"'{subject}' is not in the subject list. "
            "Add the subject first."
        )

    assigned = clean_subject_list(teacher.get("subjects", []))

    if any(
        item.lower() == subject.lower()
        for item in assigned
    ):
        return False, (
            f"{teacher.get('full_name', '')} is already assigned "
            f"to {subject}."
        )

    assigned.append(subject)
    teacher["subjects"] = assigned

    try:
        save_data()
        commit_activity(
            "Subject assigned",
            (
                f"{teacher.get('full_name', '')} "
                f"({teacher.get('username', '')}) assigned to {subject}"
            ),
            actor
        )

        return True, f"{subject} assigned to {teacher.get('full_name', '')}."

    except OSError as error:
        assigned.remove(subject)
        return False, f"Unable to save the assignment: {error}"


def remove_subject_from_teacher(
    teacher_username,
    subject,
    actor="system"
):
    """Remove a subject assignment from a teacher account."""

    teacher = find_user(teacher_username)

    if teacher is None:
        return False, "Teacher account not found."

    subject = subject.strip()

    assigned = clean_subject_list(teacher.get("subjects", []))

    target = next(
        (
            item for item in assigned
            if item.lower() == subject.lower()
        ),
        None
    )

    if target is None:
        return False, f"{subject} is not assigned to this teacher."

    assigned.remove(target)
    teacher["subjects"] = assigned

    try:
        save_data()
        commit_activity(
            "Subject assignment removed",
            (
                f"{teacher.get('full_name', '')} "
                f"({teacher.get('username', '')}) removed from {target}"
            ),
            actor
        )

        return True, (
            f"{target} removed from "
            f"{teacher.get('full_name', '')}."
        )

    except OSError as error:
        assigned.append(target)
        return False, f"Unable to save the assignment: {error}"


def update_user(
    user_id,
    full_name="",
    username="",
    role="",
    password="",
    actor="system",
    subjects=None,
    student_id=None
):
    user = next(
        (
            item for item in data_store["users"]
            if item.get("id") == user_id
        ),
        None
    )

    if user is None:
        return False, "The selected account no longer exists."

    full_name = full_name.strip()
    username = username.strip()
    role = role.strip()

    if not full_name or not username:
        return False, "Username and full name are required."

    if role and role not in ROLES:
        return False, "Please select a valid account role."

    if is_admin_account(user):
        if role and role != "Admin":
            return False, (
                "The administrator account role cannot be changed."
            )
    elif role == "Admin":
        return False, (
            "This system allows only one administrator account."
        )

    for other in data_store["users"]:
        if other.get("id") == user_id:
            continue

        if other.get("username", "").lower() == username.lower():
            return False, "This username already exists."

    new_password = password.strip()

    if new_password and len(new_password) < 6:
        return False, "Passwords must be at least 6 characters long."

    previous = {
        "username": user.get("username", ""),
        "full_name": user.get("full_name", ""),
        "role": user.get("role", ""),
        "student_id": str(user.get("student_id", "")).strip(),
        "subjects": clean_subject_list(user.get("subjects", []))
    }

    cleaned_id = None

    if student_id is not None:
        target_role = (role or previous["role"]).lower()

        if target_role == "student":
            cleaned_id, error = clean_student_id(student_id)

            if error:
                return False, error

            if student_id_taken(cleaned_id, user_id):
                return False, (
                    f"ID number '{cleaned_id}' is already used "
                    "by another student."
                )

        else:
            cleaned_id = ""

    user["full_name"] = full_name
    user["username"] = username

    if role:
        user["role"] = role

    changes = []

    if previous["full_name"] != full_name:
        changes.append("full name")

    if previous["username"] != username:
        changes.append("username")

    if role and previous["role"] != role:
        changes.append("role")

    if new_password:
        user["password"] = hash_password(new_password)
        changes.append("password")

    if (
        cleaned_id is not None
        and cleaned_id != previous["student_id"]
    ):
        user["student_id"] = cleaned_id
        changes.append("ID number")

    if subjects is not None and user.get("role", "").lower() == "teacher":
        assigned = clean_subject_list(subjects)

        if assigned != previous["subjects"]:
            user["subjects"] = assigned
            changes.append("subject assignments")

    if not changes:
        return False, "Nothing was changed."

    try:
        save_data()
        commit_activity(
            "Account updated",
            (
                f"{previous['full_name']} ({previous['username']}) - "
                f"changed: {', '.join(changes)}"
            ),
            actor
        )

        return True, "Account updated successfully."

    except OSError as error:
        user["full_name"] = previous["full_name"]
        user["username"] = previous["username"]
        user["role"] = previous["role"]
        user["student_id"] = previous["student_id"]

        return False, f"Unable to save the account: {error}"



def reset_password(user_id, new_password, actor="system"):
    user = next(
        (
            item for item in data_store["users"]
            if item.get("id") == user_id
        ),
        None
    )

    if user is None:
        return False, "The selected account no longer exists."

    new_password = new_password.strip()

    if len(new_password) < 6:
        return False, "Passwords must be at least 6 characters long."

    user["password"] = hash_password(new_password)

    try:
        save_data()
        commit_activity(
            "Password reset",
            f"Password reset for {user.get('full_name', '')} "
            f"({user.get('username', '')})",
            actor
        )

        return True, "Password reset successfully."

    except OSError as error:
        return False, f"Unable to save the account: {error}"


def set_user_active(user_id, active, actor="system"):
    user = next(
        (
            item for item in data_store["users"]
            if item.get("id") == user_id
        ),
        None
    )

    if user is None:
        return False, "The selected account no longer exists."

    if is_admin_account(user) and not active:
        return False, (
            "The administrator account cannot be deactivated."
        )

    user["active"] = bool(active)

    try:
        save_data()
        commit_activity(
            "Account activated" if active else "Account deactivated",
            (
                f"{user.get('full_name', '')} "
                f"({user.get('username', '')})"
            ),
            actor
        )

        return True, (
            "Account activated."
            if active
            else "Account deactivated."
        )

    except OSError as error:
        return False, f"Unable to save the account: {error}"


def delete_user(user_id, actor="system"):
    user = next(
        (
            item for item in data_store["users"]
            if item.get("id") == user_id
        ),
        None
    )

    if user is None:
        return False, "The selected account no longer exists."

    if is_admin_account(user):
        return False, "The administrator account cannot be deleted."

    if user.get("protected"):
        return False, (
            "Default system accounts cannot be deleted. "
            "Deactivate the account instead."
        )

    removed_grades = [
        grade for grade in data_store["grades"]
        if grade.get("student_username", "").lower()
        == user.get("username", "").lower()
    ]

    for grade in removed_grades:
        data_store["grades"].remove(grade)

    data_store["users"].remove(user)

    try:
        save_data()
        commit_activity(
            "Account deleted",
            (
                f"{user.get('full_name', '')} "
                f"({user.get('username', '')}) and "
                f"{len(removed_grades)} grade record(s) removed"
            ),
            actor
        )

        return True, (
            "Account deleted. "
            f"{len(removed_grades)} grade record(s) were removed too."
        )

    except OSError as error:
        data_store["users"].append(user)
        data_store["grades"].extend(removed_grades)

        return False, f"Unable to save the account: {error}"


def clean_assessment_block(block):
    """Validate one term of assessment scores.

    Each assessment type holds a list of individual scores so a term can
    carry several activities and several quizzes.
    """

    if not isinstance(block, dict):
        return None, "Assessment scores are missing."

    cleaned = {}

    for key in ASSESSMENT_NAMES:
        expected = ASSESSMENT_ITEM_COUNTS[key]
        raw = block.get(key)

        if isinstance(raw, (int, float)):
            raw = [raw]

        if not isinstance(raw, (list, tuple)):
            return None, (
                f"Enter a valid {ASSESSMENT_LABELS[key]} score."
            )

        scores = []

        for value in raw:
            try:
                score = float(value)
            except (TypeError, ValueError):
                return None, (
                    f"Enter valid {ASSESSMENT_LABELS[key]} scores."
                )

            if score < 0 or score > 100:
                return None, (
                    f"{ASSESSMENT_LABELS[key]} scores "
                    "must be between 0 and 100."
                )

            scores.append(score)

        if len(scores) != expected:
            return None, (
                f"Enter {expected} {ASSESSMENT_LABELS[key]} "
                f"score(s) for this term."
            )

        cleaned[key] = scores

    cleaned["term_grade"] = compute_term_grade(cleaned)

    return cleaned, None


def compute_term_grade(cleaned):
    """Compute the weighted term grade.

    Activities and quizzes form the written works category at 30%, the exam
    is 30%, and the performance task is 40%.
    """

    categories = {}

    written_works = []
    written_works.extend((cleaned or {}).get("activities") or [])
    written_works.extend((cleaned or {}).get("quizzes") or [])

    if written_works:
        categories["written_works"] = (
            sum(written_works) / len(written_works)
        )

    for key in ("exams", "performance_tasks"):
        scores = (cleaned or {}).get(key) or []

        if scores:
            categories[key] = sum(scores) / len(scores)

    if not categories:
        return None

    total_weight = sum(ASSESSMENT_WEIGHTS[key] for key in categories)

    weighted = sum(
        categories[key] * ASSESSMENT_WEIGHTS[key]
        for key in categories
    )

    return round(weighted / total_weight, 2)


def assessment_type_average(cleaned, key):
    """Return the average score of one assessment type."""

    scores = (cleaned or {}).get(key) or []

    if not scores:
        return None

    return round(sum(scores) / len(scores), 2)


def completed_term_grades(terms):
    """Return the term grades that are already computed."""

    values = []

    for term in TERM_NAMES:
        block = (terms or {}).get(term)

        if not isinstance(block, dict):
            continue

        grade = block.get("term_grade")

        if isinstance(grade, (int, float)):
            values.append((term, float(grade)))

    return values


def overall_grade_for_terms(terms):
    """Average every completed term grade."""

    values = [
        value for _, value in completed_term_grades(terms)
    ]

    if not values:
        return None

    return round(sum(values) / len(values), 2)


def validate_assessments(assessments):
    """Validate a full set of term assessments."""

    if not isinstance(assessments, dict):
        return None, "Assessment scores are missing."

    cleaned = {}

    for term in TERM_NAMES:
        term_data = assessments.get(term)

        if not isinstance(term_data, dict):
            return None, f"Missing assessment scores for {term}."

        block, error = clean_assessment_block(term_data)

        if error:
            return None, f"{term}: {error}"

        cleaned[term] = block

    return cleaned, None


def find_student(username):
    """Return the student account matching a username."""

    return next(
        (
            user for user in data_store["users"]
            if user.get("username", "").lower()
            == username.strip().lower()
            and user.get("role", "").lower() == "student"
        ),
        None
    )


def find_student_by_id(student_id):
    """Return the student account matching an ID number."""

    needle = str(student_id or "").strip().lower()

    if not needle:
        return None

    return next(
        (
            user for user in data_store["users"]
            if user.get("role", "").lower() == "student"
            and str(user.get("student_id", "")).strip().lower() == needle
        ),
        None
    )


def find_student_by_reference(reference):
    """Return a student account by username or by ID number."""

    needle = str(reference or "").strip().lower()

    if not needle:
        return None

    student = find_student(needle)

    if student is not None:
        return student

    return find_student_by_id(needle)


def student_id_of(username):
    """Return the ID number of a student account."""

    user = find_user(username)

    if user is None:
        return ""

    return str(user.get("student_id", "")).strip()


def student_id_taken(student_id, ignore_id=None):
    """Check whether an ID number belongs to another student."""

    needle = str(student_id or "").strip().lower()

    if not needle:
        return False

    return any(
        user.get("role", "").lower() == "student"
        and user.get("id") != ignore_id
        and str(user.get("student_id", "")).strip().lower() == needle
        for user in data_store["users"]
    )


def clean_student_id(student_id):
    """Validate an ID number and return it in a clean form."""

    cleaned = str(student_id or "").strip()

    if not cleaned:
        return None, "Enter the ID number of the student."

    if len(cleaned) < 3:
        return None, "Student ID numbers must be at least 3 characters long."

    if len(cleaned) > 30:
        return None, "Student ID numbers must be 30 characters or fewer."

    return cleaned, None


def find_grade_record(student_username, subject):
    """Return the grade record of a student in a subject."""

    student_username = student_username.strip().lower()
    subject = subject.strip().lower()

    return next(
        (
            grade for grade in data_store["grades"]
            if grade.get("student_username", "").lower()
            == student_username
            and grade.get("subject", "").strip().lower() == subject
        ),
        None
    )


def add_grade(
    student_username,
    subject,
    assessments,
    teacher_username="",
    actor="system"
):
    student_username = student_username.strip()
    subject = subject.strip()

    if not student_username or not subject:
        return False, "Enter the student username and subject."

    student = find_student(student_username)

    if student is None:
        return False, "Student account not found."

    cleaned, error = validate_assessments(assessments)

    if error:
        return False, error

    overall_grade = overall_grade_for_terms(cleaned)

    record = {
        "id": next_id(data_store["grades"]),
        "student_username": student["username"],
        "subject": subject,
        "teacher_username": teacher_username.strip(),
        "terms": cleaned,
        "final_grade": overall_grade,
        "terms_completed": len(TERM_NAMES),
        "updated_at": timestamp()
    }

    data_store["grades"].append(record)

    try:
        save_data()
        commit_activity(
            "Grade record saved",
            (
                f"{student['username']} - {subject} "
                f"overall {overall_grade:.2f} "
                f"by {teacher_username or 'system'}"
            ),
            actor
        )

        return True, (
            "Grades saved successfully.\n"
            f"Overall grade: {overall_grade:.2f}"
        )

    except OSError as error:
        data_store["grades"].remove(record)
        return False, f"Unable to save grades: {error}"


def save_term_grade(
    student_username,
    subject,
    term,
    assessments,
    teacher_username="",
    actor="system"
):
    """Save the assessment scores of a single term.

    The record is created on the first term and updated afterwards, so a
    teacher can calculate the grade of one term at a time.
    """

    student_username = student_username.strip()
    subject = subject.strip()
    term = term.strip()

    if not student_username or not subject:
        return False, "Enter the student username and subject."

    if term not in TERM_NAMES:
        return False, "Please select a valid term."

    student = find_student(student_username)

    if student is None:
        return False, "Student account not found."

    cleaned, error = clean_assessment_block(assessments)

    if error:
        return False, error

    record = find_grade_record(student["username"], subject)

    created = record is None

    if created:
        record = {
            "id": next_id(data_store["grades"]),
            "student_username": student["username"],
            "subject": subject,
            "teacher_username": teacher_username.strip(),
            "terms": {},
            "final_grade": None,
            "terms_completed": 0,
            "updated_at": timestamp()
        }

        data_store["grades"].append(record)

    previous_term_grade = None

    existing_block = record.get("terms", {}).get(term)

    if isinstance(existing_block, dict):
        previous_term_grade = existing_block.get("term_grade")

    record.setdefault("terms", {})
    record["terms"][term] = cleaned

    if teacher_username.strip():
        record["teacher_username"] = teacher_username.strip()

    record["final_grade"] = overall_grade_for_terms(record["terms"])
    record["terms_completed"] = len(completed_term_grades(record["terms"]))
    record["updated_at"] = timestamp()

    try:
        save_data()
        commit_activity(
            "Term grade saved",
            (
                f"{student['username']} - {subject} - {term} "
                f"grade {cleaned['term_grade']:.2f} "
                f"by {teacher_username or 'system'}"
            ),
            actor
        )

        completed = record["terms_completed"]

        return True, (
            f"{term} grade saved: {cleaned['term_grade']:.2f}\n"
            f"Overall grade: {record['final_grade']:.2f} "
            f"({completed} of {len(TERM_NAMES)} terms complete)"
        )

    except OSError as error:
        if created:
            data_store["grades"].remove(record)
        elif existing_block is None:
            record["terms"].pop(term, None)
        else:
            record["terms"][term] = existing_block

        record["final_grade"] = overall_grade_for_terms(record["terms"])
        record["terms_completed"] = len(
            completed_term_grades(record["terms"])
        )

        return False, f"Unable to save grades: {error}"


def delete_grade(record_id, actor="system"):
    """Delete a grade record."""

    record = next(
        (
            grade for grade in data_store["grades"]
            if grade.get("id") == record_id
        ),
        None
    )

    if record is None:
        return False, "The selected grade record no longer exists."

    data_store["grades"].remove(record)

    try:
        save_data()
        commit_activity(
            "Grade record deleted",
            (
                f"{record.get('student_username', '')} - "
                f"{record.get('subject', '')}"
            ),
            actor
        )

        return True, "Grade record deleted."

    except OSError as error:
        data_store["grades"].append(record)
        return False, f"Unable to delete the record: {error}"


def student_performance(username):
    """Build the performance summary of a student."""

    records = grades_for_student(username)

    subjects = []

    for record in records:
        subject = record.get("subject", "")
        terms = record.get("terms", {})
        term_grades = completed_term_grades(terms)
        overall = overall_grade_for_terms(terms)

        class_values = [
            overall_grade_for_terms(grade.get("terms", {}))
            for grade in data_store["grades"]
            if grade.get("subject", "").strip().lower()
            == subject.strip().lower()
        ]

        class_values = [
            value for value in class_values
            if isinstance(value, (int, float))
        ]

        class_average = (
            round(sum(class_values) / len(class_values), 2)
            if class_values else None
        )

        rank = None

        if overall is not None and class_values:
            rank = 1 + len([
                value for value in class_values
                if value > overall
            ])

        subjects.append({
            "subject": subject,
            "teacher_username": record.get("teacher_username", ""),
            "teacher_name": teacher_display_name(
                record.get("teacher_username", "")
            ),
            "terms": {
                term: value for term, value in term_grades
            },
            "terms_completed": len(term_grades),
            "overall": overall,
            "class_average": class_average,
            "class_size": len(class_values),
            "rank": rank,
            "status": (
                "—" if overall is None
                else ("PASSED" if overall >= PASSING_GRADE else "FAILED")
            ),
            "remark": grade_remark(overall)
        })

    subjects.sort(key=lambda item: item["subject"].lower())

    graded = [
        item for item in subjects
        if isinstance(item["overall"], (int, float))
    ]

    general_average = (
        round(
            sum(item["overall"] for item in graded) / len(graded),
            2
        )
        if graded else None
    )

    return {
        "subjects": subjects,
        "general_average": general_average,
        "subjects_count": len(subjects),
        "passed": len([
            item for item in graded
            if item["overall"] >= PASSING_GRADE
        ]),
        "failed": len([
            item for item in graded
            if item["overall"] < PASSING_GRADE
        ])
    }


def grade_remark(overall):
    """Return the descriptive remark of an overall grade."""

    if not isinstance(overall, (int, float)):
        return "No grade yet"

    if overall >= 95:
        return "Outstanding"

    if overall >= 90:
        return "Excellent"

    if overall >= 85:
        return "Very Good"

    if overall >= PASSING_GRADE:
        return "Good"

    if overall >= 60:
        return "Needs Improvement"

    return "Failed"


def teacher_display_name(username):
    """Return the full name of a teacher account."""

    if not username:
        return ""

    user = find_user(username)

    if user is None:
        return username

    return user.get("full_name", username)


def teacher_subject_report(teacher_username, subject=""):
    """Build the class performance list of a teacher."""

    records = [
        grade for grade in data_store["grades"]
        if grade.get("teacher_username", "").lower()
        == teacher_username.strip().lower()
        and (
            not subject
            or grade.get("subject", "").strip().lower()
            == subject.strip().lower()
        )
    ]

    rows = []

    for record in records:
        terms = record.get("terms", {})
        term_grades = completed_term_grades(terms)
        overall = overall_grade_for_terms(terms)

        rows.append({
            "record_id": record.get("id"),
            "student_username": record.get("student_username", ""),
            "student_name": student_display_name(
                record.get("student_username", "")
            ),
            "student_id": student_id_of(
                record.get("student_username", "")
            ),
            "subject": record.get("subject", ""),
            "terms": {term: value for term, value in term_grades},
            "terms_completed": len(term_grades),
            "overall": overall,
            "status": (
                "—" if overall is None
                else ("PASSED" if overall >= PASSING_GRADE else "FAILED")
            )
        })

    rows.sort(key=lambda item: item["student_username"].lower())

    values = [
        row["overall"] for row in rows
        if isinstance(row["overall"], (int, float))
    ]

    return {
        "rows": rows,
        "records": len(rows),
        "class_average": (
            round(sum(values) / len(values), 2) if values else None
        ),
        "highest": round(max(values), 2) if values else None,
        "lowest": round(min(values), 2) if values else None,
        "passing": len([
            value for value in values
            if value >= PASSING_GRADE
        ]),
        "failing": len(values) - len([
            value for value in values
            if value >= PASSING_GRADE
        ])
    }


def student_display_name(username):
    """Return the full name of a student account."""

    if not username:
        return ""

    user = find_user(username)

    if user is None:
        return username

    return user.get("full_name", username)


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


def all_grade_records(student="", subject="", teacher=""):
    student = student.strip().lower()
    subject = subject.strip().lower()
    teacher = teacher.strip().lower()

    records = []

    for grade in data_store["grades"]:
        if student:
            username = grade.get("student_username", "").lower()
            identifier = student_id_of(
                grade.get("student_username", "")
            ).lower()

            if student not in username and student not in identifier:
                continue

        if subject and subject not in grade.get(
            "subject", ""
        ).lower():
            continue

        if teacher and teacher not in grade.get(
            "teacher_username", ""
        ).lower():
            continue

        records.append(grade)

    return sorted(
        records,
        key=lambda grade: grade.get("id", 0),
        reverse=True
    )


def list_subjects():
    return list(data_store["subjects"])


def add_subject(name, actor="system"):
    name = name.strip()

    if not name:
        return False, "Enter a subject name."

    if len(name) > 60:
        return False, "Subject names must be 60 characters or fewer."

    for existing in data_store["subjects"]:
        if existing.strip().lower() == name.lower():
            return False, f"'{name}' is already in the subject list."

    data_store["subjects"].append(name)

    try:
        save_data()
        commit_activity("Subject added", name, actor)

        return True, f"Subject '{name}' added."

    except OSError as error:
        data_store["subjects"].remove(name)
        return False, f"Unable to save the subject: {error}"


def remove_subject(name, actor="system"):
    target = next(
        (
            subject for subject in data_store["subjects"]
            if subject.strip().lower() == name.strip().lower()
        ),
        None
    )

    if target is None:
        return False, "That subject is not in the subject list."

    used = len([
        grade for grade in data_store["grades"]
        if grade.get("subject", "").strip().lower() == target.lower()
    ])

    data_store["subjects"].remove(target)

    try:
        save_data()
        commit_activity(
            "Subject removed",
            f"{target} ({used} existing grade record(s) kept)",
            actor
        )

        return True, (
            f"Subject '{target}' removed. "
            f"{used} existing grade record(s) were kept."
        )

    except OSError as error:
        data_store["subjects"].append(target)
        return False, f"Unable to save the subject: {error}"


def subject_usage(name):
    return len([
        grade for grade in data_store["grades"]
        if grade.get("subject", "").strip().lower() == name.strip().lower()
    ])


def system_statistics():
    users = data_store["users"]
    grades = data_store["grades"]

    finals = []

    for grade in grades:
        value = grade.get("final_grade")

        if isinstance(value, (int, float)):
            finals.append(float(value))

    passing = len([
        value for value in finals
        if value >= PASSING_GRADE
    ])

    failing = len(finals) - passing

    subject_values = {}

    for grade in grades:
        value = grade.get("final_grade")

        if not isinstance(value, (int, float)):
            continue

        subject = grade.get("subject", "") or "(Unspecified)"

        subject_values.setdefault(subject, []).append(float(value))

    per_subject = []

    for subject, values in subject_values.items():
        per_subject.append({
            "subject": subject,
            "records": len(values),
            "average": round(sum(values) / len(values), 2),
            "highest": round(max(values), 2),
            "lowest": round(min(values), 2),
            "passing": len([
                value for value in values
                if value >= PASSING_GRADE
            ])
        })

    per_subject.sort(key=lambda item: item["subject"].lower())

    student_values = {}

    for grade in grades:
        value = grade.get("final_grade")

        if not isinstance(value, (int, float)):
            continue

        username = grade.get("student_username", "")

        student_values.setdefault(username, []).append(float(value))

    student_averages = []

    for username, values in student_values.items():
        student_averages.append({
            "username": username,
            "records": len(values),
            "average": round(sum(values) / len(values), 2)
        })

    student_averages.sort(
        key=lambda item: item["average"],
        reverse=True
    )

    teacher_counts = {}

    for grade in grades:
        teacher = grade.get("teacher_username", "") or "(Unassigned)"
        teacher_counts[teacher] = teacher_counts.get(teacher, 0) + 1

    teacher_activity = sorted(
        teacher_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )

    inactive = len([
        user for user in users
        if not user.get("active", True)
    ])

    assignments = teacher_assignments()

    teachers = users_by_role("Teacher")

    unassigned_teachers = len([
        user for user in teachers
        if not clean_subject_list(user.get("subjects", []))
    ])

    return {
        "total_users": len(users),
        "active_users": len(users) - inactive,
        "inactive_users": inactive,
        "admins": admin_count(),
        "teachers": len(teachers),
        "students": len(users_by_role("Student")),
        "total_grades": len(grades),
        "average_grade": (
            round(sum(finals) / len(finals), 2) if finals else 0.0
        ),
        "highest_grade": round(max(finals), 2) if finals else 0.0,
        "lowest_grade": round(min(finals), 2) if finals else 0.0,
        "passing": passing,
        "failing": failing,
        "pass_rate": (
            round(passing / len(finals) * 100, 2) if finals else 0.0
        ),
        "subjects_offered": len(data_store["subjects"]),
        "subject_assignments": len(assignments),
        "unassigned_teachers": unassigned_teachers,
        "per_subject": per_subject,
        "top_students": student_averages[:5],
        "needs_attention": list(reversed(student_averages))[:5],
        "teacher_activity": teacher_activity,
        "activity_events": len(data_store["activity_log"])
    }


def _text_row(values, widths):
    cells = []

    for value, width in zip(values, widths):
        text = "" if value is None else str(value)

        if len(text) > width:
            text = text[:max(1, width - 3)] + "..."

        cells.append(text.ljust(width))

    return " | ".join(cells)


def _report_header(title):
    lines = [
        "=" * 78,
        "SMCII GRADE CALCULATION PERFORMANCE SYSTEM",
        title,
        f"Generated: {timestamp()}",
        "=" * 78,
        ""
    ]

    return lines


def build_user_report():
    lines = _report_header("USER ACCOUNTS REPORT")

    headers = [
        "ID",
        "ID Number",
        "Username",
        "Full Name",
        "Role",
        "Status"
    ]

    widths = [5, 14, 20, 28, 10, 10]

    lines.append(_text_row(headers, widths))
    lines.append("-" * 78)

    for user in sorted(
        data_store["users"],
        key=lambda item: item.get("id", 0)
    ):
        lines.append(_text_row([
            user.get("id", ""),
            user.get("student_id", "") or "—",
            user.get("username", ""),
            user.get("full_name", ""),
            user.get("role", ""),
            "Active" if user.get("active", True) else "Inactive"
        ], widths))

    lines.append("")
    lines.append(f"Total accounts: {len(data_store['users'])}")
    lines.append(
        f"Teachers: {len(users_by_role('Teacher'))}  "
        f"Students: {len(users_by_role('Student'))}  "
        f"Administrators: {admin_count()}"
    )

    lines.append("")
    lines.append("TEACHER SUBJECT ASSIGNMENTS")
    lines.append("-" * 78)

    assignments = teacher_assignments()

    if assignments:
        for item in assignments:
            lines.append(
                f"{item['teacher_name']} "
                f"({item['teacher_username']}) - "
                f"{item['subject']} "
                f"[{item['records']} grade record(s)]"
            )
    else:
        lines.append("No teacher has been assigned a subject yet.")

    return "\n".join(lines) + "\n"


def build_grade_report():
    lines = _report_header("ALL GRADE RECORDS REPORT")

    headers = [
        "ID",
        "Student",
        "Subject",
        "Prelim",
        "Midterm",
        "Semifinal",
        "Finals",
        "Overall",
        "Status",
        "Teacher"
    ]

    widths = [4, 16, 16, 8, 8, 9, 8, 8, 8, 14]

    lines.append(_text_row(headers, widths))
    lines.append("-" * 78)

    records = all_grade_records()

    for grade in records:
        terms = grade.get("terms", {})
        values = []

        for term in TERM_NAMES:
            value = terms.get(term, {}).get("term_grade")

            if isinstance(value, (int, float)):
                values.append(f"{value:.2f}")
            else:
                values.append("—")

        overall = grade.get("final_grade")

        if not isinstance(overall, (int, float)):
            overall = overall_grade_for_terms(terms)

        if isinstance(overall, (int, float)):
            overall_text = f"{float(overall):.2f}"
            status = (
                "PASSED"
                if float(overall) >= PASSING_GRADE
                else "FAILED"
            )
        else:
            overall_text = "—"
            status = "—"

        lines.append(_text_row([
            grade.get("id", ""),
            grade.get("student_username", ""),
            grade.get("subject", ""),
            *values,
            overall_text,
            status,
            grade.get("teacher_username", "") or "(Unassigned)"
        ], widths))

    lines.append("")
    lines.append(f"Total grade records: {len(records)}")

    lines.append("")
    lines.append("ASSESSMENT BREAKDOWN")
    lines.append("-" * 78)

    for grade in records:
        terms = grade.get("terms", {})

        if not terms:
            continue

        lines.append("")
        lines.append(
            f"Record {grade.get('id', '')} - "
            f"{grade.get('student_username', '')} - "
            f"{grade.get('subject', '')}"
        )

        for term in TERM_NAMES:
            block = terms.get(term)

            if not isinstance(block, dict):
                continue

            lines.append(
                f"  {term} - grade {block.get('term_grade', 0):.2f}"
            )

            for key in ASSESSMENT_NAMES:
                scores = block.get(key) or []

                if not scores:
                    continue

                average = assessment_type_average(block, key)

                detail = ", ".join(
                    f"{score:.2f}" for score in scores
                )

                lines.append(
                    f"    {ASSESSMENT_LABELS[key]}: {detail} "
                    f"(average {average:.2f})"
                )

    return "\n".join(lines) + "\n"


def build_statistics_report():
    stats = system_statistics()

    lines = _report_header("SYSTEM ANALYTICS SUMMARY")

    lines.append("ACCOUNT OVERVIEW")
    lines.append("-" * 78)

    summary = [
        ("Total accounts", stats["total_users"]),
        ("Active accounts", stats["active_users"]),
        ("Inactive accounts", stats["inactive_users"]),
        ("Administrators", stats["admins"]),
        ("Teachers", stats["teachers"]),
        ("Students", stats["students"]),
        ("Subjects offered", stats["subjects_offered"]),
        ("Teacher subject assignments", stats["subject_assignments"]),
        ("Teachers without a subject", stats["unassigned_teachers"]),
        ("Grade records", stats["total_grades"]),
        ("Average grade", f"{stats['average_grade']:.2f}"),
        ("Highest grade", f"{stats['highest_grade']:.2f}"),
        ("Lowest grade", f"{stats['lowest_grade']:.2f}"),
        ("Passing records", stats["passing"]),
        ("Failing records", stats["failing"]),
        ("Pass rate", f"{stats['pass_rate']:.2f}%"),
        ("Logged activities", stats["activity_events"])
    ]

    for label, value in summary:
        lines.append(f"{label + ':':<28}{value}")

    lines.append("")
    lines.append("PER SUBJECT BREAKDOWN")
    lines.append("-" * 78)

    headers = ["Subject", "Records", "Average", "Highest", "Lowest", "Passing"]
    widths = [24, 8, 9, 9, 8, 8]

    lines.append(_text_row(headers, widths))

    for item in stats["per_subject"]:
        lines.append(_text_row([
            item["subject"],
            item["records"],
            f"{item['average']:.2f}",
            f"{item['highest']:.2f}",
            f"{item['lowest']:.2f}",
            item["passing"]
        ], widths))

    lines.append("")
    lines.append("TOP STUDENTS BY AVERAGE GRADE")
    lines.append("-" * 78)

    if stats["top_students"]:
        for index, item in enumerate(stats["top_students"], start=1):
            lines.append(
                f"{index}. {item['username']} - "
                f"average {item['average']:.2f} "
                f"({item['records']} record(s))"
            )
    else:
        lines.append("No grade records yet.")

    lines.append("")
    lines.append("STUDENTS NEEDING SUPPORT")
    lines.append("-" * 78)

    if stats["needs_attention"]:
        for index, item in enumerate(stats["needs_attention"], start=1):
            lines.append(
                f"{index}. {item['username']} - "
                f"average {item['average']:.2f} "
                f"({item['records']} record(s))"
            )
    else:
        lines.append("No grade records yet.")

    lines.append("")
    lines.append("TEACHER ACTIVITY")
    lines.append("-" * 78)

    if stats["teacher_activity"]:
        for teacher, count in stats["teacher_activity"]:
            lines.append(f"{teacher + ':':<28}{count} record(s)")
    else:
        lines.append("No grade records yet.")

    return "\n".join(lines) + "\n"


def build_activity_report():
    lines = _report_header("ACTIVITY LOG REPORT")

    headers = ["Timestamp", "Actor", "Action", "Detail"]
    widths = [20, 18, 24, 40]

    lines.append(_text_row(headers, widths))
    lines.append("-" * 78)

    entries = activity_entries(limit=MAX_ACTIVITY_ENTRIES)

    for entry in entries:
        lines.append(_text_row([
            entry.get("timestamp", ""),
            entry.get("actor", ""),
            entry.get("action", ""),
            entry.get("detail", "")
        ], widths))

    lines.append("")
    lines.append(f"Total entries: {len(entries)}")

    return "\n".join(lines) + "\n"


def write_text_report(path, content):
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
    except OSError as error:
        return False, f"Unable to write the report: {error}"

    return True, path


ensure_default_users()

try:
    save_data()
except OSError:
    pass
