
# -- 28/2/22


import csv as csv
from enum import Enum
import locale as locale
import Logger as Logger
import datetime as datetime
import copy as copy

# forward ref
class StatementEntry:
    pass


# the database of statement data
statement_entries: list = []
weekly_summaries: list = []
monthly_summaries: list = []


class StatementEntryType(Enum):
    NONE = 0
    SANTANDER_CREDIT_CARD = 1
    SANTANDER_CURRENT_ACCOUNT = 2
    CASH_PLUS = 3

    def __str__(self):
        if self == StatementEntryType.NONE:
            return "None"
        elif self == StatementEntryType.SANTANDER_CREDIT_CARD:
            return "Santander Credit Card"
        elif self == StatementEntryType.SANTANDER_CURRENT_ACCOUNT:
            return "Santander Current Account"
        elif self == StatementEntryType.CASH_PLUS:
            return "Cashplus"
        else:
            return "?"

    def __lt__(self, other):
        return self.value < other.value

    def from_str(self, text: str):
        if text.lower() == "Santander Credit Card".lower():
            return StatementEntryType.SANTANDER_CREDIT_CARD
        elif text.lower() == "Santander Current Account".lower():
            return StatementEntryType.SANTANDER_CURRENT_ACCOUNT
        elif text.lower() == "Cashplus".lower():
            return StatementEntryType.CASH_PLUS
        else:
            return StatementEntryType.NONE


# -----------------------------------------------------------------------
# Weekly/Monthly Summary
class StatementSummary:

    def __init__(self,
                 summary_id: str = "",
                 summary_date: datetime.date = datetime.date(2000, 1, 1),
                 total: float = 0.0,
                 transactions: int = 0) -> None:
        self._summary_id = summary_id
        self._summary_date = summary_date
        self._total = total
        self._transactions = transactions
        self._entries = []

    # -----------------------------------------------------------------------
    # summary id accessors
    @property
    def summary_id(self):
        return self._summary_id

    @summary_id.setter
    def summary_id(self, value) -> None:
        self._summary_id = value

    # -----------------------------------------------------------------------
    # date accessors
    @property
    def summary_date(self):
        return self._summary_date

    @property
    def summary_date_str(self) -> str:
        dow = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return '{:02d}/{:02d}/{:02d} {}'.format(self._summary_date.day,  self._summary_date.month,
                                                self._summary_date.year, dow[self._summary_date.weekday()])

    @summary_date.setter
    def summary_date(self, value) -> None:
        self._summary_date = value

    # -----------------------------------------------------------------------
    # total accessors
    @property
    def total(self):
        return self._total

    @property
    def total_str(self) -> str:
        if self._total < 0:
            return '-£{:,.2f}'.format(-self._total)
        else:
            return '£{:,.2f}'.format(self._total)

    @total.setter
    def total(self, value) -> None:
        self._total = value

    # -----------------------------------------------------------------------
    # transactions accessors
    @property
    def transactions(self):
        return self._transactions

    @property
    def transactions_str(self) -> str:
        return '{}'.format(self._transactions)

    @transactions.setter
    def transactions(self, value) -> None:
        self._transactions = value

    # -----------------------------------------------------------------------
    # entries accessors
    @property
    def entries(self):
        return self._entries

    @entries.setter
    def entries(self, value) -> None:
        self._entries = value

    def add_entry(self, entry: StatementEntry) -> None:
        add_statement_entry(self._entries, entry)


