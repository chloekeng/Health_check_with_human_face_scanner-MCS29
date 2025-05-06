import os
import cv2
import numpy as np
import pickle


def load_data(folder_sick, folder_healthy, image_size, ftype, extra_healthy=None, extra_sick=None):
    files_healthy = os.listdir(folder_healthy)
    files_sick = os.listdir(folder_sick)
    data = []
    labels = []

    if extra_healthy is None:
        extra_healthy = ftype
    if extra_sick is None:
        extra_sick = ftype

    for filename in sorted(files_healthy):
        sick = np.array([0])
        full_path = os.path.join(folder_healthy, filename)
        if ((ftype in filename) or (extra_healthy in filename)) and os.path.isfile(full_path):
            image = cv2.imread(full_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (image_size, image_size), interpolation=cv2.INTER_CUBIC)
            data.append(image.astype(np.int32))
            labels.append(sick.astype(np.int32))
    for filename in sorted(files_sick):
        sick = np.array([1])
        full_path = os.path.join(folder_sick, filename)
        if ((ftype in filename) or (extra_sick in filename)) and os.path.isfile(full_path):
            image = cv2.imread(full_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (image_size, image_size), interpolation=cv2.INTER_CUBIC)
            data.append(image.astype(np.int32))
            labels.append(sick.astype(np.int32))

    return np.asarray(data, dtype=np.float64) / 255.0, np.asarray(labels, dtype=np.int32)


def make_stacked_sets(image_folder_sick, image_folder_healthy, image_size):
    mouth, labels = load_data(image_folder_sick, image_folder_healthy, image_size, "mouth")
    nose, _       = load_data(image_folder_sick, image_folder_healthy, image_size, "nose")
    skin, _       = load_data(image_folder_sick, image_folder_healthy, image_size, "skin")
    eye, _        = load_data(image_folder_sick, image_folder_healthy, image_size, "_right", extra_sick="eye")

    perm = np.random.permutation(len(mouth))
    print(len(mouth), len(nose), len(skin), len(eye))

    imgs = [mouth[perm], nose[perm], skin[perm], eye[perm]]
    return np.asarray(imgs), labels[perm]


def make_stacked_sets_unshuffled(image_folder_sick, image_folder_healthy, image_size):
    mouth, labels = load_data(image_folder_sick, image_folder_healthy, image_size, "mouth")
    nose, _       = load_data(image_folder_sick, image_folder_healthy, image_size, "nose")
    skin, _       = load_data(image_folder_sick, image_folder_healthy, image_size, "skin")
    eye, _        = load_data(image_folder_sick, image_folder_healthy, image_size, "_right")

    imgs = [mouth, nose, skin, eye]
    return np.asarray(imgs), labels


def load_shuffled_data(folder_sick, folder_healthy, image_size, ftype):
    data, labels = load_data(folder_sick, folder_healthy, image_size, ftype)
    perm = np.random.permutation(len(data))
    return data[perm], labels[perm]


def save_history(save_path, history, feature, i):
    path = os.path.join(save_path, str(feature))
    fname = f"history_{i}.pickle" if i < 3 else "history.pickle"
    with open(os.path.join(path, fname), 'wb') as f:
        pickle.dump(history.history, f)


def to_labels(predictions):
    pred = np.zeros((len(predictions), 1), dtype=np.int32)
    for i, p in enumerate(predictions):
        pred[i] = 1 if p >= 0.5 else 0
    return pred


def compute_per_participant(pred, val_labels, folds, feature):
    if feature == 'eye':
        return compute_per_participant_step(pred, val_labels, folds)

    per_participant = np.zeros(len(val_labels), dtype=np.float32)
    for i in range(folds):
        for j in range(len(val_labels)):
            if (pred[i*10+j] == val_labels[j]):
                per_participant[j] += 1
    return per_participant / folds


def compute_per_participant_step(pred, val_labels, folds):
    half = len(val_labels) // 2
    per_participant = np.zeros(half, dtype=np.float32)
    for i in range(folds):
        for j in range(0, len(val_labels), 2):
            if (pred[i*10+j] == val_labels[j]):
                per_participant[j//2] += 1
    return per_participant / folds


# ─── NEW: majority_vote ──────────────────────────────────────────────────

def majority_vote(predictions_list, threshold=None):
    """
    Combine binary predictions from multiple features into one per-person vote.

    Args:
      predictions_list: list of 1D np.arrays of shape (N,) with values {0,1}.
      threshold:        minimum number of "1" votes to flag sick.
                        If None, defaults to strict majority (floor(F/2)+1).

    Returns:
      1D np.array of shape (N,), dtype=int32, with the final 0/1 vote.
    """
    # Stack into shape (F, N) and sum votes per person
    votes = np.stack(predictions_list, axis=0).sum(axis=0)
    F = len(predictions_list)
    if threshold is None:
        threshold = (F // 2) + 1

    # Final = 1 wherever votes ≥ threshold
    return (votes >= threshold).astype(np.int32)
