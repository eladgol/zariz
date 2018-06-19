from django.utils.html import conditional_escape as esc
from django.utils.safestring import mark_safe
from itertools import groupby
from calendar import HTMLCalendar, monthrange

class ContestCalendar(HTMLCalendar):

    def __init__(self, pContestEvents):
        super(ContestCalendar, self).__init__()
        self.contest_events = self.group_by_day(pContestEvents)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.contest_events:
                cssclass += ' filled'
                body = []
                for contest in self.contest_events[day]:
                    body.append('<a href="%s">' % contest.get_absolute_url())
                    body.append(esc(contest.contest.name))
                    body.append('</a><br/>')
                return self.day_cell(cssclass, '<div class="dayNumber">%d</div> %s' % (day, ''.join(body)))
            return self.day_cell(cssclass, '<div class="dayNumber">%d</div>' % day)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(ContestCalendar, self).formatmonth(year, month)

    def group_by_day(self, pContestEvents):
        field = lambda contest: contest.date_of_event.day
        return dict(
            [(day, list(items)) for day, items in groupby(pContestEvents, field)]
        )

    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)

