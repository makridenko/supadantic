import re


def _to_snake_case(value: str) -> str:
    """
    Converts a string from camel case or Pascal case to snake case.

    This function uses a regular expression to find uppercase letters within
    the string and inserts an underscore before them (except at the beginning
    of the string).  The entire string is then converted to lowercase.

    Args:
        value (str): The string to convert.

    Returns:
        (str): The snake_case version of the input string.

    Example:
        >>> _to_snake_case("MyClassName")
        'my_class_name'
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower()
