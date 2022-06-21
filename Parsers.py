
import Logger as Logger
import Database as Database
import StatementData as StatementData
import datetime as datetime
import locale as locale
import os
from enum import Enum


def parse_statement(s: str) -> bool:
    # returns true if new entries have been added to the database

    lines = s.split('\n')
    new_data = False

    for line in lines:
        # if line.__contains__('09-01-28 43377166 - 123 CURRENT ACCOUNT'):
        if line.__contains__('1|2|3 Current Account earnings'):
            new_data = parse_santander_current_account_statement(lines)
            break
        # if line.__contains__('xxxx xxxx xxxx 3878 - SANTANDER 1 2 3 CASHBACK CARD'):
        if line.__contains__('1|2|3 Credit Card earnings'):
            new_data = parse_santander_credit_card_statement(lines)
            break
        if line.__contains__('CashPlus Online Banking'):
            new_data = parse_cash_plus_statement(lines)
            break

    if new_data:
        Database.set_dirty()
        return True
    else:
        return False


class ParseState(Enum):
    PRE_PARSE = 0
    PARSING = 1
    POST_PARSE = 2


def parse_santander_current_account_statement(lines: []) -> bool:
    Logger.log_info('parsing santander current account statement')
    Database.clear_parsed_text()
    state = ParseState.PRE_PARSE
    count = 0
    new_count = 0

    for line in lines:

        if state == ParseState.PRE_PARSE:
            Database.add_parsed_line(False, line)

            # 'Date	Description	Money in	Money out	Balance'
            if os.name == 'nt' and line == 'Date\tDescription\tMoney in\tMoney out\tBalance':
                state = ParseState.PARSING
                continue
            if os.name == 'posix' and line == 'Date \tDescription \tMoney in \tMoney out \tBalance':
                state = ParseState.PARSING
                continue

        if state == ParseState.PARSING:
            try:

                # 24/02/2022	**3878	GOOGLE PAY CHIPPENHAM CAFFE NERO CHIPPENHAM		£4.35
                # 0 - date, 1 - description, 2 - credit, 3 - debit, 4 - balance
                ts = line.split('\t')
                ds = ts[0].split('/')

                if len(ds) != 3:
                    # end of data
                    state = ParseState.POST_PARSE
                else:
                    date = datetime.date(int(ds[2]), int(ds[1]), int(ds[0]))
                    entry = StatementData.StatementEntry()
                    entry.type = StatementData.StatementEntryType.SANTANDER_CURRENT_ACCOUNT
                    entry.balance = locale.atof(ts[4].replace('£', '').replace(',', ''))
                    entry.date = date
                    entry.week_no = calculate_week_no(date)
                    entry.description = ts[1]

                    if len(ts[2]) == 0:
                        entry.amount = -locale.atof(ts[3].replace('£', '').replace(',', ''))
                    else:
                        entry.amount = locale.atof(ts[2].replace('£', '').replace(',', ''))

                    entry.included_weekly = is_weekly_included(entry)
                    entry.included_monthly = is_monthly_included(entry)

                    count += 1
                    entry.seq_no = Database.next_seq_no()

                    n = Database.add_statement_entry(Database.statement_entries, entry)
                    if n != -1:
                        # new entry
                        new_count += 1
                        entry.is_new = True
                        entry.lookup = n
                    else:
                        entry.is_new = False
                        entry.lookup = -1

                    Database.add_parsed_line(True, line)

            except ValueError as ex:
                Logger.log_error(f'error parsing line \'{line}\': {repr(ex)}')
                Database.add_parsed_line(False, '**** Error ***')
                state = ParseState.POST_PARSE

        if state == ParseState.POST_PARSE:
            Database.add_parsed_line(False, line)

    Logger.log_info(f'Parsed Santander current account, {new_count} of {count} entries are new')
    return new_count > 0


def parse_santander_credit_card_statement(lines: []) -> bool:
    Logger.log_info('parsing santander credit card statement')
    Database.clear_parsed_text()
    state = ParseState.PRE_PARSE
    count = 0
    new_count = 0

    for line in lines:

        if state == ParseState.PRE_PARSE:
            Database.add_parsed_line(False, line)

            if os.name == 'nt' and line == 'Date\tCard no.\tDescription\tMoney in\tMoney out':
                state = ParseState.PARSING
                continue
            if os.name == 'posix' and line == 'Date \tCard no. \tDescription \tMoney in \tMoney out':
                state = ParseState.PARSING
                continue


        if state == ParseState.PARSING:
            try:
                # 24/02/2022	**3878	GOOGLE PAY CHIPPENHAM CAFFE NERO CHIPPENHAM		£4.35
                # 0 - date, 1 - card no, 2 - description, 3 - credit, 4 - debit

                # end of data
                if len(line) < 10:
                    state = ParseState.POST_PARSE
                else:
                    ts = line.split('\t')
                    ds = ts[0].split('/')

                    if len(ds) != 3:
                        state = ParseState.POST_PARSE
                    else:
                        date = datetime.date(int(ds[2]), int(ds[1]), int(ds[0]))
                        entry = StatementData.StatementEntry()
                        entry.type = StatementData.StatementEntryType.SANTANDER_CREDIT_CARD
                        entry.date = date
                        entry.week_no = calculate_week_no(date)
                        entry.description = ts[2]

                        if len(ts[3]) == 0:
                            entry.amount = -locale.atof(ts[4].replace('£', '').replace(',', ''))
                        else:
                            entry.amount = locale.atof(ts[3].replace('£', '').replace(',', ''))

                        entry.included_weekly = is_weekly_included(entry)
                        entry.included_monthly = is_monthly_included(entry)

                        count += 1
                        entry.seq_no = Database.next_seq_no()

                        n = Database.add_statement_entry(Database.statement_entries, entry)
                        if n != -1:
                            # new entry
                            new_count += 1
                            entry.is_new = True
                            entry.lookup = n
                        else:
                            entry.is_new = False
                            entry.lookup = -1

                        Database.add_parsed_line(True, line)

            except ValueError as ex:
                Logger.log_error(f'error parsing line \'{line}\': {repr(ex)}')
                Database.add_parsed_line(False, '**** Error ***')
                state = ParseState.POST_PARSE

        if state == ParseState.POST_PARSE:
            Database.add_parsed_line(False, line)

    Logger.log_info(f'Parsed Santander credit card statement, {new_count} of {count} entries are new')
    return new_count > 0


