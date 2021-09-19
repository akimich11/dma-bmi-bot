class User:
    def __init__(self, user_id, username, first_name, last_name,
                 department, is_admin, is_voenka, former_group, skips_month, skips_semester, *args):
        self.username = None if username == 'undefined' else username
        self.first_name = first_name
        self.last_name = last_name
        self.id = int(user_id)
        self.department = department
        self.is_admin = bool(is_admin)
        self.is_voenka = bool(is_voenka)
        self.former_group = former_group
        self.skips_month = skips_month
        self.skips_semester = skips_semester
