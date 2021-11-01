from base.decorators.db import connector


class Question:
    def __init__(self, **kwargs):
        self.question = kwargs['question']
        self.options = kwargs['options'].split(',')
        self.is_multi = bool(kwargs['is_multi'])
        self.weekday = kwargs['weekday']
        self.time = str(kwargs['utc_time'])


class QuestionModel:
    def __init__(self):
        self.cursor = None
        self.conn = None
        self.questions = []
        self.__init_questions()

    @connector
    def __init_questions(self):
        self.cursor.execute("""SELECT * FROM questions""")
        data = self.cursor.fetchall()
        column_names = [column[0] for column in self.cursor.description]
        if data is not None:
            for row in data:
                self.questions.append(Question(**dict(zip(column_names, row))))
