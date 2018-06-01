import os

import pytest

from specd.sdk import create_sdk


@pytest.fixture()
def specd_path():
    return os.path.join(os.path.dirname(__file__), "specs")


@pytest.fixture()
def sdk(specd_path):
    sdk = create_sdk(specd_path, verify_ssl=False)
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
    assert op_kwargs == {
        "_request_options": {"headers": {"Authorization": token}}
    }


def test_definitions(sdk):
    assert sdk.definitions.Pet == sdk.definitions["Pet"]

    with pytest.raises(KeyError):
        assert sdk.definitions["MadeUpName"] == sdk.definitions.MadeUpName


def test_model_instantiate(sdk):
    pet = sdk.instantiate(sdk.definitions.Pet, RESPONSE)
    assert pet.id == 898988944
    assert pet.name == "doggie"


def test_override_models_module(specd_path):
    from . import pet_models

    sdk = create_sdk(specd_path, models=pet_models)

    pet = sdk.instantiate(sdk.definitions.Pet, RESPONSE)
    assert isinstance(pet, pet_models.Pet)
    assert pet.speak() == "woof"


def test_override_models_class(specd_path):
    from .pet_models import Pet

    sdk = create_sdk(specd_path, models=[Pet])

    pet = sdk.instantiate(sdk.definitions.Pet, RESPONSE)
    assert isinstance(pet, Pet)
    assert pet.speak() == "woof"


def test_override_models_dict(specd_path):
    from .pet_models import Pet

    sdk = create_sdk(specd_path, models=dict(Pet=Pet))

    pet = sdk.instantiate(sdk.definitions.Pet, RESPONSE)
    assert isinstance(pet, Pet)
    assert pet.speak() == "woof"


def test_clone(specd_path):
    from .pet_models import Pet

    sdk = create_sdk(specd_path, models=Pet)

    pet = sdk.instantiate("Pet", RESPONSE)
    clone = pet.clone(name="doggie 2")
    assert clone.speak() == "hello"
    assert clone.id == 898988944
    assert clone.status == "available"


@pytest.mark.asyncio
async def test_async_sdk(specd_path, socket_enabled):
    from .pet_models import Pet

    sdk = create_sdk(
        specd_path, verify_ssl=False, async_enabled=True, models=Pet
    )
    assert sdk.pets
    assert sdk.pets.listPets

    pet = sdk.instantiate(sdk.definitions.Pet, RESPONSE)
    assert isinstance(pet, Pet)
    assert pet.speak() == "woof"

    token = "Token 0123456789ABCDEF"
    sdk.set_headers(Authorization=token)
    assert sdk.pets.listPets.headers == dict(Authorization=token)

    op_kwargs = {}
    sdk.pets.listPets.update_headers(op_kwargs)
    assert op_kwargs == {
        "_request_options": {"headers": {"Authorization": token}}
    }

    await sdk.close()


RESPONSE = {
    "id": 898988944,
    "category": {"id": 0, "name": "string"},
    "name": "doggie",
    "photoUrls": ["string"],
    "tags": [{"id": 0, "name": "string"}],
    "status": "available",
}
