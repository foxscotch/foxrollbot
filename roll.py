import re
import random

from errors import InvalidSyntaxException,  \
                   OutOfRangeException,     \
                   TooManyPartsException


class DiceRoll:
    MAX_DICE = 100
    MAX_SIDES = 1000
    SYNTAX = re.compile(r'[+-]?(\d+)d(\d+)')

    def __init__(self, qty, die, negative=False):
        self.qty = qty
        self.die = die
        self.negative = negative

    @classmethod
    def from_str(cls, roll_str):
        if roll_str.startswith('+') or roll_str.startswith('-'):
            sign, roll_str = roll_str[0], roll_str[1:]
        else:
            sign = '+'

        match = cls.SYNTAX.fullmatch(roll_str)

        if match:
            qty = int(match.group(1))
            die = int(match.group(2))

            if qty < 1 or qty > cls.MAX_DICE:
                raise OutOfRangeException(
                    f'Number of dice must be between 1 and {cls.MAX_DICE}.')
            if die < 2 or die > cls.MAX_SIDES:
                raise OutOfRangeException(
                    f'Number of sides must be between 2 and {cls.MAX_SIDES}.')

            return cls(qty, die, sign == '-')
        else:
            raise InvalidSyntaxException()

    def roll(self):
        results = []
        for i in range(self.qty):
            results.append(random.randint(1, self.die))
        return RollResult(self.qty, self.die, results, self.negative)

    def __str__(self):
        sign = '-' if self.negative else ''
        return f'{sign}{self.qty}d{self.die}'


class RollResult:
    def __init__(self, qty, die, results, negative):
        self.qty = qty
        self.die = die
        self.negative = negative
        self.results = results

    def __str__(self):
        sep = ' | ' if self.results else ''
        ind_results = ', '.join(map(lambda x: str(x), self.results))
        return f'{self.qty}d{self.die}: {sum(self.results)}{sep}{ind_results}'


class CompleteRoll:
    SYNTAX = re.compile(r'(\d+d\d+|\d+)([+-](\d+d\d+|\d+))*')

    def __init__(self, rolls, modifiers):
        self.rolls = rolls
        self.modifiers = modifiers

    @classmethod
    def from_str(cls, roll_str):
        if cls.SYNTAX.fullmatch(roll_str):
            substituted = re.sub(r'([+-])', r'\g<1>\g<1>', roll_str)
            parts = re.split(r'[+-](?=[+-])', substituted)
            rolls = []
            modifiers = []

            if len(parts) > 25:
                raise TooManyPartsException(
                    'A roll may only have up to 25 parts.')

            for part in parts:
                match = DiceRoll.SYNTAX.match(part)
                if match:
                    rolls.append(DiceRoll.from_str(part))
                else:
                    num = int(part)
                    if num > 1000:
                        raise OutOfRangeException(
                            'Modifiers must be between 1 and 1000.')
                    else:
                        modifiers.append(int(part))

            if len(rolls) == 0:
                raise InvalidSyntaxException()

            return cls(rolls, modifiers)
        else:
            raise InvalidSyntaxException()

    def roll(self):
        results = []
        for roll in self.rolls:
            results.append(roll.roll())
        return CompleteRollResult(results, self.modifiers)


class CompleteRollResult:
    def __init__(self, rolls, modifiers):
        self.rolls = rolls

        self.roll_total = 0
        for roll in self.rolls:
            subtotal = sum(roll.results)
            if not roll.negative:
                self.roll_total += subtotal
            else:
                self.roll_total -= subtotal

        self.modifiers = modifiers
        self.mod_total = sum(self.modifiers)
        self.total = self.roll_total + self.mod_total

    def __str__(self):
        total = f'Total: {self.total}\n'
        roll_results = '\n'.join(str(r) for r in self.rolls) + '\n'

        if len(self.modifiers) == 1:
            mod_total = 'Modifier: {0}'.format(self.mod_total)
        else:
            modifiers = ', '.join(str(m) for m in self.modifiers)
            mod_total = f'Modifiers: {self.mod_total} | {modifiers}'

        if len(self.rolls) == 1 and len(self.modifiers) == 0:
            return str(self.rolls[0])
        elif len(self.modifiers) == 0:
            return total + roll_results
        else:
            return total + roll_results + mod_total