# -----------------------------------------------------------------------
# Statement entry taken from a line in a bank statement,
# includes an amount the current account balance, type of account etc.
class StatementEntry:

    def __init__(self,
                 entry_type: StatementEntryType = StatementEntryType.NONE,
                 amount: float = 0.0,
                 balance: float = 0.0,
                 a_date: datetime.date = datetime.date(2000, 1, 1),
                 week_no: int = 0,
                 seq_no: int = 0,
                 included_weekly: bool = False,
                 included_monthly: bool = False,
                 description: str = "") -> None:
        self._entry_type = entry_type
        self._amount = amount
        self._balance = balance
        self._date = a_date
        self._week_no = week_no
        # the order it appears in the original bank statement
        self._seq_no = seq_no
        self._included_weekly = included_weekly
        self._included_monthly = included_monthly
        self._description = description

    # -----------------------------------------------------------------------
    def __str__(self) -> str:
        return '{}, {}, {}, {}, {}, {}, {}'.format(
            str(self._entry_type) ,
            self.amount_str,
            self.balance_str,
            self.date_str,
            self.week_no_str,
            self.seq_no_str,
            self._description)

    # -----------------------------------------------------------------------
    def __eq__(self, other) -> bool:
        return self.date == other.date and \
                self.entry_type == other.entry_type and \
                self.seq_no == other.seq_no

    # -----------------------------------------------------------------------
    # entry type accessors
    @property
    def entry_type(self):
        return self._entry_type

    @property
    def entry_type_str(self) -> str:
        return str(self._entry_type)

    @entry_type.setter
    def entry_type(self, value) -> None:
        self._entry_type = value

    # -----------------------------------------------------------------------
    # amount accessors
    @property
    def amount(self):
        return self._amount

    @property
    def amount_str(self) -> str:
        if self._amount < 0:
            return '-£{:,.2f}'.format(-self._amount)
        else:
            return '£{:,.2f}'.format(self._amount)

    @amount.setter
    def amount(self, value) -> None:
        self._amount = value

    # -----------------------------------------------------------------------
    # balance accessors
    @property
    def balance(self):
        return self._balance

    @property
    def balance_str(self) -> str:
        if self._balance < 0:
            return '-£{:,.2f}'.format(-self._balance)
        else:
            return '£{:,.2f}'.format(self._balance)

    @balance.setter
    def balance(self, value) -> None:
        self._balance = value

    # -----------------------------------------------------------------------
    # date accessors
    @property
    def date(self):
        return self._date

    @property
    def date_str(self) -> str:
        dow = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return '{:02d}/{:02d}/{:02d} {}'.format(self._date.day,  self._date.month, self._date.year,
                                                dow[self._date.weekday()])

    @date.setter
    def date(self, value) -> None:
        self._date = value

    # -----------------------------------------------------------------------
    # week no accessors
    @property
    def week_no(self):
        return self._week_no

    @property
    def week_no_str(self) -> str:
        return '{}'.format(self._week_no)

    @week_no.setter
    def week_no(self, value) -> None:
        self._week_no = value

    # -----------------------------------------------------------------------
    # seq no accessors
    @property
    def seq_no(self):
        return self._seq_no

    @property
    def seq_no_str(self) -> str:
        return '{}'.format(self._seq_no)

    @seq_no.setter
    def seq_no(self, value) -> None:
        self._seq_no = value

    # -----------------------------------------------------------------------
    # included weekly accessors
    @property
    def included_weekly(self) -> bool:
        return self._included_weekly

    @property
    def included_weekly_str(self) -> str:
        if self._included_weekly:
            return "*"
        else:
            return ""

    @included_weekly.setter
    def included_weekly(self, value) -> None:
        self._included_weekly = value

    # -----------------------------------------------------------------------
    # included monthly accessors
    @property
    def included_monthly(self) -> bool:
        return self._included_monthly

    @property
    def included_monthly_str(self) -> str:
        if self._included_monthly:
            return "*"
        else:
            return ""

    @included_monthly.setter
    def included_monthly(self, value) -> None:
        self._included_monthly = value

    # -----------------------------------------------------------------------
    # description accessors
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value) -> None:
        self._description = value

    # -----------------------------------------------------------------------
    # create a line of csv, comma separated with double quotes around each field
    # as the current fields have comma delimiters
    def to_csv(self) -> str:
        return '\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\"'.format(
            str(self._entry_type),
            self.amount_str,
            self.balance_str,
            self.date_str,
            self.week_no_str,
            self.seq_no_str,
            self.included_weekly_str,
            self.included_monthly_str,
            self._description)

    # -----------------------------------------------------------------------
    # read from a line of csv
    #
    # v1.10 - c# spend reckoner file, comma separator, currency has no comma delimiters or currency symbol
    #           description the final field has commas so appears as more than one field
    #
    # v1.20 - this python version, comma separated with double quotes around each field,
    #           currency has currency symbol and thousand delimiters
    #
    def from_csv(self, csvstr: str, ver: float) -> bool:
        if ver == 1.1:
            return self.from_csv_v1_10(csvstr)
        elif ver == 1.2 or ver == 1.3:
            return self.from_csv_v1_20(csvstr)

    # -----------------------------------------------------------------------
    # parse data from CSV string taken from file V1.10
    def from_csv_v1_10(self, csvstr: str) -> bool:

        try:

            # Santander Current Account, -£1.10, £48481.19, 10/8/2021 Tue, 344, 240, *, *, CARD PAYMENT TO MIPERMIT
            ts = csvstr.split(',', 6)

            # type
            self._entry_type = StatementEntryType.NONE.from_str(ts[0].strip())
            # amount
            self._amount = locale.atof(ts[1].replace('£', '').replace(',', ''))

            # balance
            self._balance = locale.atof(ts[2].replace('£', '').replace(',', ''))

            # date
            ds = ts[3].strip().split(' ')[1].split('/')
            self._date = datetime.date(int(ds[2]), int(ds[1]), int(ds[0]))

            # week no
            self._week_no = int(ts[4])

            # id
            self._seq_no = int(ts[5])

            # description
            self._description = ts[6].strip()

            return True

        except ValueError as e:
            Logger.log_error(repr(e))
            return False

    # -----------------------------------------------------------------------
    # parse data from CSV string taken from file V1.20 and V1.30
    def from_csv_v1_20(self, csv_str: str) -> bool:

        try:

            # tokenise csv line
            reader = csv.reader([csv_str], delimiter=',')
            ts = next(reader)

            # type
            self._entry_type = StatementEntryType.NONE.from_str(ts[0].strip())

            # amount
            self._amount = locale.atof(ts[1].replace('£', '').replace(',', '').strip())

            # balance
            s = ts[2].replace('£', '').replace(',', '').strip()
            if len(s) > 0:
                self._balance = locale.atof(s)
            else:
                self._balance = 0

            # date
            ds = ts[3].strip().split(' ')[0].split('/')
            self._date = datetime.date(int(ds[2]), int(ds[1]), int(ds[0]))

            # week no
            self._week_no = int(ts[4])

            # id
            self._seq_no = int(ts[5])

            # included weekly
            self._included_weekly = bool(ts[6].strip() == "*")

            # included weekly
            self._included_monthly = bool(ts[7].strip() == "*")

            # description
            self._description = ts[8].strip()

            return True

        except ValueError as e:
            Logger.log_error(repr(e))
            return False


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


