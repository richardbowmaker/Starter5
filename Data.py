
from StatementEntry import *
from Logger import *
from functools import cmp_to_key

global statement_entries
statement_entries = []


def compare_statement_entries(se1: StatementEntry, se2: StatementEntry) -> int:

    # sort by date first
    if se1.date < se2.date:
        return -1
    if se1.date > se2.date:
        return 1

    # then sort by type
    if se1.entry_type != se2.entry_type:
        if se1.entry_type < se2.entry_type:
            return -1
        else:
            return 1

    # sort by week first
    if se1.week_no != se2.week_no:
        if se1.week_no < se2.week_no:
            return -1
        else:
            return 1

    # then by statement order
    if se1.seq_no < se2.seq_no:
        t = -1
    elif se1.seq_no > se2.seq_no:
        t = 1
    else:
        t = 0

    # the statements in the santander current account are ordered
    # newest first, the others have oldest first
    if se1.entry_type == StatementEntryType.SANTANDER_CURRENT_ACCOUNT:
        return -t
    else:
        return t


# -----------------------------------------------------
# read data from file
def read_file(file_name: str) -> bool:

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
            se = StatementEntry()
            if se.from_csv(ls[n], vers):
                add_statement_entry(se)
            else:
                log_error(f'Error parsing line ({n}) : \'{ls[n]}\'')
                return False

        return True

    except FileNotFoundError:
        log_error(f'Could not find file {file_name}')
        return False
    except RuntimeError as e:
        log_error(repr(e))
        return False


# ------------------------------------------------------
# write to file
def write_file (file_name: str) -> bool:

    try:
       with open(file_name, mode='w', encoding="utf-8") as f:
           f.write("Money Reckoner 1.30\n")
           for se in statement_entries:
               f.write(se.to_csv())
               f.write('\n')

    except FileNotFoundError:
        log_error(f'Could not write to file {file_name}')
        return False
    except RuntimeError as e:
        log_error(repr(e))
        return False


# ------------------------------------------------------
# add entry to entries list in the correct order
def add_statement_entry(se: StatementEntry):
    for n in range(len(statement_entries)):
        if compare_statement_entries(se, statement_entries[n]) < 0:
            statement_entries.insert(n, se)
            return
    statement_entries.append(se)
