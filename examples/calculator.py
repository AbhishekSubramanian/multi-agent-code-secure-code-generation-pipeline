"""
Calculator Module

A comprehensive calculator that performs basic arithmetic operations,
scientific calculations, and provides a user-friendly interface.
"""

import math
from typing import Union

Number = Union[int, float]


class Calculator:
    """
    A calculator class that performs various mathematical operations.
    
    Supports basic arithmetic, scientific functions, and maintains
    calculation history.
    """
    
    def __init__(self):
        """Initialize the calculator with empty history."""
        self.history = []
    
    def add(self, a: Number, b: Number) -> Number:
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
        
        Returns:
            Sum of a and b
        """
        result = a + b
        self._add_to_history(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: Number, b: Number) -> Number:
        """
        Subtract b from a.
        
        Args:
            a: First number (minuend)
            b: Second number (subtrahend)
        
        Returns:
            Difference of a and b
        """
        result = a - b
        self._add_to_history(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: Number, b: Number) -> Number:
        """
        Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
        
        Returns:
            Product of a and b
        """
        result = a * b
        self._add_to_history(f"{a} × {b} = {result}")
        return result
    
    def divide(self, a: Number, b: Number) -> float:
        """
        Divide a by b.
        
        Args:
            a: Numerator
            b: Denominator
        
        Returns:
            Quotient of a and b
        
        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self._add_to_history(f"{a} ÷ {b} = {result}")
        return result
    
    def power(self, base: Number, exponent: Number) -> Number:
        """
        Raise base to the power of exponent.
        
        Args:
            base: The base number
            exponent: The exponent
        
        Returns:
            base raised to the power of exponent
        """
        result = base ** exponent
        self._add_to_history(f"{base} ^ {exponent} = {result}")
        return result
    
    def square_root(self, n: Number) -> float:
        """
        Calculate the square root of n.
        
        Args:
            n: Number to find square root of
        
        Returns:
            Square root of n
        
        Raises:
            ValueError: If n is negative
        """
        if n < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = math.sqrt(n)
        self._add_to_history(f"√{n} = {result}")
        return result
    
    def modulo(self, a: Number, b: Number) -> Number:
        """
        Calculate the remainder of a divided by b.
        
        Args:
            a: Dividend
            b: Divisor
        
        Returns:
            Remainder of a divided by b
        
        Raises:
            ValueError: If b is zero
        """
        if b == 0:
            raise ValueError("Cannot perform modulo with zero divisor")
        result = a % b
        self._add_to_history(f"{a} mod {b} = {result}")
        return result
    
    def factorial(self, n: int) -> int:
        """
        Calculate the factorial of n.
        
        Args:
            n: Non-negative integer
        
        Returns:
            Factorial of n
        
        Raises:
            ValueError: If n is negative or not an integer
        """
        if not isinstance(n, int):
            raise ValueError("Factorial requires an integer argument")
        if n < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        result = math.factorial(n)
        self._add_to_history(f"{n}! = {result}")
        return result
    
    def percentage(self, value: Number, percent: Number) -> float:
        """
        Calculate percentage of a value.
        
        Args:
            value: The base value
            percent: The percentage to calculate
        
        Returns:
            percent% of value
        """
        result = (value * percent) / 100
        self._add_to_history(f"{percent}% of {value} = {result}")
        return result
    
    def sine(self, angle_degrees: Number) -> float:
        """
        Calculate sine of an angle.
        
        Args:
            angle_degrees: Angle in degrees
        
        Returns:
            Sine of the angle
        """
        result = math.sin(math.radians(angle_degrees))
        self._add_to_history(f"sin({angle_degrees}°) = {result}")
        return result
    
    def cosine(self, angle_degrees: Number) -> float:
        """
        Calculate cosine of an angle.
        
        Args:
            angle_degrees: Angle in degrees
        
        Returns:
            Cosine of the angle
        """
        result = math.cos(math.radians(angle_degrees))
        self._add_to_history(f"cos({angle_degrees}°) = {result}")
        return result
    
    def tangent(self, angle_degrees: Number) -> float:
        """
        Calculate tangent of an angle.
        
        Args:
            angle_degrees: Angle in degrees
        
        Returns:
            Tangent of the angle
        
        Raises:
            ValueError: If angle is 90° or 270° (where tangent is undefined)
        """
        if angle_degrees % 180 == 90:
            raise ValueError(f"Tangent is undefined at {angle_degrees}°")
        result = math.tan(math.radians(angle_degrees))
        self._add_to_history(f"tan({angle_degrees}°) = {result}")
        return result
    
    def logarithm(self, n: Number, base: Number = math.e) -> float:
        """
        Calculate logarithm of n with specified base.
        
        Args:
            n: Number to calculate logarithm of
            base: Base of the logarithm (default: e for natural log)
        
        Returns:
            Logarithm of n with given base
        
        Raises:
            ValueError: If n or base are invalid
        """
        if n <= 0:
            raise ValueError("Logarithm argument must be positive")
        if base <= 0 or base == 1:
            raise ValueError("Logarithm base must be positive and not equal to 1")
        
        result = math.log(n, base)
        base_str = "e" if base == math.e else str(base)
        self._add_to_history(f"log_{base_str}({n}) = {result}")
        return result
    
    def absolute_value(self, n: Number) -> Number:
        """
        Calculate the absolute value of n.
        
        Args:
            n: Number to find absolute value of
        
        Returns:
            Absolute value of n
        """
        result = abs(n)
        self._add_to_history(f"|{n}| = {result}")
        return result
    
    def _add_to_history(self, operation: str) -> None:
        """
        Add an operation to the calculation history.
        
        Args:
            operation: String representation of the operation
        """
        self.history.append(operation)
    
    def get_history(self) -> list[str]:
        """
        Retrieve the calculation history.
        
        Returns:
            List of all operations performed
        """
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear the calculation history."""
        self.history.clear()
    
    def display_history(self) -> None:
        """Print the calculation history to console."""
        if not self.history:
            print("No calculations in history.")
            return
        
        print("\n" + "=" * 40)
        print("CALCULATION HISTORY")
        print("=" * 40)
        for idx, operation in enumerate(self.history, 1):
            print(f"{idx}. {operation}")
        print("=" * 40 + "\n")


def main():
    """
    Demonstrate calculator functionality with example operations.
    """
    calc = Calculator()
    
    print("=" * 50)
    print("CALCULATOR DEMO".center(50))
    print("=" * 50 + "\n")
    
    # Basic arithmetic
    print("BASIC ARITHMETIC:")
    print(f"Addition: 15 + 7 = {calc.add(15, 7)}")
    print(f"Subtraction: 20 - 8 = {calc.subtract(20, 8)}")
    print(f"Multiplication: 6 × 7 = {calc.multiply(6, 7)}")
    print(f"Division: 100 ÷ 4 = {calc.divide(100, 4)}")
    print(f"Power: 2 ^ 8 = {calc.power(2, 8)}")
    print(f"Modulo: 17 mod 5 = {calc.modulo(17, 5)}")
    
    # Advanced operations
    print("\nADVANCED OPERATIONS:")
    print(f"Square root: √64 = {calc.square_root(64)}")
    print(f"Factorial: 5! = {calc.factorial(5)}")
    print(f"Percentage: 25% of 200 = {calc.percentage(200, 25)}")
    print(f"Absolute value: |-15| = {calc.absolute_value(-15)}")
    
    # Trigonometric functions
    print("\nTRIGONOMETRIC FUNCTIONS:")
    print(f"sin(30°) = {calc.sine(30):.4f}")
    print(f"cos(60°) = {calc.cosine(60):.4f}")
    print(f"tan(45°) = {calc.tangent(45):.4f}")
    
    # Logarithms
    print("\nLOGARITHMS:")
    print(f"ln(10) = {calc.logarithm(10):.4f}")
    print(f"log₁₀(100) = {calc.logarithm(100, 10):.4f}")
    
    # Display history
    calc.display_history()


if __name__ == "__main__":
    main()