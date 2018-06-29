import re
import random
from functools import total_ordering

from errors import *


class Dice:
    SYNTAX = re.compile(r'[+-]?(\d+)d(\d+)')

    MAX_DICE = 100
    MAX_SIDES = 1000

    def __init__(self, quantity, die, negative=False):
        if quantity < 1 or quantity > self.MAX_DICE:
            raise OutOfRangeException(
                f'Number of dice must be between 1 and {self.MAX_DICE}.')
        if die < 2 or die > self.MAX_SIDES:
            raise OutOfRangeException(
                f'Number of sides must be between 2 and {self.MAX_SIDES}.')

        self.quantity = quantity
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
            quantity = int(match.group(1))
            die = int(match.group(2))
            return cls(quantity, die, sign == '-')
        else:
            raise InvalidSyntaxException()

    def roll(self):
        results = []
        for i in range(self.quantity):
            results.append(random.randint(1, self.die))
        return DiceResult(self, results, self.negative)

    def __str__(self):
        sign = '-' if self.negative else ''
        return f'{sign}{self.quantity}d{self.die}'


@total_ordering
class DiceResult:
    def __init__(self, dice, results, negative):
        self.dice = dice
        self.negative = negative
        self.results = results

    def __str__(self):
        sep = ' | ' if len(self.results) > 1 else ''
        if len(self.results) > 1:
            ind_results = ', '.join(str(r) for r in self.results)
        else:
            ind_results = ''
        return f'{self.dice}: {sum(self.results)}{sep}{ind_results}'
    
    def __add__(self, other):
        if type(other) == int:
            return sum(self.results) + other
        else:
            return sum(self.results) + sum(other.results)
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __eq__(self, other):
        return sum(self.results) == sum(other.results)
    
    def __lt__(self, other):
        return sum(self.results) < sum(other.results)



class Roll:
    NORMAL = 0
    ADVANTAGE = 1
    DISADVANTAGE = 2

    SYNTAX = re.compile(r'(\d+d\d+|\d+)([+-](\d+d\d+|\d+))*')

    MAX_COMPONENTS = 25
    MAX_MODIFIER = 1000

    def __init__(self, rolls, modifiers, advantage):
        components = len(rolls) + len(modifiers)
        if components < 1 or components > self.MAX_COMPONENTS:
            raise TooManyComponentsException(
                f'Rolls may only have up to {self.MAX_COMPONENTS} components.')

        for modifier in modifiers:
            if modifier < 1 or modifier > self.MAX_MODIFIER:
                raise OutOfRangeException(
                    f'Modifiers must be between 1 and {self.MAX_MODIFIER}.')

        self.rolls = rolls
        self.modifiers = modifiers
        self.advantage = advantage

    @classmethod
    def from_str(cls, roll_str, advantage):
        if cls.SYNTAX.fullmatch(roll_str):
            components = re.sub(r'([+-])', r' \g<1>', '+' + roll_str).split()
            rolls = []
            modifiers = []

            for comp in components:
                match = Dice.SYNTAX.match(comp)
                if match:
                    rolls.append(Dice.from_str(comp))
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
                other_results.append(roll.roll())

            greater = max(results, other_results)
            lesser = min(results, other_results)

            if self.advantage is self.ADVANTAGE:
                return RollResult(greater, self.modifiers, sum(lesser))
            if self.advantage is self.DISADVANTAGE:
                return RollResult(lesser, self.modifiers, sum(greater))
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
        output = ''

        roll_count = len(self.rolls)
        mod_count = len(self.modifiers)
        if roll_count == 1 and mod_count == 0 and self.losing is None:
            return str(self.rolls[0])

        total = f'Total: {self.total}\n' if roll_count > 1 else ''
        roll = '\n'.join(str(r) for r in self.rolls)

        if len(self.modifiers) == 0:
            output += total + roll
        elif len(self.modifiers) == 1:
            output += f'\nModifier: {self.mod_total}'
        else:
            modifiers = ', '.join(str(m) for m in self.modifiers)
            output += f'\nModifiers: {self.mod_total} | {modifiers}'

        if self.losing is None:
            return output
        else:
            return output + f'\nOther roll: {self.losing}'


class RollCommand:
    def __init__(self, rolls):
        self.rolls = rolls
    
    @staticmethod
    def from_args(args):
        rolls = []

        # Dict in which to temporarily store roll info
        cur_roll = {
            'roll': None,
            'adv': Roll.NORMAL,
            'qty': 1
        }

        for arg in args:
            if arg[0].isdigit():
                if cur_roll['roll'] is not None:
                    roll = Roll.from_str(cur_roll['roll'], cur_roll['adv'])
                    rolls += [roll] * cur_roll['qty']
                cur_roll = {
                    'roll': arg,
                    'adv': Roll.NORMAL,
                    'qty': 1
                }
            elif arg[0] == 'x' and arg[1:].isnumeric():
                cur_roll['qty'] = int(arg[1:])
            else:
                if 'advantage'.startswith(arg):
                    cur_roll['adv'] = Roll.ADVANTAGE
                elif 'disadvantage'.startswith(arg):
                    cur_roll['adv'] = Roll.DISADVANTAGE
                else:
                    raise InvalidSyntaxException()

        roll = Roll.from_str(cur_roll['roll'], cur_roll['adv'])
        rolls += [roll] * cur_roll['qty']

        return '\n\n'.join(str(r.roll()) for r in rolls)


class RollCommandResult:
    def __init__(self):
        pass
