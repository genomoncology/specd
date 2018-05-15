import pytest
import os
from specd.sdk import create_sdk


@pytest.fixture()
def sdk():
    specd_path = os.path.join(os.path.dirname(__file__), "specs")
    sdk = create_sdk(specd_path)
    return sdk


def test_get_annotations_resource(sdk):
    assert sdk.pets
    assert sdk.pets.listPets


def test_set_headers(sdk):
    token = "Token 0123456789ABCDEF"
    sdk.set_headers(Authorization=token)
    assert sdk.pets.listPets.headers == dict(Authorization=token)

    op_kwargs = {}
    sdk.pets.listPets.update_headers(op_kwargs)
    assert (
        op_kwargs
        == {"_request_options": {"headers": {"Authorization": token}}}
    )


def test_definitions(sdk):
    assert sdk.definitions.Pet == sdk.definitions["Pet"]

    with pytest.raises(KeyError):
        assert sdk.definitions["MadeUpName"] == sdk.definitions.MadeUpName


def test_model_instantiate(sdk):
    pet = sdk.instantiate(sdk.definitions.Pet, RESPONSE)
    assert pet.id == 898988944
    assert pet.name == "doggie"


def test_override_models_module(sdk):
    from . import pet_models

    sdk.add_models(pet_models)

    pet = sdk.instantiate(sdk.definitions.Pet, RESPONSE)
    assert isinstance(pet, pet_models.Pet)
    assert pet.speak() == "woof"


def test_override_models_class(sdk):
    from .pet_models import Pet

    sdk.add_models(Pet)

    pet = sdk.instantiate(sdk.definitions.Pet, RESPONSE)
    assert isinstance(pet, Pet)
    assert pet.speak() == "woof"


def test_override_models_dict(sdk):
    from .pet_models import Pet

    sdk.add_models(dict(Pet=Pet))

    pet = sdk.instantiate(sdk.definitions.Pet, RESPONSE)
    assert isinstance(pet, Pet)
    assert pet.speak() == "woof"


def test_clone(sdk):
    from .pet_models import Pet

    sdk.add_models(dict(Pet=Pet))
    pet = sdk.instantiate("Pet", RESPONSE)
    clone = pet.clone(name="doggie 2")
    assert clone.speak() == "hello"
    assert clone.id == 898988944
    assert clone.status == "available"


RESPONSE = {
    "id": 898988944,
    "category": {"id": 0, "name": "string"},
    "name": "doggie",
    "photoUrls": ["string"],
    "tags": [{"id": 0, "name": "string"}],
    "status": "available",
}
