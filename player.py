class Player:
    def __init__(self, balance: float):
        self.balance = balance

    def withdraw(self, amount: float):
        if 0 < amount <= self.balance:
            self.balance -= amount
            return True
        return False

    def deposit(self, amount: float):
        self.balance += amount
