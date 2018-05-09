# book.json created from this URL:
# https://openlibrary.org/api/books?bibkeys=ISBN:9780201896831&format=json&jscmd=data

import os

import related

from specd.utils import file_path_to_dict
from specd.walker import generate_definitions, generate_for_array, Definition


def test_generate_for_array():
    publishers = [{"name": "Addison-Wesley"}]
    dfn = list(generate_for_array("Book", "publishers", publishers))
    expected_props = {"name": {"format": "char", "type": "string"}}
    assert dfn == [Definition("BookPublisher", expected_props)]


def test_generate_for_array_complex():
    ebooks = [
        {
            "formats": {
                "mobi": [{"site": "one"}, {"another": 2, "site": "two"}]
            },
            "availability": "restricted",
        }
    ]

    dfn = related.to_dict(list(generate_for_array("Book", "ebooks", ebooks)))
    assert (
        dfn
        == [
            {
                "name": "BookEbookFormatMobi",
                "properties": {
                    "another": {"format": "int64", "type": "integer"},
                    "site": {"format": "char", "type": "string"},
                },
            },
            {
                "name": "BookEbookFormat",
                "properties": {
                    "mobi": {
                        "items": {"$ref": "#/definitions/BookEbookFormatMobi"},
                        "type": "array",
                    }
                },
            },
            {
                "name": "BookEbook",
                "properties": {
                    "availability": {"format": "char", "type": "string"},
                    "formats": {
                        "$ref": "#/definitions/BookEbookFormat",
                        "type": "object",
                    },
                },
            },
        ]
    )


def test_generate_properties():
    input_file = os.path.join(os.path.dirname(__file__), "book.json")
    book_dict = file_path_to_dict(input_file)
    assert len(book_dict) == 16

    definitions = list(generate_definitions("Book", book_dict))
    name_count_set = {(d.name, len(d.properties)) for d in definitions}
    assert (
        name_count_set
        == {
            ("Book", 16),
            ("BookAuthor", 2),
            ("BookClassification", 2),
            ("BookCover", 3),
            ("BookEbook", 3),
            ("BookEbookFormat", 0),
            ("BookIdentifier", 6),
            ("BookPublishPlace", 1),
            ("BookPublisher", 1),
            ("BookSubject", 2),
            ("BookTableOfContent", 4),
        }
    )
