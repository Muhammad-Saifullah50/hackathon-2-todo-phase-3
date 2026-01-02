# MCP Server Test Suite

Comprehensive test coverage for the MCP (Model Context Protocol) server.

## Test Files

### `test_mcp_tools.py`
Basic unit tests for all MCP tools:
- `add_task`
- `list_tasks`
- `complete_task`
- `update_task`
- `delete_task`

### `test_mcp_comprehensive.py` ⭐ NEW
Comprehensive unit tests covering:
- **Edge cases**: Empty inputs, invalid formats, boundary conditions
- **Error handling**: Database errors, network errors, validation failures
- **All input variations**: Valid/invalid priorities, dates, status values
- **Authentication behavior**: Documents current insecure defaults
- **Database operations**: Connection pooling, transactions, rollbacks

**Critical Tests for Future Changes:**
- `TestAuthenticationBehavior` - Will fail when authentication is added (GOOD!)
- `TestDatabaseConnectionPool` - Verifies pool reuse
- `TestErrorHandling` - Ensures graceful error handling

### `test_mcp_integration.py` ⭐ NEW
Integration tests for HTTP layer:
- FastAPI configuration
- CORS settings
- Health check endpoint
- MCP protocol endpoints (SSE, message)
- Security configuration (documents gaps)
- Lifespan management

**Security Gap Documentation:**
- `TestSecurityConfiguration` - Documents CORS allowing all origins
- `TestSecurityHeaders` - Shows missing security headers
- `test_rate_limiting_missing` - No rate limiting implemented
- `test_monkey_patch_location_documented` - Documents security bypass

## Running Tests

### Run All Tests
```bash
cd mcp_server
pytest
```

### Run Specific Test File
```bash
pytest tests/test_mcp_comprehensive.py
pytest tests/test_mcp_integration.py
pytest tests/test_mcp_tools.py
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Tests Matching Pattern
```bash
pytest -k "auth"  # All authentication-related tests
pytest -k "database"  # All database tests
pytest -k "security"  # All security tests
```

## Test Strategy

### Unit Tests
- Mock all database connections
- Test individual function behavior
- Fast execution (< 1 second)
- No external dependencies

### Integration Tests
- Test HTTP layer
- Mock database but test FastAPI
- Verify CORS, middleware, routing
- Test lifespan management

## Critical Test Cases

### 🚨 Tests That Document Security Issues

These tests will FAIL when security is properly implemented (this is GOOD):

1. **`test_default_user_id_is_used`** (test_mcp_comprehensive.py)
   - Documents that default user_id is used
   - SHOULD FAIL when authentication is required

2. **`test_user_id_can_be_overridden`** (test_mcp_comprehensive.py)
   - Documents that anyone can set any user_id
   - SHOULD FAIL when JWT authentication is added

3. **`test_cors_allows_all_origins`** (test_mcp_integration.py)
   - Documents that CORS allows ALL origins
   - SHOULD FAIL when restricted to specific domains

4. **`test_no_host_validation`** (test_mcp_integration.py)
   - Documents that host validation is bypassed
   - SHOULD FAIL when TrustedHostMiddleware is properly configured

5. **`test_security_headers_missing`** (test_mcp_integration.py)
   - Documents missing security headers
   - SHOULD FAIL when headers are added

## Test Coverage Goals

| Module | Current | Target |
|--------|---------|--------|
| MCP Tools | 60% | 95% ✅ |
| HTTP Layer | 0% | 80% ✅ |
| Auth | 0% | 90% (after implementation) |
| Error Handling | 40% | 90% ✅ |
| Database | 50% | 85% ✅ |

## Test Maintenance

### When Adding New MCP Tools
1. Add basic tests to `test_mcp_tools.py`
2. Add comprehensive tests to `test_mcp_comprehensive.py`
3. Add integration tests to `test_mcp_integration.py`

### When Fixing Security Issues
1. Existing tests will fail - this is EXPECTED
2. Update tests to verify new secure behavior
3. Add new tests for authentication flows
4. Ensure tests verify JWT validation

### When Adding Features
1. Write tests FIRST (TDD)
2. Ensure tests fail without implementation
3. Implement feature
4. Verify all tests pass
5. Check coverage: `pytest --cov`

## Dependencies

- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `httpx` - HTTP client for integration tests
- `python-dotenv` - Environment variable loading

## Environment Setup

Tests use mock environment variables (see `conftest.py`):
- `DATABASE_URL=postgresql://test:test@localhost:5432/test_db`
- `FRONTEND_URL=http://localhost:3000`

No real database connection required for tests.

## CI/CD Integration

### GitHub Actions Example
```yaml
name: MCP Server Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          cd mcp_server
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd mcp_server
          pytest -v --cov --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Debugging Tests

### Run Single Test
```bash
pytest tests/test_mcp_comprehensive.py::TestAddTaskComprehensive::test_add_task_minimal_required_fields -v
```

### Enable Debug Output
```bash
pytest -v -s  # -s shows print statements
```

### Run with Debugger
```bash
pytest --pdb  # Drop into debugger on failure
```

## Test Markers

Use markers to categorize tests:
```python
@pytest.mark.asyncio  # Async test
@pytest.mark.integration  # Integration test
@pytest.mark.unit  # Unit test
@pytest.mark.slow  # Slow running test
```

Run specific marker:
```bash
pytest -m unit  # Run only unit tests
pytest -m integration  # Run only integration tests
```

## Known Issues

1. **No Real Database Tests**: Tests use mocks, need actual database tests
2. **No Performance Tests**: Should add load/stress tests
3. **No Security Audit Tests**: Should add OWASP ZAP integration
4. **Missing E2E Tests**: Need tests with real MCP client

## Future Improvements

- [ ] Add real database integration tests with test database
- [ ] Add performance/load tests with locust or k6
- [ ] Add security scanning in CI/CD
- [ ] Add E2E tests with actual MCP client
- [ ] Add mutation testing with mutmut
- [ ] Increase coverage to 95%+
- [ ] Add contract testing for MCP protocol

## Contributing

When adding tests:
1. Follow existing patterns
2. Add docstrings explaining what is tested
3. Use descriptive test names
4. Mock external dependencies
5. Keep tests fast (< 100ms each)
6. Document security issues explicitly

---

**Remember:** Tests that fail when security is added are GOOD - they document the current insecure behavior and verify the fixes work!
