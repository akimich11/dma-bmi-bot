def get_poll(polls, last_poll_id, poll_question):
    if poll_question is not None:
        for p, v in polls.values():
            if poll_question.lower() in p.question.lower():
                return p, v
        else:
            return None, None
    else:
        if last_poll_id is not None:
            return polls[last_poll_id]
        return None, None


def get_probability(polls, user_id, poll_question):
    num_attends = 0
    num_polls = 0
    for poll, votes in polls.values():
        question_to_find = poll_question.split()[0].lower().replace('/', '')
        real_question = poll.question.lower().replace('/', '')
        if question_to_find in real_question and user_id in votes:
            for option in votes[user_id]:
                if 'не' in option.lower():
                    break
            else:
                num_attends += 1
            num_polls += 1
    if not num_polls:
        return 0.
    return 100. * (num_attends / num_polls)
