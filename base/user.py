class User:
    def __init__(self, **kwargs):
        self.username = None if kwargs['username'] == 'undefined' else kwargs['username']
        self.first_name = kwargs['first_name']
        self.last_name = kwargs['last_name']
        self.id = int(kwargs['id'])
        self.is_admin = bool(kwargs['is_admin'])
        self.department = kwargs['department'].lower()
        self.skips_month = kwargs['skips_month']
        self.skips_semester = kwargs['skips_semester']
