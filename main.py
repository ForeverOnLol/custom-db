class Database:
    def __init__(self):
        self.data = {}
        self.transactions = []

    def set(self, key, value):
        if self.transactions:
            self.transactions[-1][key] = value
        else:
            self.data[key] = value

    def get(self, key):
        if self.transactions:
            for transaction in reversed(self.transactions):
                if key in transaction:
                    return transaction[key] if transaction[key] is not None else 'NULL'
        return self.data.get(key, 'NULL')

    def unset(self, key):
        if self.transactions:
            self.transactions[-1][key] = None
        elif key in self.data:
            del self.data[key]

    def counts(self, value):
        count = 0
        for transaction in self.transactions:
            count += list(transaction.values()).count(value)
        count += list(self.data.values()).count(value)
        return count

    def find(self, value):
        keys = []
        for key, val in self.data.items():
            if val == value:
                keys.append(key)
        for transaction in self.transactions:
            for key, val in transaction.items():
                if val == value and key not in keys:
                    keys.append(key)
                elif val is None and key in keys:
                    keys.remove(key)
        return keys

    def begin(self):
        self.transactions.append({})

    def rollback(self):
        if not self.transactions:
            print("NO TRANSACTION")
        else:
            self.transactions.pop()

    def commit(self):
        if not self.transactions:
            print("NO TRANSACTION")
        else:
            current_transaction = self.transactions.pop()
            if self.transactions:
                for key, value in current_transaction.items():
                    self.transactions[-1][key] = value
            else:
                for key, value in current_transaction.items():
                    if value is None:
                        if key in self.data:
                            del self.data[key]
                    else:
                        self.data[key] = value


class Command:
    def execute(self, db: Database, args):
        pass


def check_args_len(expected_len: int):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if len(args[2]) == expected_len:
                return func(*args, **kwargs)
            else:
                print("WRONG ARGUMENTS")
                return True
        return wrapper
    return decorator


class SetCommand(Command):
    @check_args_len(3)
    def execute(self, db, args):
        db.set(args[1], args[2])
        return True


class GetCommand(Command):
    @check_args_len(2)
    def execute(self, db, args):
        print(db.get(args[1]))
        return True


class UnsetCommand(Command):
    @check_args_len(2)
    def execute(self, db, args):
        db.unset(args[1])
        return True


class CountsCommand(Command):
    @check_args_len(2)
    def execute(self, db, args):
        print(db.counts(args[1]))
        return True


class FindCommand(Command):
    @check_args_len(2)
    def execute(self, db, args):
        print(' '.join(db.find(args[1])))
        return True


class BeginCommand(Command):
    @check_args_len(1)
    def execute(self, db, args):
        db.begin()
        return True


class RollbackCommand(Command):
    @check_args_len(1)
    def execute(self, db, args):
        db.rollback()
        return True


class CommitCommand(Command):
    @check_args_len(1)
    def execute(self, db, args):
        db.commit()
        return True


class EndCommand(Command):
    @check_args_len(1)
    def execute(self, db, args):
        return False


class UnknownCommand(Command):
    def execute(self, db, args):
        print("UNKNOWN COMMAND")
        return True


def main():
    db = Database()
    commands = {
        'SET': SetCommand(),
        'GET': GetCommand(),
        'UNSET': UnsetCommand(),
        'COUNTS': CountsCommand(),
        'FIND': FindCommand(),
        'BEGIN': BeginCommand(),
        'ROLLBACK': RollbackCommand(),
        'COMMIT': CommitCommand(),
        'END': EndCommand()
    }

    while True:
        try:
            cmd_input = input().strip().split()
        except EOFError:
            break

        if not cmd_input:
            continue

        cmd_name = cmd_input[0].upper()
        cmd = commands.get(cmd_name, UnknownCommand())

        if not cmd.execute(db, cmd_input):
            break


if __name__ == '__main__':
    main()
