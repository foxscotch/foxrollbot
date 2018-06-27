import random
from unittest import TestCase, main

from roll import Dice, Roll
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

        d1 = Dice(1, 20)
        d2 = Dice(2, 4)
        d3 = Dice(4, 8)

        self.dice = d1
        self.roll = Roll([d1, d2, d3], [], Roll.ADVANTAGE)
    
    def test_roll_output(self):
        self.result = self.roll.roll()
        self.expected_output =     \
            f'Total: 39\n'          \
            f'1d20: 13\n'            \
            f'2d4: 3 | 2, 1\n'        \
            f'4d8: 23 | 8, 1, 7, 7\n'  \
            f'Other roll: 35'
        self.assertEqual(str(self.result), self.expected_output)
    
    def test_disallows_too_many_components(self):
        modifiers = [1] * Roll.MAX_COMPONENTS
        self.assertRaises(TooManyComponentsException,
                          lambda: Roll([self.dice], modifiers, Roll.NORMAL))
    
    def test_disallows_small_modifier(self):
        self.assertRaises(OutOfRangeException,
                          lambda: Roll([self.dice], [0], Roll.NORMAL))
    
    def test_disallows_large_modifier(self):
        modifier = Roll.MAX_MODIFIER + 1
        self.assertRaises(OutOfRangeException,
                          lambda: Roll([self.dice], [modifier], Roll.NORMAL))


if __name__ == '__main__':
    main()
