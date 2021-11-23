import re
import datetime
import pandas as pd
from variables import month_dict


def clean_text(text):
    text = text.strip()
    non_html = re.sub(r'<[^>]*>', ' ', text)
    non_linebreak = non_html.replace("\n", " ")
    return non_linebreak


def parse_date(date_string):
    output = []
    for i in re.split(r'\.', date_string):
        output.append(int(i))
    return output


def find_values(string, array):
    if re.search(array[0], string) is None:
        return None
    cut_front = re.split(array[0], string)[1]
    cut_back = re.split(array[1], cut_front)[0]
    processed = array[2](cut_back)
    return processed


def parse_numbers(string):
    SRnumbers = []
    links = []
    for number in re.split('href="', string)[1:]:
        links.append(re.split('">', number)[0])
        start = re.split('">', number)[1]
        SRnumbers.append(re.split(r'</a>', start)[0].strip())
    return [links, SRnumbers]


# Values for different values
DEPARTMENT_ARRAY = [
    r'<a _ngcontent-\w+-\w+="" id="', r'">', lambda x: x.strip()]
TEXT_ARRAY = [r'<li _ngcontent-\w+-\w+="">\s*<span _ngcontent-\w+-\w+="">\s*',
              r'</span>', lambda x: clean_text(x)]
TITLE_ARRAY = [r'">', r'</strong>', lambda x: clean_text(x)]
TITLE = r'<!-- -->\s*<h5 _ngcontent-\w+-\w+="">\s*<strong _ngcontent-\w+-\w+="'
BEHOERDE_ARRAY = [
    r'Behörde:\s*</i>\s*</strong>\s*<span _ngcontent-\w+-\w+="">', '</span>', lambda x: x.strip()]
FRIST_ARRAY = [r'</span>\s*<span _ngcontent-\w+-\w+="">',
               r'</span>', lambda x: parse_date(x)]
NUMMERN_ARRAY = [r'Betroffene SR Nummer', r'</li>', lambda x: parse_numbers(x)]


def process_year(html):
    counter = 0
    dikts = []
    # First split
    departments = re.split(DEPARTMENT_ARRAY[0], html)[1:]
    # Across different departments
    for department in departments:
        dep = re.split(DEPARTMENT_ARRAY[1], department)[0]
        # Different Vernehmlassungen
        for title in re.split(TITLE, department)[1:]:
            counter += 1
            dikt = dict()
            dikt['Department'] = dep
            tit = find_values(title, TITLE_ARRAY)
            dikt['Title'] = tit
            tex = find_values(title, TEXT_ARRAY)
            dikt['Text'] = tex
            fri = find_values(title, FRIST_ARRAY)
            # If no Frist found
            if fri is not None:
                dikt['Vernehmlassung_Day'] = fri[0]
                dikt['Vernehmlassung_Month'] = fri[1]
                dikt['Vernehmlassung_Year'] = fri[2]
            else:
                dikt['Vernehmlassung_Day'] = None
                dikt['Vernehmlassung_Month'] = None
                dikt['Vernehmlassung_Year'] = None
            beh = find_values(title, BEHOERDE_ARRAY)
            dikt['Behoerde'] = beh
            num = find_values(title, NUMMERN_ARRAY)
            # If no Links found
            if num is not None:
                dikt['SR_Links'] = num[0]
                dikt['SR_Numbers'] = num[1]
                dikt['Link_count'] = len(num[0])
            else:
                dikt['SR_Links'] = None
                dikt['SR_Numbers'] = None
                dikt['Link_count'] = None
            dikts.append(dikt)
    # Concat dfs
    df = pd.DataFrame(dikts)
    if counter == 0:
        return None
    return df


def make_date(date_string):
    cut_date = re.split(r'</td>', date_string)[0]
    (day, month, year) = re.split(
        r' ', cut_date)[:3]
    return_date = datetime.date(
        int(year.strip()), month_dict[month.strip()], int(day.strip()[:-1]))
    return return_date


def process_link(history, vernehmlassung_date):
    # Init values for loop
    return_delta = None
    return_acc_date = None
    history_entries = re.split(r'<tr _ngcontent', history)[2:]
    # Loop across different history entries
    for entry in history_entries:
        if len(re.split(r'class="nowrap"> [0-9]', entry)[1:]) >= 2:
            dates = re.split(r'class="nowrap"> ', entry)[1:3]
            decision_date = make_date(dates[0])
            temp_accept_date = make_date(dates[1])
            # Write dates, if they are after vernehmlassung
            if (decision_date-vernehmlassung_date).days >= 0 and (temp_accept_date-decision_date).days >= 0:
                return_delta = (
                    decision_date-vernehmlassung_date).days
                return_acc_date = temp_accept_date
    return return_delta, return_acc_date
