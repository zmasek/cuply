def normalize_value(value, lower, upper, original_lower=0, original_upper=1023, round_value=False):
    # restrict to limits
    if value < original_lower:
        value = original_lower
    elif value > original_upper:
        value = original_upper

    percentage = abs(value / original_upper)

    new_range_max = upper - lower
    normalized = lower + percentage * new_range_max

    return normalized if not round_value else round(normalized)

def invert_analog_value(value):
    return (value * -1) + 1023
