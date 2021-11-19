import re
import pandas as pd


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
    departments = re.split(DEPARTMENT_ARRAY[0], html)[
        1:]
    for department in departments:
        dep = re.split(DEPARTMENT_ARRAY[1], department)[0]
        for title in re.split(TITLE, department)[1:]:
            counter += 1
            dikt = dict()
            dikt['Department'] = dep
            tit = find_values(title, TITLE_ARRAY)
            dikt['Title'] = tit
            tex = find_values(title, TEXT_ARRAY)
            dikt['Text'] = tex
            fri = find_values(title, FRIST_ARRAY)
            if fri is not None:
                dikt['Vernehmlassung Day'] = fri[0]
                dikt['Vernehmlassung Month'] = fri[1]
                dikt['Vernehmlassung Year'] = fri[2]
            else:
                dikt['Vernehmlassung Day'] = None
                dikt['Vernehmlassung Month'] = None
                dikt['Vernehmlassung Year'] = None
            beh = find_values(title, BEHOERDE_ARRAY)
            dikt['Behoerde'] = beh
            num = find_values(title, NUMMERN_ARRAY)
            if num is not None:
                dikt['SR Links'] = num[0]
                dikt['SR Numbers'] = num[1]
            else:
                dikt['SR Links'] = None
                dikt['SR Numbers'] = None
            dikts.append(dikt)
    df = pd.DataFrame(dikts)
    print(counter)
    if counter == 0:
        return None
    return df
