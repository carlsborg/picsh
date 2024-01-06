import pytest
from picsh.models.root_model import RootModel

def test_root_model():
    some_ref = ["aaa", "bbb"]
    root_model = RootModel(cluster_spec_paths=some_ref)
    root_model.state_change_listener({"cluster_spec_paths": ["zzz"]})
    assert some_ref == ["zzz"]
    assert root_model.cluster_spec_paths == ["zzz"]

    with pytest.raises(Exception):
        root_model.state_change_listener({"foo": "bar"})

if __name__ == "__main__":
    test_root_model()

