import chardet
import pandas as pd


def detect_encoding(file_path: str) -> str:
    with open(file_path, "rb") as f:
        raw = f.read(32768)
    result = chardet.detect(raw)
    return result.get("encoding") or "utf-8"


def detect_delimiter(file_path: str, encoding: str) -> str:
    with open(file_path, encoding=encoding, errors="replace") as f:
        sample = f.read(8192)
    candidates = {",": 0, ";": 0, "\t": 0, "|": 0}
    for delimiter in candidates:
        candidates[delimiter] = sample.count(delimiter)
    return max(candidates, key=lambda k: candidates[k])


def load_raw(file_path: str) -> pd.DataFrame:
    encoding = detect_encoding(file_path)
    delimiter = detect_delimiter(file_path, encoding)
    df = pd.read_csv(
        file_path,
        encoding=encoding,
        sep=delimiter,
        encoding_errors="replace",
        on_bad_lines="skip",
        dtype=str,
        skipinitialspace=True,
    )
    df.columns = [c.strip().lower() for c in df.columns]
    df = df[~df.apply(lambda r: r.astype(str).str.lower().eq(r.index.str.lower()).all(), axis=1)]
    df = df.reset_index(drop=True)
    return df


def save_clean(df: pd.DataFrame, output_path: str) -> None:
    df.to_csv(output_path, index=False, encoding="utf-8")
