from unittest import TestCase, main

from roll import Dice, Roll


class RollTestCase(TestCase):
    def setUp(self):
        d1 = Dice(1, 20)
        d2 = Dice(2, 4)
        d3 = Dice(4, 8)
        self.roll = Roll([d1, d2, d3], [], Roll.ADVANTAGE, 1)
        self.result = self.roll.roll()
        self.expected_output =              \
            f'Total: {self.result.total}\n'  \
            f'{str(self.result.rolls[0])}\n'  \
            f'{str(self.result.rolls[1])}\n'   \
            f'{str(self.result.rolls[2])}\n'    \
            f'Other roll: {self.result.losing}'.strip()
    
    def test_roll_output(self):
        self.assertEqual(str(self.result), self.expected_output)


if __name__ == '__main__':
    main()
