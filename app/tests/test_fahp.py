import pytest
import numpy as np
from app.services.methods.fuzzy_ahp import FuzzyAHP
from app.services.methods.fuzzy_ahp import TriangularFuzzyNumber
from app.services.utils.matrices import MatrixHelper


def test_defuzzification():
    test_cases = [
        # (l, m, u), expected using (l + 2*m + u) / 4
        ((1, 1, 1), 1.0),  # Crisp
        ((0, 0.5, 1), 0.5),  # Symmetric triangle: (0 + 2*0.5 + 1)/4 = 0.5
        ((0, 1, 1), 0.75),  # (0 + 2*1 + 1)/4 = 0.75
        ((0, 0, 1), 0.25)   # (0 + 0 + 1)/4 = 0.25
    ]

    for (l, m, u), expected in test_cases:
        tfn = TriangularFuzzyNumber(l, m, u)
        assert abs(tfn.defuzzify() - expected) < 1e-9


def test_consistency_check_valid():
    # Matrix is consistent
    valid_matrix = [[1, 2, 5],
                    [1/2, 1, 3],
                    [1/5, 1/3, 1]]
    cr = MatrixHelper.calculate_consistency_ratio(valid_matrix)
    assert cr < 0.1


def test_consistency_check_invalid():
    # Highly inconsistent matrix
    invalid_matrix = [[1, 9, 9],
                      [1/9, 1, 0.1],
                      [1/9, 10, 1]]
    cr = MatrixHelper.calculate_consistency_ratio(invalid_matrix)
    assert cr > 0.1


def test_edge_case_same_scores():
    # All scores identical - should produce identity matrix
    scores = [5, 5, 5]
    matrix = MatrixHelper._build_matrix_from_importances(scores)
    expected = np.ones((3, 3))
    assert np.allclose(matrix, expected)


def test_edge_case_two_criteria_weights():
    # Testing FAHP with two criteria
    fahp = FuzzyAHP()

    # Fuzzy 2x2 matrix
    tfn_matrix = [
        [TriangularFuzzyNumber(1, 1, 1), TriangularFuzzyNumber.from_crisp(0.5)],
        [TriangularFuzzyNumber.from_crisp(2), TriangularFuzzyNumber(1, 1, 1)]
    ]

    weights = fahp._calculate_weights(tfn_matrix)
    assert pytest.approx(sum(weights), abs=1e-6) == 1.0
    assert all(0 <= w <= 1 for w in weights)


# def test_full_fahp_flow():
#     # Test data preparation
#     criteria = [("Quality", 8), ("Price", 6), ("Safety", 9)]
#     alternatives = [("Product A", 7), ("Product B", 4), ("Product C", 9)]
#
#     # Simulating system workflow
#     fahp = FuzzyAHP()
#     criteria_matrix = MatrixHelper._build_matrix_from_importances([v for _, v in criteria])
#     fuzzy_matrix = fahp._build_fuzzy_matrix(criteria_matrix)
#     weights = fahp._calculate_weights(fuzzy_matrix)
#
#     # Verifying results
#     assert sum(weights) == pytest.approx(1.0, rel=1e-3)
#     assert weights[2] > weights[0] > weights[1]  # Safety > Quality > Price


def test_specific_comparison_matrix():
    # Matrix from step 2
    matrix = [
        [1.00, 1.00, 3.00, 0.33, 5.00],
        [1.00, 1.00, 3.00, 0.33, 5.00],
        [1/3, 1/3, 1.00, 0.20, 3.00],
        [3.00, 3.00, 5.00, 1.00, 9.00],
        [0.20, 0.20, 1/3, 1/9, 1.00]
    ]

    expected_weights = [0.213961196, 0.213961196, 0.137561109, 0.345800069, 0.088716431]

    fahp = FuzzyAHP()
    fuzzy_matrix = fahp._build_fuzzy_matrix(matrix)
    weights = fahp._calculate_weights(fuzzy_matrix)

    # Print percentages for readability
    print("\nCalculated criterion weights (%):")
    for i, w in enumerate(weights):
        print(f"C{i+1}: {w*100:.2f}%")

    # Verify ranking matches expected (compare sorted indices)
    expected_order = sorted(range(len(expected_weights)), key=lambda i: expected_weights[i], reverse=True)
    actual_order = sorted(range(len(weights)), key=lambda i: weights[i], reverse=True)

    print("\nExpected ranking (descending importance):", expected_order)
    print("Actual ranking:", actual_order)

    assert actual_order == expected_order, "Criterion ranking doesn't match expected"