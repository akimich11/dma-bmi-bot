from base.decorators import db


class TimetableService:
    @staticmethod
    @db.fetch(return_type='all_tuples')
    def get_timetable_for_day(department_id, sub_department, weekday, cursor):
        cursor.execute("SELECT start_time, subject, type, auditory FROM timetables "
                       "WHERE weekday=%s AND department_id=%s AND sub_department LIKE %s "
                       "ORDER BY start_time",
                       (weekday, department_id, f'%{sub_department}%'))

    @staticmethod
    @db.fetch(return_type='all_tuples')
    def get_timetable_for_week(department_id, sub_department, cursor):
        cursor.execute("SELECT weekday, start_time, subject, type, auditory FROM timetables "
                       "WHERE department_id=%s AND sub_department LIKE %s "
                       "ORDER BY weekday, start_time",
                       (department_id, f'%{sub_department}%'))

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
