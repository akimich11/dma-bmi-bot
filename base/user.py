class User:
    def __init__(self, **kwargs):
        self.raw_data = kwargs

    @property
    def username(self):
        return None if self.raw_data['username'] == 'undefined' else self.raw_data['username']

    @property
    def first_name(self):
        return self.raw_data['first_name']

    @property
    def last_name(self):
        return self.raw_data['last_name']

    @property
    def id(self):
        return int(self.raw_data['id'])

    @property
    def is_admin(self):
        return bool(self.raw_data['is_admin'])

    @property
    def skips_month(self):
        return self.raw_data['skips_month']

    @property
    def skips_semester(self):
        return self.raw_data['skips_semester']
