try:
    assert 1 == 0
except Exception as ex:
    print(type(ex) is AssertionError)