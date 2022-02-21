

import csv
from datetime import date
from enum import Enum
import locale

class StatementEntryType(Enum):
    NONE = 0
    SANTANDER_CREDIT_CARD = 1
    SANTANDER_CURRENT_ACCOUNT = 2
    CASHPLUS = 3

    def __str__(self):
        if self == StatementEntryType.NONE:
            return "None"
        elif self == StatementEntryType.SANTANDER_CREDIT_CARD:
            return "Santander Credit Card"
        elif self == StatementEntryType.SANTANDER_CURRENT_ACCOUNT:
            return "Santander Current Account"
        elif self == StatementEntryType.CASHPLUS:
            return "Cashplus"
        else:
            return "?"

    def from_str(self, text: str):
        if text.lower() == "Santander Credit Card".lower():
            return StatementEntryType.SANTANDER_CREDIT_CARD
        elif text.lower() == "Santander Current Account".lower():
            return StatementEntryType.SANTANDER_CURRENT_ACCOUNT
        elif text.lower() == "Cashplus".lower():
            return StatementEntryType.CASHPLUS
        else:
            return StatementEntryType.NONE

# -----------------------------------------------------------------------
# Statement entry taken from a line in a bank statement,
# includes an amount the current account balance, type of account etc.
class StatementEntry:

    def __init__(self,  \
                 entry_type: StatementEntryType = StatementEntryType.NONE,    \
                 amount: float = 0.0,               \
                 balance: float = 0.0,              \
                 a_date: date = date(2000, 1, 1),   \
                 week_no: int = 0,                  \
                 seq_no: int = 0,                   \
                 included_weekly: bool = False,             \
                 included_monthly: bool = False,            \
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
        return '{}, {}, {}, {}, {}, {}, {}'.format( \
            str(self._entry_type) ,     \
            self.amount_str,            \
            self.balance_str,           \
            self.date_str,              \
            self.week_no_str,           \
            self.seq_no_str,            \
            self._description)

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
        return '{:02d}\\{:02d}\\{:02d}'.format( self._date.day,  self._date.month, self._date.year)

    @date.setter
    def x(self, value) -> None:
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
    def included_weekly(self):
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
    # included weekly accessors
    @property
    def included_monthly(self):
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
    # create a line of csv, comma separated with double quotes around each field
    # as the current fields have comma delimiters
    def to_csv(self) -> str:
        return '\"{}\",\"{}\",\"{},\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"{}\"'.format( \
            str(self._entry_type), \
            self.amount_str, \
            self.balance_str, \
            self.date_str, \
            self.week_no_str, \
            self.seq_no_str, \
            self.included_weekly_str, \
            self.included_monthly_str, \
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
    def from_csv(self, csvstr: str, ver: int) -> None:
        if ver == 1.1:
            return self.from_csv_v1_10(csvstr)
        elif ver == 1.2:
            return self.from_csv_v1_20(csvstr)

    # -----------------------------------------------------------------------
    # parse data from CSV string taken from file V1.10
    def from_csv_v1_10(self, csvstr: str) -> None:

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
        self._date = date(int(ds[2]), int(ds[1]), int(ds[0]))

        # week no
        self._week_no = int(ts[4])

        # id
        self._seq_no = int(ts[5])

        # description
        self._description = ts[6].strip()

    # -----------------------------------------------------------------------
    # parse data from CSV string taken from file V1.20
    def from_csv_v1_20(self, csvstr: str) -> None:

        # tokenise csv line
        reader = csv.reader([csvstr], delimiter=',')
        ts = next(reader)

        # type
        self._entry_type = StatementEntryType.NONE.from_str(ts[0].strip())
        # amount
        self._amount = locale.atof(ts[1].replace('£', '').replace(',', ''))

        # balance
        self._balance = locale.atof(ts[2].replace('£', '').replace(',', ''))

        # date
        ds = ts[3].split(' ')[1].split('/')
        self._date = date(int(ds[2]), int(ds[1]), int(ds[0]))

        # week no
        self._week_no = int(ts[4])

        # id
        self._seq_no = int(ts[5])

        # included weekly
        self._included_weekly = bool(ts[6].strip() == "*")

        # included weekly
        self._included_monthly = bool(ts[7].strip() == "*")

        # description
        self._description = ts[8]





















