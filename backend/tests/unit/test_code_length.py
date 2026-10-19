import pytest
from app.utils.code_generator import generate_short_code

@pytest.mark.parametrize('length', [0, -1, True, False, 1.5, '7', None])
def test_invalid_length_cannot_create_empty_or_invalid_codes(length):
    with pytest.raises(ValueError, match='positive integer'):
        generate_short_code(length)

@pytest.mark.parametrize('length', [1, 7, 200])
def test_positive_lengths_remain_supported(length):
    assert len(generate_short_code(length)) == length
