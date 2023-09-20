#!/usr/bin/python3

import os
import random

import pprint
import json
import pytest
from risuspubl.dbmodels import Author

from conftest import Genius, DbBasedTester


# Set environment variable for Flask's configuration
os.environ["FLASK_ENV"] = "testing"
# This should be set before creating the app instance.


# def test_delete_author_book_endpoint # 7/83

# def test_delete_author_by_id_endpoint # 8/83

# def test_delete_author_manuscript_endpoint # 9/83

# def test_delete_author_metadata_endpoint # 10/83

# def test_delete_authors_book_endpoint # 11/83

# def test_delete_authors_manuscript_endpoint # 12/83

