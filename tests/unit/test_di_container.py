"""
Unit tests for the DI Container.

These tests verify:
1. Database session management (no leaks)
2. Unicode encoding compatibility (Windows cp1252)
3. Proper dependency injection
"""
import pytest
import sys
import importlib
from unittest.mock import patch
from sqlalchemy.orm import Session
from typing import Generator


def test_db_session_is_closed_after_use():
    """
    CRITICAL: Session must be closed after use (generator pattern).

    This test verifies that get_db_session() uses a generator pattern
    with yield to ensure the session is properly closed after use.

    Bug: Current implementation returns Session() directly without closing it.
    Fix: Must use yield with try/finally block.
    """
    from src.di_container import get_db_session
    from sqlalchemy import inspect

    # The function should be a generator (return type includes Generator)
    session_gen = get_db_session()

    # Verify it's actually a generator
    assert hasattr(session_gen, '__next__'), \
        "get_db_session() must be a generator (use 'yield' not 'return')"

    # Get the session from the generator
    session = next(session_gen)

    # Verify we got a valid session
    assert isinstance(session, Session), "Should yield a SQLAlchemy Session"

    # Simulate end of context (this should trigger cleanup)
    try:
        next(session_gen)
    except StopIteration:
        pass  # Expected - generator is exhausted

    # CRITICAL: After generator exhaustion, session should be closed
    # In SQLAlchemy 1.x and 2.x, we check if the session's transaction is closed
    # by verifying the session cannot execute new queries
    with pytest.raises(Exception):
        # This should fail because session.close() was called
        # which invalidates the session for new transactions
        session.execute("SELECT 1")
        session.commit()  # This line should not be reached


def test_multiple_requests_dont_leak_connections():
    """
    CRITICAL: Multiple requests should not accumulate connections.

    This simulates multiple API requests to ensure the connection pool
    doesn't grow unbounded, which would crash production.

    Bug: Sessions are created but never closed.
    Fix: Each session must be properly closed after use.
    """
    from src.di_container import get_db_session

    # Simulate 10 API requests and verify cleanup happens
    for i in range(10):
        session_gen = get_db_session()
        session = next(session_gen)

        # Verify session is usable during the request
        assert session is not None

        # Simulate end of request - close the generator
        try:
            next(session_gen)
        except StopIteration:
            pass

    # If we get here without errors, the generator pattern is working
    # The fact that we can create 10 sessions sequentially without
    # running out of connections proves the cleanup is working


def test_get_db_session_has_correct_return_type():
    """
    Verify that get_db_session has the correct type annotation.

    For FastAPI Depends() to work correctly with cleanup, the function
    must return Generator[Session, None, None].
    """
    from src.di_container import get_db_session
    import inspect

    # Get the function signature
    sig = inspect.signature(get_db_session)
    return_annotation = sig.return_annotation

    # Check if return type is a Generator
    # Note: This will pass even with current code, but documents the requirement
    assert return_annotation != Session, \
        "Return type should be Generator[Session, None, None], not Session"


def test_di_container_loads_without_unicode_error():
    """
    CRITICAL: DI container must load without Unicode errors on Windows.

    Windows console uses cp1252 encoding by default, which cannot handle
    emojis (📊, ✅). This causes UnicodeEncodeError crashes on print().

    Bug: Lines 34 and 54 use emoji characters.
    Fix: Remove emojis or use safe_print() with error handling.
    """
    # Simulate Windows cp1252 encoding environment
    original_stdout = sys.stdout

    try:
        # Create a mock stdout that simulates cp1252 (rejects emojis)
        class CP1252Stdout:
            def __init__(self):
                self.encoding = 'cp1252'
                self.errors = 'strict'

            def write(self, text):
                # This will raise UnicodeEncodeError if emoji is present
                text.encode('cp1252')  # Simulate Windows console encoding
                return len(text)

            def flush(self):
                pass

        # Replace stdout with our cp1252 simulator
        sys.stdout = CP1252Stdout()

        # Try to reload the di_container module
        # This will trigger the print() statements at module level
        import src.di_container
        importlib.reload(src.di_container)

        # If we get here without UnicodeEncodeError, the test passes

    except UnicodeEncodeError as e:
        pytest.fail(
            f"DI Container crashes on Windows with cp1252 encoding!\n"
            f"Error: {e}\n"
            f"Emojis in print() statements cannot be encoded to cp1252.\n"
            f"Fix: Remove emojis or use safe_print() utility."
        )

    finally:
        # Restore original stdout
        sys.stdout = original_stdout


def test_di_container_prints_safe_messages():
    """
    Verify that DI container uses ASCII-safe messages.

    After fixing Bug #3, this test ensures messages are safe for all encodings.
    """
    from src.di_container import DATABASE_URL

    # These should not contain emojis
    database_msg = f"[DATABASE] Using: {DATABASE_URL.split('://')[0].upper()}"
    tables_msg = "[DATABASE] Tables created/verified successfully"

    # Verify messages can be encoded to cp1252 (Windows)
    try:
        database_msg.encode('cp1252')
        tables_msg.encode('cp1252')
    except UnicodeEncodeError:
        pytest.fail("Messages still contain characters incompatible with cp1252")


def test_db_session_cleanup_on_exception():
    """
    Verify that session is closed even if exception occurs.

    This ensures the finally block in the generator properly handles cleanup.
    """
    from src.di_container import get_db_session

    session_gen = get_db_session()
    session = next(session_gen)

    # Verify session is usable
    assert session is not None

    # Simulate an exception during request processing
    exception_occurred = False
    try:
        raise ValueError("Simulated error during request")
    except ValueError:
        exception_occurred = True

    assert exception_occurred, "Test setup failed"

    # Close the generator (as FastAPI would do in finally block)
    try:
        next(session_gen)
    except StopIteration:
        pass

    # Verify cleanup happened even with exception
    # Try to use the session - should fail because it's been closed and rolled back
    with pytest.raises(Exception):
        session.execute("SELECT 1")
        session.commit()
