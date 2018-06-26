import re
import random

from errors import InvalidSyntaxException,  \
                   OutOfRangeException,     \
                   TooManyComponentsException


class Dice:
    SYNTAX = re.compile(r'[+-]?(\d+)d(\d+)')

    MAX_DICE = 100
    MAX_SIDES = 1000

    def __init__(self, qty, die, negative=False):
        self.qty = qty
        self.die = die
        self.negative = negative

    @classmethod
    def from_str(cls, roll_str):
        if roll_str.startswith('+') or roll_str.startswith('-'):
            sign = roll_str[0]
            roll_str = roll_str[1:]
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
        return DiceResult(self.qty, self.die, results, self.negative)

    def __str__(self):
        sign = '-' if self.negative else ''
        return f'{sign}{self.qty}d{self.die}'


class DiceResult:
    def __init__(self, qty, die, results, negative):
        self.qty = qty
        self.die = die
        self.negative = negative
        self.results = results

    def __str__(self):
        sep = ' | ' if self.results else ''
        ind_results = ', '.join(map(lambda x: str(x), self.results))
        return f'{self.qty}d{self.die}: {sum(self.results)}{sep}{ind_results}'


class Roll:
    NORMAL = 0
    ADVANTAGE = 1
    DISADVANTAGE = 2

    SYNTAX = re.compile(r'(\d+d\d+|\d+)([+-](\d+d\d+|\d+))*')

    MAX_COMPONENTS = 25
    MAX_MODIFIER = 1000

    def __init__(self, rolls, modifiers, advantage, quantity):
        self.rolls = rolls
        self.modifiers = modifiers
        self.advantage = advantage
        self.quantity = quantity

    @classmethod
    def from_args(cls, roll_str, advantage):
        if cls.SYNTAX.fullmatch(roll_str):
            components = re.sub(r'([+-])', r' \g<1>', '+' + roll_str).split()
            rolls = []
            modifiers = []

            if len(components) > cls.MAX_COMPONENTS:
                raise TooManyComponentsException(
                    'Rolls may only have up to 25 components.')

            for comp in components:
                match = Dice.SYNTAX.match(comp)
                if match:
                    rolls.append(Dice.from_str(comp))
                else:
                    num = int(comp)
                    if num < 1 or num > cls.MAX_MODIFIER:
                        raise OutOfRangeException(
                            'Modifiers must be between 1 and '
                            f'{cls.MAX_MODIFIER}.')
                    else:
                        modifiers.append(int(comp))

            if len(rolls) == 0:
                raise InvalidSyntaxException()

            return cls(rolls, modifiers, advantage)
        else:
            raise InvalidSyntaxException()

    def roll(self):
        results = []
        for roll in self.rolls:
            results.append(roll.roll())

        if self.advantage is not self.NORMAL:
            other_results = []
            for roll in self.rolls:
                results.append(roll.roll())

            greater = max(results, other_results)
            lesser = min(results, other_results)

            if self.advantage is self.ADVANTAGE:
                return RollResult(greater, self.modifiers, lesser)
            if self.advantage is self.DISADVANTAGE:
                return RollResult(lesser, self.modifiers, greater)
        else:
            return RollResult(results, self.modifiers, None)


class RollResult:
    def __init__(self, rolls, modifiers, losing):
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

        self.losing = losing

    def __str__(self):
        if len(self.rolls) == 1 and len(self.modifiers) == 0:
            return str(self.rolls[0])

        total = f'Total: {self.total}\n'
        roll_total = '\n'.join(str(r) for r in self.rolls) + '\n'
        if len(self.modifiers) == 0:
            return total + roll_total

        if len(self.modifiers) == 1:
            mod_total = f'Modifier: {self.mod_total}\n'
        else:
            modifiers = ', '.join(str(m) for m in self.modifiers)
            mod_total = f'Modifiers: {self.mod_total} | {modifiers}\n'

        if self.losing is None:
            return total + roll_total + mod_total
        else:
            return total + roll_total + mod_total + f'Other roll: {self.losing}'


class RollCommand:
    def __init__(self, rolls):
        self.rolls = rolls
    
    @staticmethod
    def from_args(args):
        parts = []

        base_part = {
            'roll': None,
            'adv': False,
            'dis': False,
            'qty': 1
        }

        for arg in args:
            if arg[0].isdigit():
                cur_part = base_part.copy()
                parts.append(cur_part)
                cur_part['roll'] = Roll.from_str(arg)
            else:
                if cur_part['roll'] is None:
                    raise InvalidSyntaxException()

                if 'advantage'.startswith(arg):
                    cur_part['adv'] = True
                elif 'disadvantage'.startswith(arg):
                    cur_part['dis'] = True
                elif arg.startswith('x') and arg[1:].isdigit():
                    cur_part['qty'] = int(arg[1:])
                else:
                    raise InvalidSyntaxException()

        result_str = ''
        for part in parts:
            for i in range(part['qty']):
                if len(result_str) > 0:
                    result_str += '\n\n'

                r1, r2 = part['roll'].roll(), part['roll'].roll()

                if part['adv']:
                    if r1.total >= r2.total:
                        result_str += str(r1)
                        result_str += '\nOther roll: {0}'.format(r2.total)
                    else:
                        result_str += str(r2)
                        result_str += '\nOther roll: {0}'.format(r1.total)
                elif part['dis']:
                    if r1.total <= r2.total:
                        result_str += str(r1)
                        result_str += '\nOther roll: {0}'.format(r2.total)
                    else:
                        result_str += str(r2)
                        result_str += '\nOther roll: {0}'.format(r1.total)
                else:
                    result_str += str(r1)

        return result_str


class RollCommandResult:
    def __init__(self):
        pass
