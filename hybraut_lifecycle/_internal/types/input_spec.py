from typing import NamedTuple, Any, Optional

class InputSpec(NamedTuple):
    name: str 
    type: Any
    buffer_size: Optional[int] = 1

    @classmethod
    def create_input_spec(cls, name: str, type: Any, buffer_size: Optional[int] = 1):
        """
        Factory method to create an InputSpec instance with validation.

        Args:
            name (str): Name of the input.
            type (Any): Type of the input (e.g., float, int, etc.).
            buffer_size (Optional[int], default=1): Size of the buffer, must be an integer >= 1.

        Returns:
            InputSpec: Validated InputSpec instance.

        Raises:
            TypeError: If buffer_size is not an integer.
            ValueError: If buffer_size is less than 1.
        """
        if not isinstance(buffer_size, int):
            raise TypeError(f"buffer_size must be of type int, not {type(buffer_size).__name__}")
        if buffer_size < 1:
            raise ValueError("buffer_size must be at least 1")

        return cls(
            name=name,
            type=type,
            buffer_size=buffer_size
        )