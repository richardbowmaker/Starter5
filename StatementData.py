

import csv as csv
from enum import Enum
import locale as locale
import Logger as Logger
import datetime as datetime


# forward ref
class StatementEntry:
    pass

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

    # def add_entry(self, entry: StatementEntry) -> None:
    #     add_statement_entry(self._entries, entry)


# -----------------------------------------------------------------------
# Statement entry taken from a line in a bank statement,
# includes an amount the current account balance, type of account etc.
class StatementEntry:

    def __init__(self,
                 type: StatementEntryType = StatementEntryType.NONE,
                 amount: float = 0.0,
                 balance: float = 0.0,
                 date: datetime.date = datetime.date(2000, 1, 1),
                 week_no: int = 0,
                 seq_no: int = 0,
                 included_weekly: bool = False,
                 included_monthly: bool = False,
                 description: str = "") -> None:
        self._type = type
        self._amount = amount
        self._balance = balance
        self._date = date
        self._week_no = week_no
        # the order it appears in the original bank statement
        self._seq_no = seq_no
        self._included_weekly = included_weekly
        self._included_monthly = included_monthly
        self._description = description
        self._is_new = False
        self._user_excluded = False
        # position in Database.statement_entries
        self._index = -1

    # -----------------------------------------------------------------------
    def __str__(self) -> str:
        return '{}, {}, {}, {}, {}, {}, {}'.format(
            str(self._type) ,
            self.amount_str,
            self.balance_str,
            self.date_str,
            self.week_no_str,
            self._description,
            self.included_summary,
            self.seq_no_str)

    # -----------------------------------------------------------------------
    def __eq__(self, other) -> bool:
        return self.date == other.date and \
               self.type == other.type and \
               self.seq_no == other.seq_no

    # -----------------------------------------------------------------------
    # entry type accessors
    @property
    def type(self):
        return self._type

    @property
    def type_str(self) -> str:
        return str(self._type)

    @type.setter
    def type(self, value) -> None:
        self._type = value

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
    # user excluded accessors
    @property
    def user_excluded(self) -> bool:
        return self._user_excluded

    @property
    def user_excluded_str(self) -> str:
        if self._user_excluded:
            return "*"
        else:
            return ""

    @user_excluded.setter
    def user_excluded(self, value) -> None:
        self._user_excluded = value

    # -----------------------------------------------------------------------
    # inclusion flags summary
    @property
    def included_summary(self):
        s = ""
        if self._included_weekly:
            s += 'W'
        if self._included_monthly:
            s += 'M'
        if self._user_excluded:
            s += 'X'
        return s

    # -----------------------------------------------------------------------
    # description accessors
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value) -> None:
        self._description = value

    # -----------------------------------------------------------------------
    # is new accessors
    @property
    def is_new(self) -> bool:
        return self._is_new

    @is_new.setter
    def is_new(self, value) -> None:
        self._is_new = value

    # -----------------------------------------------------------------------
    # index accessors
    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value) -> None:
        self._index = value

    # -----------------------------------------------------------------------
    # month str accessors
    @property
    def month_str(self):
        return '{:02d}/{:04d}'.format(self._date.month, self._date.year)

    # -----------------------------------------------------------------------
    # create a line of csv, comma separated with double quotes around each field
    # as the current fields have comma delimiters
    def to_csv(self) -> str:
        return '\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\"'.format(
            str(self._type),
            self.amount_str,
            self.balance_str,
            self.date_str,
            self.week_no_str,
            self.seq_no_str,
            self.included_weekly_str,
            self.included_monthly_str,
            self._description,
            self._user_excluded)

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
        elif ver == 1.2 or ver == 1.3 or ver == 1.4:
            return self.from_csv_v1_20(csvstr)

    # -----------------------------------------------------------------------
    # parse data from CSV string taken from file V1.10
    def from_csv_v1_10(self, csv_str: str) -> bool:

        try:

            # Santander Current Account, -£1.10, £48481.19, 10/8/2021 Tue, 344, 240, *, *, CARD PAYMENT TO MIPERMIT
            ts = csv_str.split(',', 6)

            # type
            self._type = StatementEntryType.NONE.from_str(ts[0].strip())
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
    # parse data from CSV string taken from file V1.20, V1.30 and V1.40
    def from_csv_v1_20(self, csv_str: str) -> bool:

        try:

            # tokenise csv line
            reader = csv.reader([csv_str], delimiter=',')
            ts = next(reader)

            # type
            self._type = StatementEntryType.NONE.from_str(ts[0].strip())

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

            # user excluded
            if len(ts) > 9:
                if ts[9] == 'True':
                    self.user_excluded = True
                else:
                    self._user_excluded = False

            return True

        except ValueError as e:
            Logger.log_error(repr(e))
            return False


def is_equal_statement_entries(se1: StatementEntry, se2: StatementEntry) -> bool:
    return se1.type == se2.type and \
           se1.date == se2.date and \
           se1.amount == se2.amount and \
           se1.balance == se2.balance


def compare_statement_entries(se1: StatementEntry, se2: StatementEntry) -> int:
    # returns -1, 0, 1

    # sort by date first
    if se1.date < se2.date:
        return -1
    if se1.date > se2.date:
        return 1

    # then sort by type
    if se1.type != se2.type:
        if se1.type < se2.type:
            return -1
        else:
            return 1

    # then by statement order
    if se1.seq_no < se2.seq_no:
        return -1
    elif se1.seq_no > se2.seq_no:
        return 1
    else:
        # should never happen
        return 0


