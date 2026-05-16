# Test Generator — 测试模板库

## 1. 纯函数测试

```python
# 纯函数：无副作用，无外部依赖
def add(a: int, b: int) -> int:
    return a + b

def is_even(n: int) -> bool:
    return n % 2 == 0

# 对应测试
class TestAdd:
    @pytest.mark.parametrize("a,b,expected", [
        (1, 2, 3),
        (-1, 1, 0),
        (0, 0, 0),
        (100, 200, 300),
    ])
    def test_add_returns_sum(self, a, b, expected):
        assert add(a, b) == expected

class TestIsEven:
    @pytest.mark.parametrize("n,expected", [
        (2, True),
        (3, False),
        (0, True),
        (-2, True),
        (-3, False),
    ])
    def test_is_even(self, n, expected):
        assert is_even(n) == expected
```

## 2. 异常路径测试

```python
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("division by zero")
    return a / b

def get_user(user_id: int) -> dict:
    if user_id <= 0:
        raise ValueError("invalid user_id")
    user = db.query(f"SELECT * FROM users WHERE id={user_id}")
    if not user:
        raise KeyError(f"user {user_id} not found")
    return user

# 对应测试
class TestDivide:
    def test_divide_by_zero_raises(self):
        with pytest.raises(ValueError, match="division by zero"):
            divide(1, 0)

    @pytest.mark.parametrize("a,b,expected", [
        (10, 2, 5.0),
        (1, 3, 1/3),
        (-6, 2, -3.0),
    ])
    def test_divide_normal(self, a, b, expected):
        assert divide(a, b) == expected

class TestGetUser:
    def test_invalid_id_raises(self):
        with pytest.raises(ValueError):
            get_user(0)

    @patch("module.db.query")
    def test_user_not_found_raises(self, mock_query):
        mock_query.return_value = []
        with pytest.raises(KeyError):
            get_user(999)

    @patch("module.db.query")
    def test_get_user_success(self, mock_query):
        mock_query.return_value = [{"id": 1, "name": "Alice"}]
        result = get_user(1)
        assert result["name"] == "Alice"
```

## 3. Mock 外部依赖

```python
class EmailService:
    def __init__(self):
        self.client = boto3.client("ses", region_name="us-east-1")

    def send_welcome(self, email: str) -> bool:
        try:
            self.client.send_email(
                Source="noreply@example.com",
                Destination={"ToAddresses": [email]},
                Message={"Subject": {"Data": "Welcome!"}, "Body": {"Text": {"Data": "Hello"}}},
            )
            return True
        except Exception:
            return False

# 对应测试
class TestEmailService:
    @patch("module.boto3.client")
    def test_send_welcome_success(self, mock_boto_client):
        mock_ses = MagicMock()
        mock_boto_client.return_value = mock_ses
        service = EmailService()

        result = service.send_welcome("user@example.com")

        assert result is True
        mock_ses.send_email.assert_called_once()

    @patch("module.boto3.client")
    def test_send_welcome_failure_returns_false(self, mock_boto_client):
        mock_ses = MagicMock()
        mock_ses.send_email.side_effect = Exception("AWS timeout")
        mock_boto_client.return_value = mock_ses
        service = EmailService()

        result = service.send_welcome("user@example.com")

        assert result is False
```

## 4. Fixture 和临时文件

```python
import tempfile

class FileProcessor:
    def process(self, path: str) -> int:
        with open(path) as f:
            return len(f.readlines())

# 对应测试
class TestFileProcessor:
    @pytest.fixture
    def tmp_file(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("line1\nline2\nline3\n")
            path = f.name
        yield path
        os.unlink(path)

    def test_process_counts_lines(self, tmp_file):
        processor = FileProcessor()
        assert processor.process(tmp_file) == 3

    def test_process_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            path = f.name
        try:
            processor = FileProcessor()
            assert processor.process(path) == 0
        finally:
            os.unlink(path)
```

## 5. 异步测试

```python
async def fetch_user(api, user_id: int) -> dict:
    return await api.get(f"/users/{user_id}")

# 对应测试
class TestFetchUser:
    @pytest.mark.asyncio
    async def test_fetch_user_success(self):
        mock_api = AsyncMock()
        mock_api.get.return_value = {"id": 1, "name": "Alice"}

        result = await fetch_user(mock_api, 1)

        assert result["name"] == "Alice"
        mock_api.get.assert_called_once_with("/users/1")

    @pytest.mark.asyncio
    async def test_fetch_user_not_found_raises(self):
        mock_api = AsyncMock()
        mock_api.get.side_effect = HTTPError(404)

        with pytest.raises(HTTPError):
            await fetch_user(mock_api, 999)
```

## 6. 上下文管理器和状态测试

```python
class DatabaseConnection:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self._connected = False

    def connect(self):
        self._connected = True

    def disconnect(self):
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

# 对应测试
class TestDatabaseConnection:
    def test_initial_state_is_disconnected(self):
        db = DatabaseConnection("sqlite:///:memory:")
        assert db.is_connected is False

    def test_connect_changes_state(self):
        db = DatabaseConnection("sqlite:///:memory:")
        db.connect()
        assert db.is_connected is True

    def test_disconnect_after_connect(self):
        db = DatabaseConnection("sqlite:///:memory:")
        db.connect()
        db.disconnect()
        assert db.is_connected is False
```
