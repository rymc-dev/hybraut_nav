# """
# specifies the order of tests to be run
# """

# TODO: Need to figure out how to order tests

# # conftest.py
# def pytest_collection_modifyitems(items):
#     # Split the tests into unit and integration tests
#     unit_tests = []
#     integration_tests = []

#     for item in items:
#         if 'unit_tests' in item.fspath.parts:  # Checks if the test is in the unit_tests directory
#             unit_tests.append(item)
#         else:
#             integration_tests.append(item)

#     # Clear the items and add unit tests first, followed by integration tests
#     items[:] = unit_tests + integration_tests