def parse_cash_plus_statement(lines: []) -> bool:
    Logger.log_info('parsing cashplus statement')
    Database.clear_parsed_text()
    state = ParseState.PRE_PARSE
    count = 0
    new_count = 0
    ln = 0

    while ln < len(lines):

        if state == ParseState.PRE_PARSE:
            Database.add_parsed_line(False, lines[ln])

            if lines[ln] == 'Balance':
                state = ParseState.PARSING
                ln += 1
                continue

        if state == ParseState.PARSING:
            try:

                # 03/03/2022 5587
                # Auth: MIPERMIT, CHIPPENHAM, GBR
                # £1.10

                # end of data
                if len(lines[ln]) < 10:
                    state = ParseState.POST_PARSE
                else:
                    # parse date
                    ts = lines[ln].split('\t')
                    ds = ts[0].strip().split('/')

                    if len(ds) < 3:
                        state = ParseState.POST_PARSE
                    else:
                        date = datetime.date(int(ds[2]), int(ds[1]), int(ds[0]))

                        entry = StatementData.StatementEntry()
                        entry.type = StatementData.StatementEntryType.CASH_PLUS
                        entry.date = date
                        entry.week_no = calculate_week_no(date)
                        entry.description = lines[ln + 1]

                        # amount
                        ln += 2
                        ts = lines[ln].split('\t')

                        if os.name == 'posix':
                            if len(ts[1]) == 0:
                                # debit
                                entry.amount = -locale.atof(ts[2].replace('£', '').replace(',', ''))
                                # first entry does not include the balance
                                if len(ts[3]) > 0:
                                    entry.balance = locale.atof(ts[3].replace('£', '').replace(',', ''))
                            else:
                                # credit
                                entry.amount = locale.atof(ts[1].replace('£', '').replace(',', ''))
                                if len(ts[3]) > 0:
                                    entry.balance = locale.atof(ts[3].replace('£', '').replace(',', ''))
                        elif os.name == 'nt':
                            if len(ts) == 2:
                                # debit
                                entry.amount = -locale.atof(ts[0].replace('£', '').replace(',', ''))
                                # first entry does not include the balance
                                if len(ts[1]) > 0:
                                    entry.balance = locale.atof(ts[1].replace('£', '').replace(',', ''))
                            else:
                                # credit
                                entry.amount = locale.atof(ts[0].replace('£', '').replace(',', ''))
                                if len(ts[2]) > 0:
                                    entry.balance = locale.atof(ts[2].replace('£', '').replace(',', ''))

                        entry.included_weekly = is_weekly_included(entry)
                        entry.included_monthly = is_monthly_included(entry)

                        count += 1
                        entry.seq_no = Database.next_seq_no()

                        n = Database.add_statement_entry(Database.statement_entries, entry)
                        if n != -1:
                            # new entry
                            new_count += 1
                            entry.is_new = True
                            entry.lookup = n
                        else:
                            entry.is_new = False
                            entry.lookup = -1


                        Database.add_parsed_line(True, lines[ln - 2])
                        Database.add_parsed_line(True, lines[ln - 1])
                        Database.add_parsed_line(True, lines[ln])

            except ValueError as ex:
                Logger.log_error(f'error parsing line \'{lines[ln]}\': {repr(ex)}')
                Database.add_parsed_line(False, '**** Error ***')
                state = ParseState.POST_PARSE

        if state == ParseState.POST_PARSE:
            Database.add_parsed_line(False, lines[ln])

        ln += 1

    Logger.log_info(f'Parsed Cashplus card statement, {new_count} of {count} entries are new')
    return new_count > 0


def calculate_week_no(date: datetime.date) -> int:
    # mon 5th Jan 2015 is week 0
    return int((date.toordinal() - datetime.date(2015, 1, 5).toordinal()) / 7)


def is_weekly_included(entry: StatementData.StatementEntry) -> bool:
    return not entry.description.upper().__contains__("LEEDS BUILDING SOC") and \
           not entry.description.upper().__contains__("CASHPLUS") and \
           not entry.description.upper().__contains__("EDF ENERGY") and \
           not entry.description.upper().__contains__("WILTSHIRE COUNCIL") and \
           not entry.description.upper().__contains__("BT GROUP PLC") and \
           not entry.description.upper().__contains__("CAMELOT LOTTERY") and \
           not entry.description.upper().__contains__("BRISTOLWESSEXWATER") and \
           not entry.description.upper().__contains__("SANTANDERCARDS") and \
           not entry.description.upper().__contains__("WINDOW PAYNE") and \
           not entry.description.upper().__contains__("INITIAL BALANCE") and \
           entry.amount < 0 and \
           entry.amount > -1000


def is_monthly_included(entry: StatementData.StatementEntry) -> bool:
    return entry.amount < 0 and entry.amount > -1000 and entry.type == StatementData.StatementEntryType.SANTANDER_CURRENT_ACCOUNT
