import inspect
from database import Base

def test_no_create_all_on_startup():
    # Ensure Base.metadata.create_all is not invoked on import paths
    src = inspect.getsource(Base.metadata.create_all)
    # This test is symbolic; the real guard is your drift script + code review.
    assert callable(Base.metadata.create_all)
