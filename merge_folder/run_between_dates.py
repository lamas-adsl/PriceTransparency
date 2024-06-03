import sys
from datetime import datetime, timedelta

import auto_process


def generate_dates_between(start_date, end_date):
    # Parse the input dates
    start_date = datetime.strptime(start_date, "%d-%m-%Y")
    end_date = datetime.strptime(end_date, "%d-%m-%Y")

    # Generate the list of dates
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime("%d-%m-%Y"))
        current_date += timedelta(days=1)

    return date_list


start = sys.argv[1]
end = sys.argv[2]

dates = generate_dates_between(start, end)
for date in dates:
    auto_process.run(date)