import numpy as np


def _validate(values, levels):
    values = np.asarray(values, dtype=np.float64)
    if values.ndim != 2 or not values.size:
        raise ValueError("DWT потребує непорожнього двовимірного масиву")
    if not isinstance(levels, int) or levels < 1:
        raise ValueError("Кількість рівнів має бути додатним цілим числом")
    if any(size % (2 ** levels) for size in values.shape):
        raise ValueError("Розміри мають бути кратними 2 у степені кількості рівнів")
    return values.copy()


def forward_haar(image, levels=3):
    coefficients = _validate(image, levels)
    height, width = coefficients.shape
    normalization = np.sqrt(2.0)

    for level in range(levels):
        rows, columns = height >> level, width >> level
        region = coefficients[:rows, :columns].copy()
        horizontal = np.empty_like(region)
        horizontal[:, :columns // 2] = (
            region[:, 0::2] + region[:, 1::2]
        ) / normalization
        horizontal[:, columns // 2:] = (
            region[:, 0::2] - region[:, 1::2]
        ) / normalization
        coefficients[:rows // 2, :columns] = (
            horizontal[0::2] + horizontal[1::2]
        ) / normalization
        coefficients[rows // 2:rows, :columns] = (
            horizontal[0::2] - horizontal[1::2]
        ) / normalization

    return coefficients


def inverse_haar(coefficients, levels=3):
    restored = _validate(coefficients, levels)
    height, width = restored.shape
    normalization = np.sqrt(2.0)

    for level in reversed(range(levels)):
        rows, columns = height >> level, width >> level
        region = restored[:rows, :columns].copy()
        vertical = np.empty_like(region)
        vertical[0::2] = (
            region[:rows // 2] + region[rows // 2:]
        ) / normalization
        vertical[1::2] = (
            region[:rows // 2] - region[rows // 2:]
        ) / normalization
        restored[:rows, :columns:2] = (
            vertical[:, :columns // 2] + vertical[:, columns // 2:]
        ) / normalization
        restored[:rows, 1:columns:2] = (
            vertical[:, :columns // 2] - vertical[:, columns // 2:]
        ) / normalization

    return restored
