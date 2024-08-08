from awk_plus_plus.cli import where
import pandas as pd

def test_read_file():
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    df.to_csv("/tmp/x.csv", index=False)
    result = where("true", "/tmp/x.csv")
    assert (df == result).all().all()
