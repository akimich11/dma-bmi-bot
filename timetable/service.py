from base import db


class TimetableService(db.ConnectionMixin):
    @classmethod
    @db.fetch(return_type='all_tuples')
    def get_timetable_for_day(cls, sub_department, weekday, cursor):
        cursor.execute("SELECT start_time, subject, type, auditory FROM timetables "
                       "WHERE weekday=%s AND sub_department LIKE %s "
                       "ORDER BY start_time",
                       (weekday, f'%{sub_department}%'))

    @classmethod
    @db.fetch(return_type='all_tuples')
    def get_timetable_for_week(cls, sub_department, cursor):
        cursor.execute("SELECT weekday, start_time, subject, type, auditory FROM timetables "
                       "WHERE sub_department LIKE %s "
                       "ORDER BY weekday, start_time",
                       (f'%{sub_department}%',))

    @staticmethod
    def parse_timetable_for_day(timetable, weekday):
        sheet = []
        for day, time, subject, subject_type, auditory in timetable:
            if day != weekday:
                continue
            sheet.append(f'{time:%H:%M} | {subject:^5.5} | {subject_type} | {auditory}')
        if not sheet:
            return f'{weekday}: пар нет, повезло-повезло\n\n'
        return weekday + '\n<pre>' + '\n'.join(sheet) + '</pre>\n\n'

    @staticmethod
    def get_pretty_timetable(timetable):
        sheet = []
        for time, subject, subject_type, auditory in timetable:
            sheet.append(f'{time:%H:%M} | {subject:^5.5} | {subject_type} | {auditory}')

        return '<pre>' + '\n'.join(sheet) + '</pre>'

    @classmethod
    @db.get_cursor
    def check_if_sub_department_exists(cls, sub_department, cursor):
        cursor.execute("SELECT id FROM timetables WHERE sub_department LIKE %s", (f'%{sub_department}%',))
        return cursor.fetchone() is not None
