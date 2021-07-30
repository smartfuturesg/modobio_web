# Testing

## Requirements

- pytest
- pytest-cov

## Run tests

From this directory or the root directory, run:

```shell
$ pytest
```

To also see a coverage report after testing, run:

```shell
$ pytest --cov odyssey
```

## Layout

- `conftest.py` creates a fixture called `test_client`. This fixture is the `Flask.app.test_client()` that can be used to call the API. It also contains data that is used by **ALL** tests, loaded as parameters into `test_client`:

    - `test_client.db`: the database handle set up for testing. Do **not** use `from odyssey import db`.
    - `test_client.client`: a client `User` instance loaded from the database.
    - `test_client.client_id`: shortcut for `test_client.client.user_id`.
    - `test_client.client_pass`: password for client.
    - `test_client.client_auth_header`: authentication header with token for client.
    - `test_client.staff`: a staff `User` instance loaded from the database.
    - `test_client.staff_id`: shortcut for `test_client.staff.user_id`.
    - `test_client.staff_pass`: password for staff.
    - `test_client.staff_auth_header`: authentication header with token for staff.

	The name `test_client` is a bit unfortunate, because we use "client" to describe a type of user. Here, `test_client` is not the client who is used for testing, but rather a client in the sense of server <-> client. `test_client.client`, however, is the main client user for testing.

- Fixtures specific to only a subset of tests are located in `conftest.py` in their respective subdirectories (e.g. `functional/telehealth/conftest.py`).

- Fixtures that apply only to tests in a single file, (e.g. `functional/doctor/0030_external_medical_record_id_test.py`) are located in that file.

- The main setup of testing loads `database/*.sql` files by calling the `sql_scriptrunner.py` script. This ensures that the database setup is exactly the same during testing as it is during development and production running.

- When loading the sql files, a set of seed users is loaded into the database. During setup, 1 client and 1 staff user are preloaded, and are available as `test_client.client` and `test_client.staff`.

- If extra user data is needed for tests to work, it should be loaded in a fixture specific to that test (or collection of tests). For example, in `tests/functional/doctor/0030_external_medical_record_id_test.py` medical institutions are added with a fixture. Medical institutions are not needed outside of these tests.

- The layout of the tests follows the layout of the API source directory. Within each subdirectory, test files are named `0000_some_name_test.py`. The filename must end with `_test.py` for it to be picked up by pytest. Tests are loaded by pytest in lexicographical order. The first 4 digits allow tests to be run in a specific order. Ordering is only within a subdirectory, it is currently not possible to sort files on a higher level (e.g. have `system/` tests be run before `client/` tests).

- Data used by tests, especially data send to the API as JSON in POST or PUT requests, is stored in a file called `data.py` in the same subdirectory as the tests.

- Utility functions used by tests are located in `tests/utils.py`.

### More on test fixtures

A fixture is a function that is "requested" by a test. A fixture request is the parameter to a test definition:

```python
def test_something(request_fixture, request_another_fixture):
    pass
```

When the test is loaded, the fixture function is called (once or more, depending on scope), and replaced with the returned result. So, while it is a function, within the test definition it can be treated as an object.


Fixtures can be inherited. For example, the fixture `care_team` in `functional/client/0070_client_clinical_care_team_test.py` inherits `test_client`, which means that all functionality from test_client is available in care_team.
