def add_numbers(a: float, b: float) -> float:
    """
    Add two numbers together and return the result.
    
    This function accepts two numeric values (integers or floats) and
    returns their sum as a float.
    
    Args:
        a: The first number to add. Can be int or float.
        b: The second number to add. Can be int or float.
    
    Returns:
        The sum of a and b as a float.
    
    Raises:
        TypeError: If either argument is not a numeric type.
    
    Examples:
        >>> add_numbers(5, 3)
        8.0
        >>> add_numbers(2.5, 3.7)
        6.2
        >>> add_numbers(-10, 15)
        5.0
    """
    # Type validation
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError(f"Both arguments must be numeric types. Got {type(a).__name__} and {type(b).__name__}")
    
    # Perform addition
    result = a + b
    
    return float(result)
print(add_numbers(5, 3))