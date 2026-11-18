"""Test check thưởng; không sửa bộ tests/ của đề."""
from pathlib import Path
import pytest
from PIL import Image
from pipeline.common import Dataset
from pipeline.checks.aspect_ratio import run


def dataset(tmp_path, text):
    (tmp_path / 'images').mkdir()
    (tmp_path / 'labels').mkdir()
    Image.new('RGB', (1000, 100)).save(tmp_path / 'images/a.JPG')
    (tmp_path / 'labels/a.txt').write_text(text)
    return Dataset(tmp_path, ['car', 'person', 'truck', 'bus'])


def test_pixel_ratio_not_normalized_ratio(tmp_path):
    ds = dataset(tmp_path, '0 .5 .5 .8 .4\n')
    got = run(ds, {'aspect_ratio': {'max_ratio': 15}})
    assert len(got) == 1 and got[0].extra['ratio'] == 20 and got[0].severity == 'warn'


def test_bad_lines_and_original_number(tmp_path):
    ds = dataset(tmp_path, 'garbage\n\n93 .5 .5 .8 .4\n0 .5 .5 0 .4\n0 .5 .5 .8 .4\n')
    assert [i.line for i in run(ds, {'aspect_ratio': {'max_ratio': 15}})] == [5]


def test_threshold_and_no_mutation(tmp_path):
    ds = dataset(tmp_path, '0 .5 .5 .8 .4\n')
    before = ds.label_path('a').read_bytes()
    assert run(ds, {'aspect_ratio': {'max_ratio': 20}}) == []
    assert ds.label_path('a').read_bytes() == before


def test_invalid_threshold(tmp_path):
    with pytest.raises(ValueError):
        run(dataset(tmp_path, ''), {'aspect_ratio': {'max_ratio': 1}})
