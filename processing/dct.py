import numpy as np


BLOCK_SIZE = 8


def create_dct_matrix(size=BLOCK_SIZE):
    frequencies = np.arange(size)[:, None]
    samples = np.arange(size)[None, :]
    matrix = np.sqrt(2 / size) * np.cos(
        np.pi * (2 * samples + 1) * frequencies / (2 * size)
    )
    matrix[0] = 1 / np.sqrt(size)
    return matrix


DCT_MATRIX = create_dct_matrix()


def _to_blocks(values):
    values = np.asarray(values, dtype=np.float64)
    if values.ndim != 2 or not values.size:
        raise ValueError("DCT потребує непорожнього двовимірного масиву")
    height, width = values.shape
    if height % BLOCK_SIZE or width % BLOCK_SIZE:
        raise ValueError("Розміри зображення мають бути кратними 8")
    return values.reshape(
        height // BLOCK_SIZE, BLOCK_SIZE,
        width // BLOCK_SIZE, BLOCK_SIZE,
    ).transpose(0, 2, 1, 3)


def _from_blocks(blocks):
    rows, columns = blocks.shape[:2]
    return blocks.transpose(0, 2, 1, 3).reshape(
        rows * BLOCK_SIZE, columns * BLOCK_SIZE,
    )


def forward_dct(image):
    blocks = _to_blocks(image) - 128.0
    coefficients = DCT_MATRIX @ blocks @ DCT_MATRIX.T
    return _from_blocks(coefficients)


def inverse_dct(coefficients):
    blocks = _to_blocks(coefficients)
    restored = DCT_MATRIX.T @ blocks @ DCT_MATRIX + 128.0
    return _from_blocks(restored)
