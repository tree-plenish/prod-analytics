from re import X
import numpy as np
import pandas as pd
import time
from datetime import datetime
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import BarChart, Reference, Series
from tech_team_database.dependencies.DatabaseSQLOperations import TpSQL
from deps.gdrive import GoogleDriveOperations


class Dashboard:
    """
    Looped retrieval, update and upload of an internal tree request
    dashboard. Update Time Independent but will be looped by main hourly.
    INCLUDES: 
    schoolcode
    # Trees Sold
    % Tree Goal Reached
    # Saplings Over last 7 days
    Uploaded via existing gdrive wrapper.
    """

    def __init__(self):
        """ Loop through full processes once called. """

        self.g = GoogleDriveOperations.GDrive()  # Google Drive handle

        self.tpsql = TpSQL()  # database handle
        orders = self.retrieve_data()
        self.schoolcodes = np.unique(orders["schoolid"]).tolist()

        data = self.update_data(orders)

        self.upload_data(data, orders)

    def retrieve_data(self):
        """ Making call to tree_order table... nothing else needed. """
        return self.tpsql.getTable("tree_order")

    def update_data(self, orders):
        """ Initializing base ids & calling all of the data update functions.
        Args:
            orders (df): current tree_order table
        """

        data = pd.DataFrame(index=self.schoolcodes)
        data["sapling count"] = self.get_sapling_counts(
            orders, self.schoolcodes)
        data["weekly sapling count"] = self.get_recent_sapling_counts(
            orders, self.schoolcodes, 7)

        return data

    def update_contest(self, schools, orders, times):
        """ Returns dataframe with time periods as columns and schools (schoolcode) as rows
            Times should be a list of dictionaries with start times as keys and end times as values
            Called in upload_data
        """
        orders = orders.sort_values(by='submit_time')
        contest = pd.DataFrame(schools, columns=["schoolid"])
        contest.index = schools
        i = 0
        for time in times:
            contest[datetime.fromtimestamp(list(time.keys())[0])] = 0
            while i < len(orders):
                if orders.iloc[i]['submit_time'] >= list(time.keys())[0] and orders.iloc[i]['submit_time'] <= time[list(time.keys())[0]]:
                    contest.iat[contest['schoolid'].tolist().index(orders.iloc[i]['schoolid']), times.index(time) + 1] += orders.iloc[i]['number']
                i += 1                  

        return contest

    def upload_data(self, data, orders):

        # First, write xlsx workbook (is just here locally in prod-analytics)
        wb = Workbook()

        # Getting sheets & loop through dataframe assigning vals
        ws1 = wb.create_sheet("Total Counts", 0)
        ws2 = wb.create_sheet("Biweekly Competitions", 1)
        ws3 = wb.create_sheet("Unaggregated Data", 2)

        # Sheet 1: Clean Count Data
        for r in dataframe_to_rows(data, index=True):
            ws1.append(r)

        # Sheet 2: Biweekly Competitions
        # times should be a list of dictionaries with the start time as the key and the end time as the value.
        starting_unix = 1642957200
        delta_unix = 1209600  # 60 * 60 * 24 * 14
        competition_count = (time.time() - starting_unix) // delta_unix + 1 # Quick calc. for # of competitions so far

        times = [{starting_unix + i * delta_unix : starting_unix + (i + 1) * delta_unix} for i in range(int(competition_count) + 1)]
        contest = self.update_contest(self.schoolcodes, orders, times)
        for r in dataframe_to_rows(contest, index=True):
            ws2.append(r)

        # Sheet 3: Unaggregated Data to go into chart
        for r in dataframe_to_rows(orders, index=True):
            ws3.append(r)

        wb.save("Tree Request Dash.xlsx")

        # Uploading using drive
        fileID = "1ok7JfQjYaCu4KFusElqI-HXbq3aAj6Gn"  # gDrive file ID for the sheet
        self.g.updateFile("Tree Request Dash.xlsx", fileID)
        print("https://drive.google.com/file/d/" +
              str(fileID) + "/view?usp=sharing")

    #########################
    # SPECIFIC UPDATE FUNCS #
    #########################

    def get_sapling_counts(self, orders, schoolcodes):
        """ Getting list of sapling counts for the entire event cycle.
        Args:
            orders (df): current tree_order table
            schoolcodes (list): list of school ids
        """
        sapling_counts = []
        for code in schoolcodes:

            rows = orders[orders["schoolid"] == code]
            sapling_counts.append(int(sum(rows["number"].values)))

        return sapling_counts

    def get_recent_sapling_counts(self, orders, schoolcodes, days):
        """ Getting list of sapling counts for the entire event cycle.
        Args:
            orders (df): current tree_order table
            schoolcodes (list): list of school ids
            days (int): cutoff for recent count
        """
        sapling_counts = []
        # Current time - Number of seconds in a day * Number of days
        unix_cutoff = time.time() - 86400 * days

        for code in schoolcodes:

            rows = orders[orders["schoolid"] == code]
            rows = rows[rows["submit_time"] >= unix_cutoff]
            sapling_counts.append(int(sum(rows["number"].values)))

        return sapling_counts


# Call
dash = Dashboard()