"""Constitution IV: sort é string de 8 caracteres, nunca inteiro. Zeros à esquerda significativos."""


def test_sort_is_eight_char_string(places):
    for p in places:
        for sort in p["verses"]:
            assert isinstance(sort, str), f"{p['place_id']}: sort não é string: {sort!r}"
            assert len(sort) == 8, f"{p['place_id']}: sort com tamanho errado: {sort!r}"


def test_place_id_and_candidate_ids_are_strings(places):
    for p in places:
        assert isinstance(p["place_id"], str)
        for c in p["candidates"]:
            assert isinstance(c["modern_id"], str)
