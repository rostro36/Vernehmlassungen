import datetime
import statistics
from ast import literal_eval
import pandas as pd
from download import get_page
from process import process_year, process_link
from variables import YEAR_BASE, HISTORY_BASE


def scrape_vernehmlassungen():
    # Init values
    df_dict = dict()
    # Loop over years
    for retry in range(3):
        for year in range(1992, 2022):
            print(year)
            if year not in df_dict:
                html = get_page(YEAR_BASE+str(year), retry)
                processed = process_year(html)
                if processed is not None:
                    df_dict[year] = processed
    # Concat df's
    dfs = []
    for year in df_dict:
        dfs.append(df_dict[year])
    df = pd.concat(dfs)
    df.to_csv('vernehmlassungen.csv')
    return df


def decide_delta(vernehmlassung_date, acc_dates, deltas):
    # Remove Nones
    clean_acc_dates = [i for i in acc_dates if i]
    if len(clean_acc_dates) == 0:
        return None, None, None
    # Find most seen acc_date
    accept_date = statistics.mode(clean_acc_dates)
    # Compute mean of decision deltas with correct acc_date
    deltas = [deltas[i]
              for i in range(len(deltas)) if accept_date == acc_dates[i]]
    delta = statistics.mean(deltas)
    # Compute values
    decision_delta = datetime.timedelta(days=delta)
    decision_date = vernehmlassung_date+decision_delta
    return decision_delta, decision_date, accept_date


def scrape_laws(vernehmlassungen_df):
    new_df = []
    for _, row in vernehmlassungen_df.iterrows():
        links = row['SR_Links']
        # No Links found
        if links is None or type(links) == float:
            new_df.append([None]*8)
            continue

        # Compute links
        if type(links) == str:
            links = literal_eval(links)
        link_count = len(links)

        # Init values for loop
        vernehmlassung_date = datetime.date(
            row['Vernehmlassung_Year'], row['Vernehmlassung_Month'], row['Vernehmlassung_Day'])
        deltas = [None]*link_count
        acc_dates = [None]*link_count

        # Loop over links
        for retry in range(5):
            for link_pos in range(link_count):
                # Link_pos already found
                if deltas[link_pos] is None:
                    history = get_page(
                        HISTORY_BASE+links[link_pos]+'/history', retry)
                    deltas[link_pos], acc_dates[link_pos] = process_link(
                        history, vernehmlassung_date)
        # Untangle the different deltas
        decision_delta, decision_date, accept_date = decide_delta(
            vernehmlassung_date, acc_dates, deltas)
        # Values found
        if decision_delta:
            new_df.append([decision_delta.days/30, decision_date.day, decision_date.month, decision_date.year,
                           (accept_date-vernehmlassung_date).days /
                           30, accept_date.day,
                           accept_date.month, accept_date.year])
        # No values found
        else:
            new_df.append([None]*8)
    # concat df's
    new_df = pd.DataFrame(new_df, columns=['Months_until_decision', 'Decision_day', 'Decision_month', 'Decision_year',
                                           'Months_until_accept', 'Accept_day', 'Accept_month', 'Accept_year']).reset_index()
    concat_df = pd.concat([vernehmlassungen_df.reset_index(), new_df], axis=1)
    concat_df.to_csv('laws.csv')
    return concat_df


if __name__ == "__main__":
    # Scrape Vernehmlassungen
    vernehmlassungen_df = scrape_vernehmlassungen()
    # Scrape adjacent laws
    laws_df = scrape_laws(vernehmlassungen_df)
