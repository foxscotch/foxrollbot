import re
import random


class DiceRoll:
    syntax_regex = re.compile('[+-]?(\d+)d(\d+)')

    def __init__(self, qty, die, negative=False):
        self.qty = qty
        self.die = die
        self.negative = negative

    @staticmethod
    def from_str(roll_str):
        if roll_str.startswith('+') or roll_str.startswith('-'):
            sign, roll_str = roll_str[0], roll_str[1:]
        else:
            sign = '+'

        match = DiceRoll.syntax_regex.fullmatch(roll_str)

        if match:
            try:
                qty = int(match.group(1))
                die = int(match.group(2))

                if qty < 1 or qty > 100:
                    raise OutOfRangeException('Number of dice must be between 1 and 100.')
                if die < 1 or die > 1000:
                    raise OutOfRangeException('Number of sides must be between 1 and 1000.')

                return DiceRoll(qty, die, sign == '-')
            except ValueError as e:
                # I can't imagine this will ever happen, because the regex
                # should prevent any non-numbers. But, you know, just in case.
                raise NotANumberException('Both the number of dice and number of sides must be numbers.')
        else:
            raise InvalidSyntaxException()

    def roll(self):
        results = []
        for i in range(self.qty):
            results.append(random.randint(1, self.die))
        return RollResult(self.qty, self.die, results, self.negative)

    def __str__(self):
        return '{0}d{1}'.format(self.qty, self.die)


class RollResult:
    def __init__(self, qty, die, results, negative):
        self.qty = qty
        self.die = die
        self.results = results
        self.negative = negative

    def __str__(self):
        if len(self.results) == 1:
            return '{0}d{1}: {2}'.format(self.qty, self.die, sum(self.results))
        else:
            return '{0}d{1}: {2} | {3}'.format(self.qty, self.die, sum(self.results), ', '.join(map(lambda x: str(x), self.results)))


class CompleteRoll:
    syntax_regex = re.compile('(\d+d\d+|\d+)([+-](\d+d\d+|\d+))*')

    def __init__(self, rolls, modifiers):
        self.rolls = rolls
        self.modifiers = modifiers

    @staticmethod
    def from_str(roll_str):
        if CompleteRoll.syntax_regex.fullmatch(roll_str):
            parts = re.split('[+-](?=[+-])', re.sub('([+-])', '\g<1>\g<1>', roll_str))
            rolls = []
            modifiers = []

            if len(parts) > 25:
                raise TooManyPartsException('A roll may only have up to 25 parts.')

            for part in parts:
                match = DiceRoll.syntax_regex.match(part)
                if match:
                    rolls.append(DiceRoll.from_str(part))
                else:
                    num = int(part)
                    if num > 1000:
                        raise OutOfRangeException('Modifiers must be between 1 and 1000.')
                    else:
                        modifiers.append(int(part))

            if len(rolls) == 0:
                raise InvalidSyntaxException()

            return CompleteRoll(rolls, modifiers)
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
        self.roll_total = sum([-sum(roll.results) if roll.negative else sum(roll.results) for roll in rolls])
        self.modifiers = modifiers
        self.mod_total = sum(modifiers)
        self.total = self.roll_total + self.mod_total

    def __str__(self):
        total = 'Total: {0}\n'.format(self.total)
        roll_results = '\n'.join(map(lambda x: str(x), self.rolls)) + '\n'

        if len(self.modifiers) == 1:
            mod_total = 'Modifier: {0}'.format(self.mod_total)
        else:
            mod_total = 'Modifiers: {0} | {1}'.format(self.mod_total, ', '.join(map(lambda x: str(x), self.modifiers)))

        if len(self.rolls) == 1 and len(self.modifiers) == 0:
            return str(self.rolls[0])
        elif len(self.modifiers) == 0:
            return total + roll_results
        else:
            return total + roll_results + mod_total
