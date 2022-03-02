
import Logger as Logger
import Database as Database
import StatementData as StatementData
import datetime as datetime
import locale as locale


def parse_statement(s: str) -> bool:
    # returns true if new entries have been added to the database

    lines = s.split('\n')
    new_data = False

    for line in lines:
        if line.__contains__('09-01-28 43377166 - 123 CURRENT ACCOUNT'):
            new_data = parse_santander_current_account_statement(lines)
            break
        if line.__contains__('xxxx xxxx xxxx 3878 - SANTANDER 1 2 3 CASHBACK CARD'):
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


def parse_santander_current_account_statement(lines: []) -> bool:
    Logger.log_info('parsing santander current account statement')

    data = False
    count = 0
    new_count = 0

    for line in lines:
        if line == 'Date	Description	Money in	Money out	Balance':
            # start parsing data
            data = True
            continue

        if data:
            try:

                # 24/02/2022	**3878	GOOGLE PAY CHIPPENHAM CAFFE NERO CHIPPENHAM		£4.35
                # 0 - date, 1 - description, 2 - credit, 3 - debit, 4 - balance
                ts = line.split('\t')
                ds = ts[0].split('/')

                if len(ds) != 3:
                    # end of data
                    break

                date = datetime.date(int(ds[2]), int(ds[1]), int(ds[0]))
                entry = StatementData.StatementEntry()
                entry.entry_type = StatementData.StatementEntryType.SANTANDER_CURRENT_ACCOUNT
                entry.balance = locale.atof(ts[4].replace('£', '').replace(',', ''))
                entry.date = date
                entry.week_no = calculate_week_no(date)
                entry.description = ts[1]
                entry.included_weekly = is_weekly_included(entry)
                entry.included_monthly = is_monthly_included(entry)

                if len(ts[2]) == 0:
                    entry.amount = -locale.atof(ts[3].replace('£', '').replace(',', ''))
                else:
                    entry.amount = locale.atof(ts[2].replace('£', '').replace(',', ''))

                count += 1
                entry.seq_no = Database.next_seq_no()

                if Database.add_statement_entry(Database.statement_entries, entry):
                    # previously unseen entry
                    new_count += 1
                    entry.is_new = True

            except ValueError as ex:
                Logger.log_error('error parsing line \'{line}\': {repr(ex)}')
                break

    Logger.log_info(f'Parsed Santander current account, {new_count} of {count} entries are new')
    return new_count > 0


def parse_santander_credit_card_statement(lines: []) -> bool:
    Logger.log_info('parsing santander credit card statement')

    data = False
    count = 0
    new_count = 0

    for line in lines:
        if line == 'Date	Card no.	Description	Money in	Money out':
            # start parsing data
            data = True
            continue

        if data:
            try:
                # 24/02/2022	**3878	GOOGLE PAY CHIPPENHAM CAFFE NERO CHIPPENHAM		£4.35
                # 0 - date, 1 - card no, 2 - description, 3 - credit, 4 - debit

                # end of data
                if len(line) < 10:
                    break

                ts = line.split('\t')
                ds = ts[0].split('/')

                if len(ds) != 3:
                    # end of data
                    break

                date = datetime.date(int(ds[2]), int(ds[1]), int(ds[0]))
                entry = StatementData.StatementEntry()
                entry.entry_type = StatementData.StatementEntryType.SANTANDER_CREDIT_CARD
                entry.date = date
                entry.week_no = calculate_week_no(date)
                entry.description = ts[2]
                entry.included_weekly = is_weekly_included(entry)
                entry.included_monthly = is_monthly_included(entry)

                if len(ts[3]) == 0:
                    entry.amount = -locale.atof(ts[4].replace('£', '').replace(',', ''))
                else:
                    entry.amount = locale.atof(ts[3].replace('£', '').replace(',', ''))

                count += 1
                entry.seq_no = Database.next_seq_no()

                if Database.add_statement_entry(Database.statement_entries, entry):
                    # previously unseen entry
                    new_count += 1
                    entry.is_new = True

            except ValueError as ex:
                Logger.log_error('error parsing line \'{line}\': {repr(ex)}')
                break

    Logger.log_info(f'Parsed Santander credit card statement, {new_count} of {count} entries are new')
    return new_count > 0


def parse_cash_plus_statement(lines: []) -> bool:
    Logger.log_info('parsing cashplus')
    return True


def calculate_week_no(date: datetime.date) -> int:
    # mon 5th Jan 2015 is week 0
    return int((date.toordinal() - datetime.date(2015, 1, 5).toordinal()) / 7)


def is_weekly_included(entry: StatementData.StatementEntry) -> bool:
    return not entry.description.__contains__("LEEDS BUILDING SOC") and \
           not entry.description.__contains__("CASHPLUS") and \
           not entry.description.__contains__("EDF ENERGY") and \
           not entry.description.__contains__("WILTSHIRE COUNCIL") and \
           not entry.description.__contains__("BT GROUP PLC") and \
           not entry.description.__contains__("CAMELOT LOTTERY") and \
           not entry.description.__contains__("BRISTOLWESSEXWATER") and \
           not entry.description.__contains__("SANTANDERCARDS") and \
           not entry.description.__contains__("WINDOW PAYNE") and \
           not entry.description.__contains__("INITIAL BALANCE") and \
           entry.amount < 0


def is_monthly_included(entry: StatementData.StatementEntry) -> bool:
    return entry.amount < 0 and entry.entry_type == StatementData.StatementEntryType.SANTANDER_CURRENT_ACCOUNT
