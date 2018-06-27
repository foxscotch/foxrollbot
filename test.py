import random
from unittest import TestCase, main

from roll import Dice, Roll


class DiceTestCase(TestCase):
    def setUp(self):
        random.seed(1, version=2)

    def test_within_bounds_1d20(self):
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
        random.seed(1, version=2)
        d1 = Dice(1, 20)
        d2 = Dice(2, 4)
        d3 = Dice(4, 8)
        self.roll = Roll([d1, d2, d3], [], Roll.ADVANTAGE, 1)
        self.result = self.roll.roll()
        self.expected_output =     \
            f'Total: 39\n'          \
            f'1d20: 13 | 13\n'       \
            f'2d4: 3 | 2, 1\n'        \
            f'4d8: 23 | 8, 1, 7, 7\n'  \
            f'Other roll: 35'
    
    def test_roll_output(self):
        self.assertEqual(str(self.result), self.expected_output)


if __name__ == '__main__':
    main()
