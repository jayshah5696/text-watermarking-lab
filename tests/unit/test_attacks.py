from watermark_lab.attacks import (
    HOMOGLYPHS,
    delete_words,
    mix_with_control,
    normalize_text,
    substitute_homoglyphs,
)


def test_normalization_applies_the_complete_recipe() -> None:
    source = "  A\u00a0\u2018test\u2019 \u2014  \uff21  "
    result = normalize_text(source)
    assert result.text == "A 'test' - A"
    assert result.operations[0].source == source


def test_homoglyph_selection_is_deterministic_and_auditable() -> None:
    first = substitute_homoglyphs("A pale cat crosses a road", rate=0.2, seed=17)
    second = substitute_homoglyphs("A pale cat crosses a road", rate=0.2, seed=17)
    assert first == second
    assert first.text != "A pale cat crosses a road"
    assert all(
        operation.replacement == HOMOGLYPHS[operation.source] for operation in first.operations
    )
    assert tuple(operation.index for operation in first.operations) == tuple(
        sorted(operation.index for operation in first.operations)
    )


def test_deletion_removes_exact_rounded_word_count() -> None:
    result = delete_words("zero one two three four five six seven eight nine", rate=0.3, seed=4)
    assert len(result.operations) == 3
    assert len(result.text.split()) == 7
    assert not set(operation.source for operation in result.operations) & set(result.text.split())


def test_mixing_replaces_aligned_words_and_keeps_marked_tail() -> None:
    result = mix_with_control(
        "a b c d marked tail",
        "w x y z",
        rate=0.5,
        seed=8,
    )
    assert len(result.operations) == 2
    assert result.text.endswith("marked tail")
    output = result.text.split()
    for operation in result.operations:
        assert output[operation.index] == operation.replacement


def test_attack_validation_rejects_empty_text_and_bad_rates() -> None:
    for call in (
        lambda: normalize_text(""),
        lambda: substitute_homoglyphs("x", rate=0, seed=1),
        lambda: delete_words("", rate=0.2, seed=1),
        lambda: mix_with_control("x", "", rate=0.2, seed=1),
    ):
        try:
            call()
        except ValueError:
            pass
        else:
            raise AssertionError("invalid attack input was accepted")
