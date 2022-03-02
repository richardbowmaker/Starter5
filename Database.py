

import StatementData as StatementData
import Logger as Logger
import datetime as datetime
import copy as copy

# the database of statement data
statement_entries: list = []
weekly_summaries: list = []
monthly_summaries: list = []

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
# returns true if added to list, false if it already exists in the list
def add_statement_entry(entries: [], entry: StatementData.StatementEntry) -> bool:

    for n in range(len(entries)):

        if StatementData.is_equal_statement_entries(entry, entries[n]):
            return False

        if StatementData.compare_statement_entries(entry, entries[n]) == -1:
            entries.insert(n, entry)
            return True

    entries.append(entry)
    return True


# -----------------------------------------------------
# get next sequence number
def next_seq_no() -> int:
    global seq_no
    seq_no += 1
    return seq_no


# -----------------------------------------------------
# reset sequence number
def reset_seq_no() -> int:
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
        else:
            raise RuntimeError(f'Invalid header \'{ls[0]}\' in file \'{file_name}\'')

        # parse lines from file
        for n in range(1, len(ls)):
            entry = StatementData.StatementEntry()
            if entry.from_csv(ls[n], vers):
                add_statement_entry(statement_entries, entry)
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
            f.write("Money Reckoner 1.30\n")
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

    for se in statement_entries:
        if week_no != se.week_no:

            # new week
            week_no = se.week_no

            # add previous summary to summaries list
            if len(summary.entries) > 0:
                weekly_summaries.append(summary)

            # start summary for the new week
            summary = StatementData.StatementSummary()
            summary.summary_id = f'{week_no}'

            # set summary date to the start of the week
            summary.summary_date = copy.copy(se.date) - datetime.timedelta(days=se.date.weekday())

        # accumulate summary data
        if se.included_weekly:
            summary.total -= se.amount
        summary.transactions += 1
        add_statement_entry(summary.entries, se)

    # add final summary to summaries list
    if len(summary.entries) > 0:
        weekly_summaries.append(summary)


# ------------------------------------------------------
def generate_monthly_summaries() -> None:
    global monthly_summaries
    monthly_summaries = []
    month = ''
    summary = StatementData.StatementSummary()

    for se in statement_entries:
        ms = f'{se.date.month}\\{se.date.year}'
        if month != ms:

            # new month
            month = ms

            # add previous summary to summaries list
            if len(summary.entries) > 0:
                monthly_summaries.append(summary)

            # start summary for the new month
            summary = StatementData.StatementSummary()
            summary.summary_id = ms

            # set summary date to the start of the week
            summary.summary_date = datetime.date(se.date.year, se.date.month, 1)

        # accumulate summary data
        if se.included_monthly:
            summary.total -= se.amount
        summary.transactions += 1
        add_statement_entry(summary.entries, se)

    # add final summary to summaries list
    if len(summary.entries) > 0:
        monthly_summaries.append(summary)



