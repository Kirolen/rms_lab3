import numpy as np


def calculate_psnr(original, restored):
    original = np.asarray(original, dtype=np.float64)
    restored = np.asarray(restored, dtype=np.float64)
    if original.shape != restored.shape or not original.size:
        raise ValueError("Для PSNR потрібні непорожні зображення однакового розміру")
    mse = np.mean((original - restored) ** 2)
    if mse == 0:
        return float("inf")
    return float(10 * np.log10(255.0 ** 2 / mse))
