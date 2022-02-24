
from StatementEntry import *
from Logger import *

global statement_entries
statement_entries = []

def read_file(file_name: str) -> bool:

    try:
        with open(file_name) as f:
            ls = f.readlines()

        l1 = ls[0][:-1]
        l2 = ls[1]
        l3 = ls[2]

        if ls[0][:-1] == "Money Reckoner 1.10":
            vers: float = 1.1
        elif ls[0][:-1] == "Money Reckoner 1.20":
            vers: float = 1.2
        else:
            raise RuntimeError(f'Invalid header \'{ls[0]}\' in file \'{file_name}\'')

        for l in ls[1:]:
            se = StatementEntry()
            se.from_csv(l, vers)
            statement_entries.append(se)

        return True

    except FileNotFoundError:
        log_error(f'Could not find file {file_name}')
        return False
    except RuntimeError as e:
        log_error(repr(e))
        return False

