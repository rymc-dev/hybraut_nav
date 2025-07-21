from typing import NamedTuple, Any

class IOSpec(NamedTuple):
    name: str 
    type: Any

    @classmethod
    def create_io_spec(cls, name: str, type: Any):
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

        return cls(
            name=name,
            type=type
        )