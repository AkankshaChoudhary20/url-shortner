from app.utils.code_generator import ALPHABET, generate_short_code


def test_generate_short_code_default_length():
    code = generate_short_code()
    assert len(code) == 7


def test_generate_short_code_custom_length():
    code = generate_short_code(length=12)
    assert len(code) == 12


def test_generate_short_code_uses_expected_alphabet():
    code = generate_short_code(length=200)
    assert set(code).issubset(set(ALPHABET))


def test_generate_short_code_is_reasonably_unique():
    codes = {generate_short_code() for _ in range(2000)}
    # collisions are possible but should be extremely rare at this sample size
    assert len(codes) >= 1990
