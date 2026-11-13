from typing import Optional, Union

import pytest
from pydantic import BaseModel, ConfigDict, Field

from lib.pydantic_scheme_extractor import SchemeExtractor


class OrderDetail(BaseModel):
    """A composite-key SQL table: no `id` field, so the table is declared on the class."""
    model_config = ConfigDict(populate_by_name=True, json_schema_extra={"table": "Order Details"})
    OrderID: Union[int, str] = Field(default=None, json_schema_extra={"table": "Orders"})
    ProductID: Union[int, str] = Field(default=None, json_schema_extra={"table": "Products"})
    Quantity: Optional[int] = None


class User(BaseModel):
    """A model generated before the class-level table existed: the table rides on the `_id` field."""
    model_config = ConfigDict(populate_by_name=True)
    id: Optional[str] = Field(default=None, alias="_id", json_schema_extra={"table": "users"})
    name: Optional[str] = None


class Untabled(BaseModel):
    name: Optional[str] = None


def test_table_comes_from_the_class_declaration():
    assert SchemeExtractor.extract_class_scheme(OrderDetail)["table"] == "Order Details"


def test_foreign_keys_are_still_references():
    assert SchemeExtractor.extract_class_scheme(OrderDetail)["references"] == {
        "OrderID": {"table": "Orders", "is_array": False},
        "ProductID": {"table": "Products", "is_array": False},
    }


def test_models_generated_before_the_class_table_use_the_id_field():
    assert SchemeExtractor.extract_class_scheme(User)["table"] == "users"


def test_a_model_without_a_table_names_itself_in_the_error():
    with pytest.raises(ValueError, match="Untabled"):
        SchemeExtractor.extract_class_scheme(Untabled)
