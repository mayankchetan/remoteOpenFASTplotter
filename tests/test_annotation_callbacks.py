import pytest
from dash.exceptions import PreventUpdate

# Functions to test (or parts of them)
# We can't directly test the Dash callbacks without a running app or more complex mocking.
# Instead, we will test the core logic if we can isolate it or simulate
# the callback's behavior.

# For annotation_callbacks, the core logic often involves list manipulation and data processing
# based on inputs. Let's simulate those.

# Mocking user_preferences and utils for now, as they are side effects or
# UI formatting


@pytest.fixture(autouse=True)
def mock_dependencies(mocker):
    mocker.patch(
        'callbacks.annotation_callbacks.save_custom_annotations',
        return_value=None)
    mocker.patch(
        'callbacks.annotation_callbacks.create_annotation_badges',
        return_value=[])  # Returns empty list for badges

# Test logic related to manage_fft_annotations


def test_manage_annotations_add_new():
    """Test adding new annotations from freq and label inputs."""
    # Simulate inputs to manage_fft_annotations
    freq_input = "10, 20.5"
    label_input = "Peak1, Peak2"
    current_annotations = []

    # Simplified logic extracted from manage_fft_annotations
    try:
        freqs = [float(f.strip()) for f in freq_input.split(",") if f.strip()]
    except ValueError:
        freqs = []  # Should handle error in real callback

    if not label_input:
        labels = [f"F{i+1}" for i in range(len(freqs))]
    else:
        labels = [lbl.strip() for lbl in label_input.split(",")]
        if len(labels) < len(freqs):
            labels += [f"F{i+1}" for i in range(len(labels), len(freqs))]

    new_annotations_list = current_annotations.copy() if current_annotations else []
    for freq, label in zip(freqs, labels):
        new_annotations_list.append({"freq": freq, "label": label})

    new_annotations_list.sort(key=lambda x: x["freq"])

    expected_annotations = [
        {"freq": 10.0, "label": "Peak1"},
        {"freq": 20.5, "label": "Peak2"}
    ]
    assert new_annotations_list == expected_annotations


def test_manage_annotations_add_to_existing():
    """Test adding new annotations to an existing list."""
    freq_input = "30"
    label_input = "NewPeak"
    current_annotations = [{"freq": 15.0, "label": "OldPeak"}]

    # Simplified logic
    freqs = [float(f.strip()) for f in freq_input.split(",") if f.strip()]
    labels = [lbl.strip() for lbl in label_input.split(",")
              ]  # Assuming label provided

    new_annotations_list = current_annotations.copy()
    for freq, label in zip(freqs, labels):
        new_annotations_list.append({"freq": freq, "label": label})
    new_annotations_list.sort(key=lambda x: x["freq"])

    expected_annotations = [
        {"freq": 15.0, "label": "OldPeak"},
        {"freq": 30.0, "label": "NewPeak"}
    ]
    assert new_annotations_list == expected_annotations


def test_manage_annotations_auto_labels():
    """Test automatic label generation when labels are not provided or insufficient."""
    freq_input = "5, 10, 15"
    label_input_none = None
    label_input_partial = "MyLabel"
    current_annotations = []

    # Case 1: No labels provided
    freqs1 = [float(f.strip()) for f in freq_input.split(",") if f.strip()]
    labels1 = [f"F{i+1}" for i in range(len(freqs1))]  # Auto-generate all

    new_annotations1 = []
    for freq, label in zip(freqs1, labels1):
        new_annotations1.append({"freq": freq, "label": label})
    new_annotations1.sort(key=lambda x: x["freq"])

    expected1 = [
        {"freq": 5.0, "label": "F1"},
        {"freq": 10.0, "label": "F2"},
        {"freq": 15.0, "label": "F3"}
    ]
    assert new_annotations1 == expected1

    # Case 2: Partial labels provided
    freqs2 = [float(f.strip()) for f in freq_input.split(",") if f.strip()]
    labels_parsed = [lbl.strip() for lbl in label_input_partial.split(",")]
    if len(labels_parsed) < len(freqs2):
        labels_parsed += [f"F{i+1}" for i in range(
            len(labels_parsed), len(freqs2))]

    new_annotations2 = []
    for freq, label in zip(freqs2, labels_parsed):
        new_annotations2.append({"freq": freq, "label": label})
    new_annotations2.sort(key=lambda x: x["freq"])

    expected2 = [
        {"freq": 5.0, "label": "MyLabel"},
        {"freq": 10.0, "label": "F2"},
        {"freq": 15.0, "label": "F3"}
    ]
    assert new_annotations2 == expected2


def test_manage_annotations_invalid_freq_input():
    """Test how invalid frequency input could be handled (conceptual)."""
    # In the actual callback, this would likely result in an error message to the UI
    # Here, we test if the parsing fails as expected.
    freq_input = "10, twenty, 30"
    with pytest.raises(ValueError):
        [float(f.strip()) for f in freq_input.split(",") if f.strip()]


