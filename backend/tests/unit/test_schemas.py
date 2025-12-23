
from src.schemas.responses import StandardizedResponse, ErrorDetail, ErrorResponse, PaginationMeta

def test_standardized_response_defaults():
    """Test that StandardizedResponse has correct default values."""
    response = StandardizedResponse()
    assert response.success is True
    assert response.message == "Operation completed successfully"
    assert response.data is None
    assert response.meta is None

def test_standardized_response_with_data():
    """Test StandardizedResponse with data payload."""
    data = {"id": 1, "name": "Test"}
    response = StandardizedResponse(data=data)
    assert response.success is True
    assert response.data == data

def test_error_response_defaults():
    """Test that ErrorResponse has correct default values."""
    error_detail = ErrorDetail(code="not_found", message="Item not found")
    response = ErrorResponse(error=error_detail)
    assert response.success is False
    assert response.error.code == "not_found"
    assert response.error.message == "Item not found"

def test_pagination_meta():
    """Test PaginationMeta model."""
    meta = PaginationMeta(total=100, page=1, limit=10, pages=10)
    assert meta.total == 100
    assert meta.page == 1
    assert meta.limit == 10
    assert meta.pages == 10
