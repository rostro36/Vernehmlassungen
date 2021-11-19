from ast import literal_eval
import datetime
from variables import month, HISTORY_BASE
from download import get_page
import re
import pandas as pd
import statistics
import time

df = pd.read_csv('second_data.csv')

new_df = []
for _, row in df.iterrows():
    links = row['SR Links']
    vernehmlassung_date = datetime.date(
        row['Vernehmlassung Year'], row['Vernehmlassung Month'], row['Vernehmlassung Day'])
    if type(links) == float:
        new_df.append([None]*9)
        continue
    links = literal_eval(links)
    link_count = len(links)
    deltas = [None]*link_count
    acc_dates = [None]*link_count
    print(links)
    for retry in range(5):
        for link_pos in reversed(range(link_count)):
            if deltas[link_pos] is None:
                acc_date = None
                history = get_page(HISTORY_BASE+links[link_pos]+'/history')
                time.sleep(2+pow(3, retry))
                entries = re.split(r'<tr _ngcontent', history)[2:]
                for entry in entries:
                    if len(re.split(r'class="nowrap"> [0-9]', entry)[1:]) >= 2:
                        dates = re.split(r'class="nowrap"> ', entry)[1:3]
                        decision_date = re.split(r'</td>', dates[0])[0]
                        (day, curr_month, year) = re.split(
                            r' ', decision_date)[:3]
                        decision_date = datetime.date(
                            int(year.strip()), month[curr_month.strip()], int(day.strip()[:-1]))
                        temp_accept_date = re.split(r'</td>', dates[1])[0]
                        (day, curr_month, year) = re.split(
                            r' ', temp_accept_date)[:3]
                        temp_accept_date = datetime.date(
                            int(year.strip()), month[curr_month.strip()], int(day.strip()[:-1]))
                        if (decision_date-vernehmlassung_date).days >= 0 and (decision_date-temp_accept_date).days <= 0:
                            deltas[link_pos] = (
                                decision_date-vernehmlassung_date).days
                            acc_dates[link_pos] = temp_accept_date
    print(deltas)
    clean_acc_dates = [i for i in acc_dates if i]
    if len(clean_acc_dates) == 0:
        placeholder = [None]*9
        placeholder[0] = link_count
        new_df.append(placeholder)
        print(placeholder)
        continue
    accept_date = statistics.mode(clean_acc_dates)
    deltas = [deltas[i]
              for i in range(len(deltas)) if accept_date == acc_dates[i]]
    delta = statistics.mean(deltas)
    decision_delta = datetime.timedelta(days=delta)
    decision_date = vernehmlassung_date+decision_delta
    print(vernehmlassung_date)
    print(decision_date)
    print(accept_date)
    new_df.append([link_count, decision_delta.days/30, decision_date.day, decision_date.month, decision_date.year,
                   (accept_date-vernehmlassung_date).days/30, accept_date.day, accept_date.month, accept_date.year])
new_df = pd.DataFrame(new_df, columns=['Link_count', 'Months until decision', 'Decision day', 'Decision month',
                      'Decision year', 'Months until accept', 'Accept day', 'Accept month', 'Accept year'])

concat_df = pd.concat([df, new_df], axis=1)
concat_df.to_csv('concat_data.csv')