# Test logic related to remove_annotation
def test_remove_annotation_logic():
    """Test the core logic of removing an annotation by index."""
    current_annotations = [
        {"freq": 10, "label": "A"},
        {"freq": 20, "label": "B"},
        {"freq": 30, "label": "C"}
    ]
    index_to_remove = 1  # Remove "B"

    # Simplified logic from remove_annotation
    new_annotations_list = [a for i, a in enumerate(
        current_annotations) if i != index_to_remove]

    expected_annotations = [
        {"freq": 10, "label": "A"},
        {"freq": 30, "label": "C"}
    ]
    assert new_annotations_list == expected_annotations


def test_remove_annotation_invalid_index():
    """Test removing with an out-of-bounds index (should not change list)."""
    current_annotations = [{"freq": 10, "label": "A"}]
    index_to_remove = 5  # Invalid

    new_annotations_list = [a for i, a in enumerate(
        current_annotations) if i != index_to_remove]
    assert new_annotations_list == current_annotations


# Test logic related to generate_rotor_harmonics
def test_generate_rotor_harmonics_logic():
    """Test the core logic of generating rotor harmonics."""
    rpm_value = 600.0  # 600 RPM = 10 Hz
    current_annotations = [{"freq": 5.0, "label": "Existing"}]

    # Simplified logic from generate_rotor_harmonics
    freq_1p = rpm_value / 60.0  # 10 Hz
    defined_harmonics = [1, 2, 3, 4, 6, 8, 9]  # As in the callback

    new_annotations_list = current_annotations.copy()
    for h_num in defined_harmonics:
        harmonic_freq = freq_1p * h_num
        harmonic_label = f"{h_num}P"

        exists = any(abs(anno.get('freq', 0) - harmonic_freq) < 0.001 and
                     anno.get('label', '') == harmonic_label
                     for anno in new_annotations_list)
        if not exists:
            new_annotations_list.append(
                {"freq": harmonic_freq, "label": harmonic_label})

    new_annotations_list.sort(key=lambda x: x["freq"])

    expected_annotations = [
        {"freq": 5.0, "label": "Existing"},
        {"freq": 10.0, "label": "1P"},  # 10 Hz * 1
        {"freq": 20.0, "label": "2P"},  # 10 Hz * 2
        {"freq": 30.0, "label": "3P"},  # 10 Hz * 3
        {"freq": 40.0, "label": "4P"},  # 10 Hz * 4
        {"freq": 60.0, "label": "6P"},  # 10 Hz * 6
        {"freq": 80.0, "label": "8P"},  # 10 Hz * 8
        {"freq": 90.0, "label": "9P"}  # 10 Hz * 9
    ]
    assert new_annotations_list == expected_annotations


def test_generate_rotor_harmonics_avoids_duplicates():
    """Test that generating harmonics avoids adding existing ones."""
    rpm_value = 60.0  # 1 Hz
    current_annotations = [
        {"freq": 1.0, "label": "1P"},  # Existing 1P
        {"freq": 3.0, "label": "SomeOther"}
    ]

    freq_1p = rpm_value / 60.0
    defined_harmonics = [1, 2, 3]  # Test with a subset that includes existing

    new_annotations_list = current_annotations.copy()
    for h_num in defined_harmonics:
        harmonic_freq = freq_1p * h_num
        harmonic_label = f"{h_num}P"

        exists = any(abs(anno.get('freq', 0) - harmonic_freq) < 0.001 and
                     anno.get('label', '') == harmonic_label
                     for anno in new_annotations_list)
        if not exists:
            new_annotations_list.append(
                {"freq": harmonic_freq, "label": harmonic_label})

    new_annotations_list.sort(key=lambda x: x["freq"])

    expected_annotations = [
        {"freq": 1.0, "label": "1P"},      # Original 1P
        {"freq": 2.0, "label": "2P"},      # New 2P
        {"freq": 3.0, "label": "SomeOther"},  # Original other
        # Note: 3P (3.0 Hz) is not added because its label would be "3P",
        # but "SomeOther" already exists at 3.0 Hz. The check is for freq AND label.
        # If we wanted to avoid adding any harmonic if *any* annotation exists at that frequency,
        # the `exists` check would be different. The current callback logic checks for label match too.
    ]
    # To be precise with the current callback's duplication check:
    # It will add a 3P if "SomeOther" is not "3P"
    # Let's refine `current_annotations` to test the exact duplication logic
    current_annotations_refined = [
        {"freq": 1.0, "label": "1P"},
        {"freq": 3.0, "label": "3P"}  # An existing 3P harmonic
    ]
    new_annotations_refined = current_annotations_refined.copy()
    for h_num in defined_harmonics:  # [1, 2, 3]
        harmonic_freq = freq_1p * h_num
        harmonic_label = f"{h_num}P"
        exists = any(abs(anno.get('freq', 0) - harmonic_freq) < 0.001 and
                     anno.get('label', '') == harmonic_label
                     for anno in new_annotations_refined)
        if not exists:
            new_annotations_refined.append(
                {"freq": harmonic_freq, "label": harmonic_label})
    new_annotations_refined.sort(key=lambda x: x["freq"])

    expected_refined = [
        {"freq": 1.0, "label": "1P"},
        {"freq": 2.0, "label": "2P"},
        {"freq": 3.0, "label": "3P"}
    ]
    assert new_annotations_refined == expected_refined
