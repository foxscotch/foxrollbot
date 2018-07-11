import random
import sqlite3
from unittest import TestCase, main

from db import SavedRollManager
from roll import Dice, Roll, RollCommand
from errors import *


def reset_seed():
    # Keep in mind that if the seed changes, all of the outputs will too.
    random.seed(1, version=2)


class DiceTestCase(TestCase):
    def setUp(self):
        reset_seed()
    
    def test_from_str(self):
        self.assertEqual(Dice.from_str('1d20'), Dice(1, 20))
    
    def test_single_die_output(self):
        dice = Dice(1, 20)
        self.assertEqual(str(dice.roll()), '1d20: 5')
    
    def test_multi_dice_output(self):
        dice = Dice(4, 8)
        self.assertEqual(str(dice.roll()), '4d8: 12 | 3, 2, 5, 2')
    
    def test_disallows_small_quantities(self):
        self.assertRaises(OutOfRangeException, lambda: Dice(0, 2))
    
    def test_disallows_large_quantities(self):
        quantity = Dice.MAX_DICE + 1
        self.assertRaises(OutOfRangeException, lambda: Dice(quantity, 2))
    
    def test_disallows_small_dice(self):
        self.assertRaises(OutOfRangeException, lambda: Dice(1, 1))
    
    def test_disallows_large_dice(self):
        sides = Dice.MAX_SIDES + 1
        self.assertRaises(OutOfRangeException, lambda: Dice(1, sides))

    def test_equals_comparison(self):
        d1 = Dice(1, 20)
        d2 = Dice(1, 20)
        d3 = Dice(4, 6)
        self.assertEqual(d1, d2)
        self.assertNotEqual(d1, d3)

    def test_within_bounds_1d20(self):
        # I'm not sure if this test and the next are really necessary,
        # especially given that I'm testing pre-determined output. But I'll
        # leave them here for now.
        dice = Dice(1, 20)
        result = sum(dice.roll().results)
        self.assertGreaterEqual(result, 1)
        self.assertLessEqual(result, 20)

    def test_within_bounds_2d6(self):
        dice = Dice(2, 6)
        result = sum(dice.roll().results)
        self.assertGreaterEqual(result, 2)
        self.assertLessEqual(result, 12)


class RollTestCase(TestCase):
    def setUp(self):
        reset_seed()
    
    def test_from_str(self):
        r1 = Roll([Dice(1, 20), Dice(4, 6)], [5, -2], False)
        r2 = Roll.from_str('1d20+4d6+5-2', False)
        self.assertEqual(r1, r2)
    
    def test_simple_roll_output(self):
        roll = Roll([Dice(1, 20)], [], Roll.NORMAL)
        result = roll.roll()
        expected_output = '1d20: 5'
        self.assertEqual(str(result), expected_output)
    
    def test_simple_roll_output_with_advantage(self):
        roll = Roll([Dice(1, 20)], [], Roll.ADVANTAGE)
        result = roll.roll()
        expected_output = ('1d20: 19\n'
                           'Other roll: 5')
        self.assertEqual(str(result), expected_output)
    
    def test_simple_roll_output_with_disadvantage(self):
        roll = Roll([Dice(1, 20)], [], Roll.DISADVANTAGE)
        result = roll.roll()
        expected_output = ('1d20: 5\n'
                           'Other roll: 19')
        self.assertEqual(str(result), expected_output)
    
    def test_complex_roll_output(self):
        d1 = Dice(1, 20)
        d2 = Dice(2, 4)
        d3 = Dice(4, 8)
        roll = Roll([d1, d2, d3], [], Roll.ADVANTAGE)
        result = roll.roll()
        expected_output = ('Total: 39\n'
                           '1d20: 13\n'
                           '2d4: 3 | 2, 1\n'
                           '4d8: 23 | 8, 1, 7, 7\n'
                           'Other roll: 35')
        self.assertEqual(str(result), expected_output)
    
    def test_disallows_too_many_components(self):
        dice = Dice(1, 20)
        modifiers = [1] * Roll.MAX_COMPONENTS
        self.assertRaises(TooManyComponentsException,
                          lambda: Roll([dice], modifiers, Roll.NORMAL))
    
    def test_disallows_small_modifier(self):
        dice = Dice(1, 20)
        self.assertRaises(OutOfRangeException,
                          lambda: Roll([dice], [0], Roll.NORMAL))
    
    def test_disallows_large_modifier(self):
        dice = Dice(1, 20)
        modifier = Roll.MAX_MODIFIER + 1
        self.assertRaises(OutOfRangeException,
                          lambda: Roll([dice], [modifier], Roll.NORMAL))

    def test_equals_comparison(self):
        d1 = Dice(1, 20)
        d2 = Dice(1, 20)
        d3 = Dice(4, 6)

        r1 = Roll([d1, d2, d3], [5, -2])
        r2 = Roll(r1.rolls, r1.modifiers, r1.advantage)
        r3 = Roll([d1, d3], [1, 6], Roll.ADVANTAGE)

        self.assertEqual(r1, r2)
        self.assertNotEqual(r1, r3)


class RollCommandTestCase(TestCase):
    def setUp(self):
        reset_seed()
    
    def test_roll_command_output(self):
        args = ['1d20', 'adv', 'x2']
        rc = RollCommand.from_args(args)
        expected_output = ('1d20: 19\n'
                           'Other roll: 5\n\n'
                           '1d20: 9\n'
                           'Other roll: 3')
        self.assertEqual(str(rc), expected_output)
    
    def test_disallows_too_many_rolls(self):
        roll = Roll([Dice(1, 20)], [], Roll.NORMAL)
        rolls = [roll] * (Roll.MAX_COMPONENTS + 1)
        self.assertRaises(TooManyComponentsException,
                          lambda: RollCommand(rolls))


class SavedRollManagerTestCase(TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.srm = SavedRollManager(self.conn)

        # Insert example entry
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO saved_rolls VALUES (?, ?, ?, ?, ?);'
                       None, 'example_roll', '1d20 adv', 12345, None)

    def get_db_entries(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM saved_rolls;')
        results = cursor.fetchall()
        return len(results), results

    def test_save(self):
        self.srm.save('test_roll', ['4d6', 'x2'], chat=54321)
        length, results = self.get_db_entries()
        self.assertEqual(length, 2)
        self.assertEqual(results[0], (1, 'test_roll', '4d6 x2', None, 54321))

    def test_get(self):
        self.test_save()
        args = self.srm.get('example_roll', user=12345)
        self.assertEqual(args, ['1d20', 'adv'])

    def test_delete(self):
        self.test_save()
        self.srm.delete('test_roll', user=12345)
        length = self.get_db_entries()[0]
        self.assertEqual(length, 0)


if __name__ == '__main__':
    main()
