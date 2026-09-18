import random


def show_df(df, max_rows=6, *, index=True, dtypes=None):
    """Preview a dataframe with head/tail rows and a second header row of dtypes.

    Import with ``from utils import show_df`` in any chapter. For an R dataframe
    or tibble, call ``show_df(r.my_dataframe)`` in a Python chunk; reticulate
    converts it to pandas automatically. Dtypes describe that pandas representation
    unless explicit labels are passed in ``dtypes``. The wrapper in utils.R supplies
    the original R type labels from pillar instead.

    The default shows three first and three last rows, separated by an ellipsis
    when needed. Use ``max_rows=None`` to show all rows or ``index=False`` to hide
    row labels. Neither the input dataframe nor global pandas settings are changed.
    """
    import pandas as pd
    from IPython.display import HTML

    if max_rows is not None and (not isinstance(max_rows, int) or max_rows < 1):
        raise ValueError('max_rows must be a positive integer or None.')
    if dtypes is not None and len(dtypes) != len(df.columns):
        raise ValueError('dtypes must contain one label for each dataframe column.')

    preview = df.copy(deep=False)
    headers = [df.columns.get_level_values(level) for level in range(df.columns.nlevels)]
    header_types = df.dtypes.astype(str) if dtypes is None else dtypes
    preview.columns = pd.MultiIndex.from_arrays([*headers, header_types])
    return HTML(preview.to_html(
        max_rows=max_rows,
        index=index,
        index_names=False,
        sparsify=False,
        classes='dataframe-preview',
        show_dimensions=max_rows is not None and len(df) > max_rows,
    ))


def assert_chart_equal(expected, actual):
    expected_dict = expected.to_dict()
    actual_dict = actual.to_dict()
    try:
        assert_dict_equal(expected_dict, actual_dict)
        message = random.choice(['Nicely done', 'Great', 'Good job', 'Well done'])
        emoji = random.choice(['🍀', '🎉', '🌈', '🙌', '🚀', '🌟', '✨', '💯'])
        return {"correct": True, "message": f'{message}! {emoji}'}
    except AssertionError as e:
        return {"correct": False, "message": str(e)}


def assert_dict_equal(expected_dict, actual_dict, path=""):
    # Check all keys in dict1
    for key in expected_dict:
        if key not in actual_dict:
            raise AssertionError(
                f"Key mismatch: '{path + key}' was expected, but not found."
            )
        else:
            # If both values are dictionaries, recurse into them
            if isinstance(expected_dict[key], dict) and isinstance(
                actual_dict[key], dict
            ):
                assert_dict_equal(
                    expected_dict[key], actual_dict[key], path + key + "."
                )
            # Compare the values
            elif expected_dict[key] != actual_dict[key]:
                raise AssertionError(
                    f"Value mismatch at '{path + key}': {expected_dict[key]} != {actual_dict[key]}"
                )

    # Check for any extra keys in dict2
    for key in actual_dict:
        if key not in expected_dict:
            raise AssertionError(f"Key mismatch: '{path + key}' was unexpected.")
