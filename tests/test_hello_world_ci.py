from features.hello_world_ci.logic import hello_world_ci


def test_hello_world_ci():
    assert hello_world_ci() == "Hello CI/CD!"
