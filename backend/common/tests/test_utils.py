from django.test import TestCase
from ..utils import normalize_value, invert_analog_value


class NormalizeValueTestCase(TestCase):
    def test_normalize_value_lower(self):
        value = 150
        lower = 100
        upper = 1000
        original_lower = 200
        result = normalize_value(value, lower, upper, original_lower=original_lower)
        self.assertTrue(275 < result < 276)

    def test_normalize_value_upper(self):
        value = 500
        lower = 100
        upper = 1000
        original_upper = 800
        result = normalize_value(value, lower, upper, original_upper=original_upper)
        self.assertTrue(662 < result < 663)

    def test_normalize_value_lower_and_upper(self):
        value = 500
        lower = 100
        upper = 1000
        original_lower = 200
        original_upper = 800
        result = normalize_value(value, lower, upper, original_lower=original_lower, original_upper=original_upper)
        self.assertTrue(662 < result < 663)

    def test_normalize_value_lower_round(self):
        value = 150
        lower = 100
        upper = 1000
        original_lower = 200
        result = normalize_value(value, lower, upper, original_lower=original_lower, round_value=True)
        self.assertEqual(result, 276)

    def test_normalize_value_upper_round(self):
        value = 500
        lower = 100
        upper = 1000
        original_upper = 800
        result = normalize_value(value, lower, upper, original_upper=original_upper, round_value=True)
        self.assertEqual(result, 662)

    def test_normalize_value_lower_and_upper_round(self):
        value = 500
        lower = 100
        upper = 1000
        original_lower = 200
        original_upper = 800
        result = normalize_value(value, lower, upper, original_lower=original_lower, original_upper=original_upper, round_value=True)
        self.assertEqual(result, 662)

    def test_normalize_value_round(self):
        value = 500
        lower = 100
        upper = 1000
        result = normalize_value(value, lower, upper, round_value=True)
        self.assertEqual(result, 540)

    def test_normalize_value(self):
        value = 500
        lower = 100
        upper = 1000
        result = normalize_value(value, lower, upper)
        self.assertTrue(539 < result < 540)


class InvertAnalogValueTestCase(TestCase):
    def test_invert_analog_value_negative(self):
        value = -100
        result = invert_analog_value(value)
        self.assertEqual(result, 1123)

    def test_invert_analog_value_positive(self):
        value = 100
        result = invert_analog_value(value)
        self.assertEqual(result, 923)
