import numpy as np


def retain_largest(coefficients, percent):
    if not 0 < percent <= 100:
        raise ValueError("Частка коефіцієнтів має бути від 0 до 100%")
    values = np.asarray(coefficients, dtype=np.float64)
    count = max(1, int(np.ceil(values.size * percent / 100)))
    if count == values.size:
        return values.copy()
    flat = values.ravel()
    selected = np.argpartition(np.abs(flat), flat.size - count)[-count:]
    result = np.zeros_like(flat)
    result[selected] = flat[selected]
    return result.reshape(values.shape)