# ------------------------------------------------------
# add entry to entries list in the correct order
def add_statement_entry(entries: [], se: StatementEntry):
    for n in range(len(entries)):
        r = compare_statement_entries(se, entries[n])
        if r == -1:
            entries.insert(n, se)
            return
        elif r == 0:
            # ignore matching entries
            return
    entries.append(se)


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
                global statement_entries
                add_statement_entry(statement_entries, se)
            else:
                Logger.log_error(f'Error parsing line ({n}) : \'{ls[n]}\'')
                return False

        Logger.log_info(f'Read {len(statement_entries)} entries from file \'{file_name}\'')
        return True

    except FileNotFoundError:
        Logger.log_error(f'Could not find file {file_name}')
        return False
    except RuntimeError as e:
        Logger.log_error(repr(e))
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
        Logger.log_error(f'Could not write to file {file_name}')
        return False
    except RuntimeError as e:
        Logger.log_error(repr(e))
        return False


# ------------------------------------------------------
def generate_weekly_summaries() -> None:
    global weekly_summaries
    weekly_summaries = []
    week_no = 0
    summary = StatementSummary()

    for se in statement_entries:
        if week_no != se.week_no:

            # new week
            week_no = se.week_no

            # add previous summary to summaries list
            if len(summary.entries) > 0:
                weekly_summaries.append(summary)

            # start summary for the new week
            summary = StatementSummary()
            summary.summary_id = f'{week_no}'

            # set summary date to the start of the week
            summary.summary_date = copy.copy(se.date) - datetime.timedelta(days=se.date.weekday())

        # accumulate summary data
        if se.included_weekly:
            summary.total -= se.amount
        summary.transactions += 1
        summary.add_entry(se)

    # add final summary to summaries list
    if len(summary.entries) > 0:
        weekly_summaries.append(summary)


# ------------------------------------------------------
def generate_monthly_summaries() -> None:
    global monthly_summaries
    monthly_summaries = []
    month = ''
    summary = StatementSummary()

    for se in statement_entries:
        ms = f'{se.date.month}\\{se.date.year}'
        if month != ms:

            # new month
            month = ms

            # add previous summary to summaries list
            if len(summary.entries) > 0:
                monthly_summaries.append(summary)

            # start summary for the new month
            summary = StatementSummary()
            summary.summary_id = ms

            # set summary date to the start of the week
            summary.summary_date = datetime.date(se.date.year, se.date.month, 1)

        # accumulate summary data
        if se.included_monthly:
            summary.total -= se.amount
        summary.transactions += 1
        summary.add_entry(se)

    # add final summary to summaries list
    if len(summary.entries) > 0:
        monthly_summaries.append(summary)




