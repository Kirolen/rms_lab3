from dataclasses import dataclass

import numpy as np

from processing.compression import retain_largest
from processing.dct import forward_dct, inverse_dct
from processing.dwt import forward_haar, inverse_haar
from processing.metrics import calculate_psnr


@dataclass(frozen=True)
class ExperimentResult:
    method: str
    percent: int
    nonzero: int
    total: int
    psnr: float


def run_experiments(original, percentages=(50, 10, 1)):
    results = []
    for name, forward, inverse in (
        ("DCT", forward_dct, inverse_dct),
        ("DWT", forward_haar, inverse_haar),
    ):
        coefficients = forward(original)
        for percent in percentages:
            filtered = retain_largest(coefficients, percent)
            restored = np.clip(np.rint(inverse(filtered)), 0, 255)
            results.append(ExperimentResult(
                name, percent, int(np.count_nonzero(filtered)),
                filtered.size, calculate_psnr(original, restored),
            ))
    return results
