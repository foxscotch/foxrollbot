import random
from unittest import TestCase, main

from roll import Dice, Roll, RollCommand
from errors import *


def reset_seed():
    # Keep in mind that if the seed changes, all of the outputs will too.
    random.seed(1, version=2)


class DiceTestCase(TestCase):
    def setUp(self):
        reset_seed()
    
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
    
    def test_simple_roll_output(self):
        roll = Roll([Dice(1, 20)], [], Roll.NORMAL)
        result = roll.roll()
        expected_output = '1d20: 5'
        self.assertEqual(str(result), expected_output)
    
    def test_simple_roll_output_with_advantage(self):
        roll = Roll([Dice(1, 20)], [], Roll.ADVANTAGE)
        result = roll.roll()
        expected_output =     \
            f'1d20: 19\n'      \
            f'Other roll: 5'
        self.assertEqual(str(result), expected_output)
    
    def test_simple_roll_output_with_disadvantage(self):
        roll = Roll([Dice(1, 20)], [], Roll.DISADVANTAGE)
        result = roll.roll()
        expected_output =      \
            f'1d20: 5\n'        \
            f'Other roll: 19'
        self.assertEqual(str(result), expected_output)
    
    def test_complex_roll_output(self):
        d1 = Dice(1, 20)
        d2 = Dice(2, 4)
        d3 = Dice(4, 8)
        roll = Roll([d1, d2, d3], [], Roll.ADVANTAGE)
        result = roll.roll()
        expected_output =          \
            f'Total: 39\n'          \
            f'1d20: 13\n'            \
            f'2d4: 3 | 2, 1\n'        \
            f'4d8: 23 | 8, 1, 7, 7\n'  \
            f'Other roll: 35'
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


class RollCommandTestCase(TestCase):
    def setUp(self):
        reset_seed()
    
    def test_roll_command_output(self):
        args = ['1d20', 'adv', 'x2']
        rc = RollCommand.from_args(args)
        expected_output =       \
            f'1d20: 19\n'        \
            f'Other roll: 5\n\n'  \
            f'1d20: 9\n'           \
            f'Other roll: 3'
        self.assertEqual(str(rc), expected_output)


if __name__ == '__main__':
    main()
