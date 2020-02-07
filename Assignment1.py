#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 15:48:36 2020

@author: samoaa
"""

import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import scipy.stats as stats


def plot_bar():
   df_agg[df_agg < 0] = 0
   # histogram
   plt.bar(df_agg.index,df_agg)
   fig = sm.qqplot(df_agg, stats.t, distargs=(4,))

def change_request(rest):
    queries = 0
    has_more = True
    gerrit_status = 'merged'
    start = 0

    while has_more and queries < 1000:

        changes = rest.get(
            "/changes/?q=status:" + gerrit_status + "&o=ALL_REVISIONS&o=ALL_COMMITS&o=ALL_FILES&o=MESSAGES&start={}".format(
                start), headers={'Content-Type': 'application/json'})

        queries += 1

        # mber_of_changes = len(changes)

        # and if there are more pages of export
        # then we move on and get the next page
        # pp.pprint(changes[number_of_changes-1])
        if "_more_changes" in changes[len(changes) - 1]:
            has_more = True

        else:
            has_more = False

        print("number of changes {}".format(len(changes)))

        for iIndex, change in enumerate(changes, start=1):
            changeID = change['id']
            revisions = change['revisions']

            if iIndex % 10 == 0:
                print("Extracting change: " + str(iIndex) + " of " + str(len(changes)) + " starting at : " + str(start))

            for revID in list(revisions.keys()):
                try:
                    # getting files in revisions

                    files = rest.get("/changes/%s/revisions/%s/files/" % (changeID, revID),
                                     headers={'Content-Type': 'application/json'})

                    commit = rest.get("/changes/%s/revisions/%s/commit/" % (changeID, revID),
                                      headers={'Content-Type': 'application/json'})

                    check_change = rest.get("/changes/%s/check" % (changeID),
                                            headers={'Content-Type': 'application/json'})

                    if len(check_change["problems"] > 0):
                        print("number of problems {0}".format(len(check_change["problems"])))

                    timestamp = commit['committer']['date']
                    author = commit['committer']['name']
                    # tags = rest.get("/changes/%s/t" % changeID, headers={'Content-Type': 'application/json'})

                    fileID, lines_inserted, lines_deleted, churn_on_file, churn, Nbugs = "", 0, 0, 0, 0, 0

                    if len(files) > 0:
                        for index, file in enumerate(files):
                            fileID = os.path.basename(file)

                            if '.' in fileID:
                                print("number of files: {} ".format(len(files)))
                                # for file in files:

                                lines_inserted = list(files.values())[index + 1]['lines_inserted']
                                lines_deleted = list(files.values())[index + 1]['lines_deleted']
                                churn_on_file = lines_inserted - lines_deleted

                                churn = churn + (lines_inserted - lines_deleted)
                                print("lines inserted: {}".format(lines_inserted))
                                print("lines deleted: {}".format(lines_deleted))
                                print("file churn: {}".format(churn_on_file))

                                with open("data.csv", mode='a') as csv_file:
                                    diff_writer = csv.writer(csv_file, delimiter=';',
                                                             quoting=csv.QUOTE_MINIMAL)
                                    diff_writer.writerow(
                                        [revID, fileID, lines_inserted, lines_deleted, churn_on_file, author,
                                         str(timestamp),
                                         Nbugs])


                except:
                    has_more = False
        if has_more:
            start += 500


def _authenticate_with_gerrit():
    # username = '-'
    # password = '-'
    # auth = HTTPBasicAuth(username, password)

    gerrit_url = 'https://code.wireshark.org/review/'
    # this line gets sets the parameters for the HTML API
    rest = GerritRestAPI(url=gerrit_url)  # add auth=auth as an argument

    change_request(rest)


def _total_churn_per_week_by_developer():
    data = pandas.read_csv("data.csv", sep=';')
    #data[['date', 'time']] = data['time'].str.split(' ', n=1, expand=True)

    data['formatted_date'] = pandas.to_datetime(data['time'])
    data['day_of_year'] = data.formatted_date.apply(lambda x: x.dayofyear)
    data['week_of_year'] = data.formatted_date.apply(lambda x: x.weekofyear)

    dd = data.groupby('week_of_year')['code_churn'].sum()

    threshold = dd.iloc[:len(dd) - 1, ].mean()
    current = dd.iloc[len(dd) - 1]


    if current > threshold:
        print('Green')
    else:
        print('Red')


def main():
    _authenticate_with_gerrit()
    _total_churn_per_week_by_developer()
    plot_bar()


main()