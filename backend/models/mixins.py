from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import declared_attr

class TimestampMixin:
    """Mixin for tracking creation and modification timestamps."""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class ActiveFlagMixin:
    """Mixin for soft-enable/disable of lookup master values."""
    active = Column(Boolean, default=True, nullable=False)

class BaseLookupMixin(ActiveFlagMixin, TimestampMixin):
    """Mixin providing unified properties for master/lookup tables while adhering to custom column schemas."""
    
    sort_order = Column(Integer, default=0, nullable=False)

    @declared_attr
    def id(cls):
        # Allow class overrides for custom primary key naming, fallback to ClassNameID
        pk_name = getattr(cls, "__pk_name__", f"{cls.__name__}ID")
        return Column(pk_name, Integer, primary_key=True)

    @declared_attr
    def name(cls):
        # Allow class overrides for custom name column naming, fallback to ClassNameName
        name_col = getattr(cls, "__name_col__", f"{cls.__name__}Name")
        return Column(name_col, String(255), nullable=False)
