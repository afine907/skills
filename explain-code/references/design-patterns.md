# Design Patterns Reference

## Creational Patterns

### Singleton

Ensures a class has only one instance.

```python
class DatabasePool:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, connection_string: str):
        if not self._initialized:
            self.pool = create_pool(connection_string)
            self._initialized = True
```

**When to use**: Database connections, configuration, logging.
**When to avoid**: Testing (hard to mock), when you need multiple instances.

### Factory Method

Defines an interface for creating objects, letting subclasses decide which class to instantiate.

```python
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message: str) -> bool: ...

class EmailNotification(Notification):
    def send(self, message: str) -> bool:
        return email_service.send(message)

class SMSNotification(Notification):
    def send(self, message: str) -> bool:
        return sms_service.send(message)

class NotificationFactory:
    @staticmethod
    def create(channel: str) -> Notification:
        match channel:
            case "email": return EmailNotification()
            case "sms": return SMSNotification()
            case _: raise ValueError(f"Unknown channel: {channel}")
```

### Builder

Separates construction of a complex object from its representation.

```python
class QueryBuilder:
    def __init__(self):
        self._table = None
        self._conditions = []
        self._order_by = None
        self._limit = None

    def table(self, name: str) -> "QueryBuilder":
        self._table = name
        return self

    def where(self, condition: str) -> "QueryBuilder":
        self._conditions.append(condition)
        return self

    def order_by(self, column: str) -> "QueryBuilder":
        self._order_by = column
        return self

    def limit(self, n: int) -> "QueryBuilder":
        self._limit = n
        return self

    def build(self) -> str:
        query = f"SELECT * FROM {self._table}"
        if self._conditions:
            query += " WHERE " + " AND ".join(self._conditions)
        if self._order_by:
            query += f" ORDER BY {self._order_by}"
        if self._limit:
            query += f" LIMIT {self._limit}"
        return query

# Usage
query = (QueryBuilder()
    .table("users")
    .where("age > 18")
    .where("active = true")
    .order_by("name")
    .limit(10)
    .build())
```

## Structural Patterns

### Adapter

Converts the interface of a class into another interface clients expect.

```python
class OldPaymentGateway:
    def charge_card(self, card_number: str, amount_cents: int) -> dict:
        ...

class NewPaymentGateway(ABC):
    @abstractmethod
    def process_payment(self, amount: float, currency: str) -> PaymentResult: ...

class PaymentAdapter(NewPaymentGateway):
    def __init__(self, old_gateway: OldPaymentGateway):
        self.old = old_gateway

    def process_payment(self, amount: float, currency: str) -> PaymentResult:
        result = self.old.charge_card(
            card_number=self._get_card(),
            amount_cents=int(amount * 100),
        )
        return PaymentResult(success=result["approved"])
```

### Decorator

Adds behavior to objects dynamically without altering their interface.

```python
from functools import wraps
import time

def timing(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        duration = time.perf_counter() - start
        logger.info(f"{func.__name__} took {duration:.3f}s")
        return result
    return wrapper

def retry(max_attempts=3, delay=1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(delay * (2 ** attempt))
        return wrapper
    return decorator

@timing
@retry(max_attempts=3)
async def fetch_data(url: str):
    ...
```

### Facade

Provides a simplified interface to a complex subsystem.

```python
class OrderFacade:
    """Simplifies the order placement process."""

    def __init__(self):
        self.inventory = InventoryService()
        self.payment = PaymentService()
        self.shipping = ShippingService()
        self.notification = NotificationService()

    def place_order(self, order: Order) -> OrderResult:
        # 1. Check inventory
        if not self.inventory.check_availability(order.items):
            return OrderResult(success=False, reason="Out of stock")

        # 2. Process payment
        payment_result = self.payment.charge(order.total, order.payment_method)
        if not payment_result.success:
            return OrderResult(success=False, reason="Payment failed")

        # 3. Create shipment
        tracking = self.shipping.create_shipment(order)

        # 4. Notify customer
        self.notification.send_confirmation(order, tracking)

        return OrderResult(success=True, tracking=tracking)
```

## Behavioral Patterns

### Strategy

Defines a family of algorithms and makes them interchangeable.

```python
from typing import Protocol

class SortStrategy(Protocol):
    def sort(self, data: list) -> list: ...

class QuickSort:
    def sort(self, data: list) -> list:
        # QuickSort implementation
        ...

class MergeSort:
    def sort(self, data: list) -> list:
        # MergeSort implementation
        ...

class Sorter:
    def __init__(self, strategy: SortStrategy):
        self.strategy = strategy

    def sort(self, data: list) -> list:
        return self.strategy.sort(data)

# Usage
sorter = Sorter(QuickSort())
result = sorter.sort([3, 1, 4, 1, 5])
```

### Observer

Defines a one-to-many dependency so that when one object changes state, all dependents are notified.

```python
class EventEmitter:
    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, callback: Callable):
        self._listeners.setdefault(event, []).append(callback)

    def emit(self, event: str, *args, **kwargs):
        for callback in self._listeners.get(event, []):
            callback(*args, **kwargs)

# Usage
emitter = EventEmitter()
emitter.on("user.created", send_welcome_email)
emitter.on("user.created", create_default_workspace)
emitter.emit("user.created", user=new_user)
```

### Middleware (Chain of Responsibility)

Passes a request along a chain of handlers.

```python
class Middleware(ABC):
    def __init__(self):
        self.next: Optional[Middleware] = None

    @abstractmethod
    async def handle(self, request: Request) -> Response: ...

class AuthMiddleware(Middleware):
    async def handle(self, request: Request) -> Response:
        if not request.headers.get("Authorization"):
            return Response(status=401)
        return await self.next.handle(request)

class RateLimitMiddleware(Middleware):
    async def handle(self, request: Request) -> Response:
        if await self.is_rate_limited(request.client_ip):
            return Response(status=429)
        return await self.next.handle(request)

# Chain them
auth = AuthMiddleware()
rate_limit = RateLimitMiddleware()
auth.next = rate_limit
rate_limit.next = final_handler
```

## Anti-Patterns to Recognize

| Anti-Pattern | Description | Better Approach |
|--------------|-------------|-----------------|
| God Object | One class does everything | Single Responsibility Principle |
| Spaghetti Code | Unstructured, tangled logic | Extract methods, use patterns |
| Copy-Paste | Duplicated code blocks | Extract shared logic |
| Golden Hammer | Using one tool for everything | Choose the right pattern per case |
| Premature Optimization | Optimizing before measuring | Profile first, then optimize |
