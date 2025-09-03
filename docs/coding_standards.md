# Coding Standards for Starter Town Tactics

## Import Order
Follow this exact order:
```python
# Standard library imports
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party imports
import pygame
import yaml
```

## Exception Handling
Use specific exceptions, never catch `Exception`:
```python
# ✅ Good
try:
    pygame.image.load(file_path)
except (pygame.error, OSError, ValueError) as e:
    logger.error(f"Failed to load {file_path}: {e}")

# ❌ Bad
try:
    pygame.image.load(file_path)
except Exception as e:
    print(f"Failed: {e}")
```

## File Operations
Always specify encoding:
```python
# ✅ Good
with open(path, 'r', encoding='utf-8') as f:
    data = f.read()

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

# ❌ Bad
with open(path, 'r') as f:
    data = f.read()
```

## Type Annotations
Use `Optional` for nullable types:
```python
# ✅ Good
def get_unit_sprite(self, unit_name: str) -> Optional[str]:
    pass

# ❌ Bad
def get_unit_sprite(self, unit_name: str) -> str | None:
    pass
```

## Class Design Limits
- **Methods per class**: ≤ 20 public methods
- **Arguments per method**: ≤ 5 positional arguments
- **Instance attributes**: ≤ 10 per class
- **Method complexity**: ≤ 12 branches, ≤ 15 local variables

## Error Handling Patterns
```python
# Standard error handling pattern
def safe_operation(self, *args, **kwargs):
    """Perform operation with proper error handling."""
    try:
        result = self._perform_operation(*args, **kwargs)
        if self.logger:
            self.logger.log_event("operation_success", {"result": result})
        return result
    except (ValueError, KeyError, AttributeError) as e:
        if self.logger:
            self.logger.log_event("operation_failed", {"error": str(e)})
        return None
```

## Logging Standards
```python
# Use structured logging
if self.logger:
    self.logger.log_event("event_name", {
        "unit_id": unit_id,
        "action": action,
        "result": result
    })
```

## Testing Requirements
- Every new class must have unit tests
- Every new method must have at least one test case
- Integration tests for complex interactions
- Test coverage target: ≥80%

## Documentation Standards
```python
def complex_method(self, param1: str, param2: int) -> bool:
    """
    Brief description of what the method does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid
        KeyError: When param2 is not found
    """
    pass
```

## Architecture Patterns
- **No singletons**: Pass instances to constructors
- **Dependency injection**: Use constructor parameters
- **Separation of concerns**: One class, one responsibility
- **Interface segregation**: Keep interfaces small and focused
