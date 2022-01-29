from base.decorators import db


class TimetableService:
    @staticmethod
    @db.fetch(return_type='all_tuples')
    def get_timetable(department_id, sub_department, weekday, cursor=None):
        cursor.execute("SELECT start_time, subject, type, auditory FROM timetables "
                       "WHERE weekday=%s AND department_id=%s AND (sub_department=%s OR sub_department IS NULL)"
                       "ORDER BY start_time",
                       (weekday, department_id, sub_department))
