

import StatementData as StatementData
import Logger as Logger
import datetime as datetime
import copy as copy

# the database of statement data
statement_entries: list = []
weekly_summaries: list = []
monthly_summaries: list = []

# parsed text, list of tuples (valid data: bool, text line: str)
parsed_text = []

# does data need committing to file
is_dirty: bool = False

# current max entry sequence no
seq_no: int = -1


# ------------------------------------------------------
# database dirty flag
def set_dirty(dirty: bool = True):
    global is_dirty
    if is_dirty != dirty:
        Logger.log_info(f'Dirty flag changed {is_dirty} -> {dirty}')
    is_dirty = dirty


def get_is_dirty():
    global is_dirty
    return is_dirty


# ------------------------------------------------------
# add entry to statement entries list in the correct order
# returns position in list if added to list, -1 if it already exists in the list
def add_statement_entry(entries: [], entry: StatementData.StatementEntry) -> int:

    n = 0
    while n < len(entries):

        if StatementData.is_equal_statement_entries(entry, entries[n]):
            return -1

        if StatementData.compare_statement_entries(entry, entries[n]) == -1:
            entries.insert(n, entry)
            return n

        n += 1

    entries.append(entry)
    return n


# -----------------------------------------------------
# get next sequence number
def next_seq_no() -> int:
    global seq_no
    seq_no += 1
    return seq_no


# -----------------------------------------------------
# reset sequence number
def reset_seq_no() -> None:
    global seq_no
    seq_no = -1


# -----------------------------------------------------
# read data from file
def read_file(file_name: str) -> bool:
    global statement_entries
    statement_entries = []

    try:
        with open(file_name, mode='r', encoding="utf-8") as f:
            ls = f.readlines()

        # which version of data
        if ls[0][:-1] == "Money Reckoner 1.10":
            vers: float = 1.1
        elif ls[0][:-1] == "Money Reckoner 1.20":
            vers: float = 1.2
        elif ls[0][:-1] == "Money Reckoner 1.30":
            vers: float = 1.3
        elif ls[0][:-1] == "Money Reckoner 1.40":
            vers: float = 1.4
        else:
            raise RuntimeError(f'Invalid header \'{ls[0]}\' in file \'{file_name}\'')

        # parse lines from file
        for n in range(1, len(ls)):
            entry = StatementData.StatementEntry()
            if entry.from_csv(ls[n], vers):
                entry.index = add_statement_entry(statement_entries, entry)
            else:
                Logger.log_error(f'Error parsing line ({n}) : \'{ls[n]}\'')
                return False

        # assign sequence numbers
        reset_seq_no()
        for entry in statement_entries:
            entry.seq_no = next_seq_no()

        Logger.log_info(f'Read {len(statement_entries)} entries from file \'{file_name}\'')
        global seq_no
        Logger.log_info(f'Max sequence number: {seq_no}')
        return True

    except FileNotFoundError:
        Logger.log_error(f'Could not find file {file_name}')
        return False
    except RuntimeError as e:
        Logger.log_error(repr(e))
        return False


# ------------------------------------------------------
# write to file
def write_file (filename: str) -> bool:

    try:
        with open(filename, mode='w', encoding="utf-8") as f:
            f.write("Money Reckoner 1.40\n")
            global statement_entries
            for se in statement_entries:
                f.write(se.to_csv())
                f.write('\n')

            Logger.log_info(f'Data saved to \'{filename}\'')

    except FileNotFoundError:
        Logger.log_error(f'Could not write to file {filename}')
        return False
    except RuntimeError as e:
        Logger.log_error(repr(e))
        return False


# ------------------------------------------------------
def generate_weekly_summaries() -> None:
    global weekly_summaries
    weekly_summaries = []
    week_no = 0
    summary = StatementData.StatementSummary()

    for entry in statement_entries:
        if week_no != entry.week_no:

            # new week
            week_no = entry.week_no

            # add previous summary to summaries list
            if len(summary.entries) > 0:
                calculate_weekly_summary(summary)
                weekly_summaries.append(summary)

            # start summary for the new week
            summary = StatementData.StatementSummary()
            summary.summary_id = entry.week_no_str

            # set summary date to the start of the week
            summary.summary_date = copy.copy(entry.date) - datetime.timedelta(days=entry.date.weekday())

        # accumulate summary data
        add_statement_entry(summary.entries, entry)

    # add final summary to summaries list
    if len(summary.entries) > 0:
        calculate_weekly_summary(summary)
        weekly_summaries.append(summary)


# ------------------------------------------------------
def calculate_weekly_summary(summary: StatementData.StatementSummary) -> None:
    summary.total = 0
    summary.transactions = 0
    for entry in summary.entries:
        if entry.included_weekly and not entry.user_excluded:
            summary.total -= entry.amount
            summary.transactions += 1


# ------------------------------------------------------
def generate_monthly_summaries() -> None:
    global monthly_summaries
    monthly_summaries = []
    ms = ''
    summary = StatementData.StatementSummary()

    for entry in statement_entries:
        if ms != entry.month_str:

            # new month
            ms = entry.month_str

            # add previous summary to summaries list
            if len(summary.entries) > 0:
                calculate_monthly_summary(summary)
                monthly_summaries.append(summary)

            # start summary for the new ms
            summary = StatementData.StatementSummary()
            summary.summary_id = ms

            # set summary date to the start of the week
            summary.summary_date = datetime.date(entry.date.year, entry.date.month, 1)

        add_statement_entry(summary.entries, entry)

    # add final summary to summaries list
    if len(summary.entries) > 0:
        calculate_monthly_summary(summary)
        monthly_summaries.append(summary)


# ------------------------------------------------------
def calculate_monthly_summary(summary: StatementData.StatementSummary) -> None:
    summary.total = 0
    summary.transactions = 0
    for entry in summary.entries:
        if entry.included_monthly and not entry.user_excluded:
            summary.total -= entry.amount
            summary.transactions += 1


# ------------------------------------------------------
def clear_parsed_text():
    global parsed_text
    parsed_text = []


# ------------------------------------------------------
def add_parsed_line(contains_data: bool, line: str):
    global parsed_text
    parsed_text.append((contains_data, line))


# ------------------------------------------------------
def update_user_excluded(entry: StatementData.StatementEntry):

    # toggle user exclusion
    entry.user_excluded = not entry.user_excluded

    # update weekly summary
    for summary in weekly_summaries:
        if summary.summary_id == entry.week_no_str:
            calculate_weekly_summary(summary)
            break

    # update monthly summary
    for summary in monthly_summaries:
        if summary.summary_id == entry.month_str:
            calculate_monthly_summary(summary)
            break

    set_dirty()

