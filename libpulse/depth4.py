import numpy as np


def t1(angle, *, z=0):
    if (0 <= angle < np.pi / 2) or (np.pi <= angle < 3 * np.pi / 2):
        return (1 / 2) * np.arctan2(
            ((-1) ** z) * np.sqrt(np.sin(2 * angle)) / (np.cos(angle) + np.sin(angle)),
            1 / (np.cos(angle) + np.sin(angle)),
        )
    if (np.pi / 2 <= angle < np.pi) or (3 * np.pi / 2 <= angle < 2 * np.pi):
        return (1 / 2) * np.arctan2(
            -((-1) ** z) * (np.sqrt(-np.sin(2 * angle)) / (np.cos(angle) - np.sin(angle))),
            1 / (np.cos(angle) - np.sin(angle)),
        )


def t2(angle, *, z=0):
    if (0 <= angle < np.pi / 2) or (np.pi <= angle < 3 * np.pi / 2):
        return (1 / 2) * np.arctan2(
            -((-1) ** z) * np.sqrt(np.sin(2 * angle)), np.cos(angle) - np.sin(angle)
        )

    if (np.pi / 2 <= angle < np.pi) or (3 * np.pi / 2 <= angle < 2 * np.pi):
        return (1 / 2) * np.arctan2(
            -((-1) ** z) * np.sqrt(-np.sin(2 * angle)), np.cos(angle) + np.sin(angle)
        )
