"""
Purpose:
    Evaluates a single trained model (default is the stacked model for fold 1) using the validation set by:
    - Predicting probabilities,
    - Plotting the ROC curve with AUC,
    - Creating a confusion matrix with custom labels ("Negative" / "Positive"),
    - And displaying the accuracy directly below the confusion matrix plot.

What’s Included:
    - Uses a threshold (thresh = 0.8) to binarize predictions.
    - Visualizes both ROC and confusion matrix, saves both plots.
    - Includes clear labeling and a printout of binary predictions and true values.
"""

import tensorflow as tf
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from pandas import DataFrame
from seaborn import heatmap

sys.path.append(os.getcwd())
from categorization.data_utils import load_data
from categorization.models import *

def get_accuracy(test_labels, prediction_labels, thresh=0.5):
    return np.mean(test_labels == (prediction_labels >= thresh))

print("Loading data...")

image_size = 128
folds = 10

def evaluate_checkpoint(feature, fold, thresh = 0.8):
    # Load test data
    test_faces, _ = load_data('data/parsed/validation_sick', 'data/parsed/validation_healthy', image_size, "face")
    test_images_mouth, test_labels = load_data('data/parsed/validation_sick', 'data/parsed/validation_healthy', image_size, "mouth")
    test_images_face, test_labels = load_data('data/parsed/validation_sick', 'data/parsed/validation_healthy', image_size, "nose")
    test_images_skin, test_labels = load_data('data/parsed/validation_sick', 'data/parsed/validation_healthy', image_size, "skin")
    test_images_left_eye, test_labels = load_data('data/parsed/validation_sick', 'data/parsed/validation_healthy', image_size, "left_eye")
    test_images_right_eye, test_labels = load_data('data/parsed/validation_sick', 'data/parsed/validation_healthy', image_size, "right_eye")

    test_images = [test_images_mouth, test_images_face, test_images_skin, test_images_left_eye, test_images_right_eye]

    # # Settings
    # feature = "mouth"
    # fold = 1
    # thresh = 0.8

    # Choose input images
    if feature == "stacked":
        imgs = test_images
    elif feature == "mouth":
        imgs = test_images[0]
    elif feature == "nose":
        imgs = test_images[1]
    elif feature == "skin":
        imgs = test_images[2]
    elif feature == "left_eye":
        imgs = test_images[3]
    elif feature == "right_eye":
        imgs = test_images[4]

    # Load model and predict
    model = tf.keras.models.load_model(f"categorization/model_saves/{feature}/model_{fold}.h5", compile=False)
    pred = model.predict(imgs)

    pred_bin = (pred >= thresh).astype(int)
    true = test_labels.astype(int)
    acc = get_accuracy(true, pred_bin, thresh)
    return acc

# # === ROC CURVE ===
# fpr, tpr, _ = roc_curve(test_labels, pred)
# roc_auc = auc(fpr, tpr)

# # ROC PLOT
# fig_roc, ax_roc = plt.subplots()
# ax_roc.plot(fpr, tpr, color='orange', label=f'AUC = {roc_auc:.3f}')
# ax_roc.plot([0, 1], [0, 1], 'r--')
# ax_roc.set_xlim([0, 1])
# ax_roc.set_ylim([0, 1])
# ax_roc.set_title(f"ROC Curve - {feature.capitalize()}")
# ax_roc.set_xlabel("False Positive Rate")
# ax_roc.set_ylabel("True Positive Rate")
# ax_roc.legend()
# ax_roc.set_aspect('equal')
# fig_roc.tight_layout()
# fig_roc.savefig(f"data/plots/roc_{feature}_max.png")
# plt.close(fig_roc)

# # === CONFUSION MATRIX ===
# pred_bin = (pred >= thresh).astype(int)
# true = test_labels.astype(int)

# acc = get_accuracy(true, pred_bin, thresh)
# print("Acc", acc)
# print("True:", true.reshape(-1))
# print("Pred:", pred_bin.reshape(-1))

# conf_matrix = np.zeros((2, 2), dtype=int)
# for t, p in zip(true, pred_bin):
#     conf_matrix[int(t)][int(p)] += 1

# df_cm = DataFrame(
#     conf_matrix,
#     index=["Negative", "Positive"],
#     columns=["Negative", "Positive"]
# )

# fig_cm, ax_cm = plt.subplots()
# heatmap(df_cm, annot=True, fmt='d', cmap="Blues", ax=ax_cm)
# ax_cm.set_title(f"Confusion Matrix - {feature.capitalize()}")
# ax_cm.set_xlabel("Predicted")
# ax_cm.set_ylabel("Actual")

# # Add accuracy below the confusion matrix
# plt.text(
#     0.5, -0.2,
#     f"Accuracy: {acc:.2f}",
#     fontsize=12,
#     ha='center',
#     transform=ax_cm.transAxes
# )

# ax_cm.set_aspect('equal')
# fig_cm.tight_layout()
# fig_cm.savefig(f"data/plots/confusion_matrix_{feature}_max.png")
# plt.close(fig_cm)
if __name__ == "__main__":
    # --- Changed: loop over folds and collect results ---
    feature  = "skin"
    max_fold = 10  # adjust to your number of saved models

    results = []
    for fold in range(1, max_fold+1):
        try:
            acc = evaluate_checkpoint(feature, fold)
            print(f"Fold {fold:2d} → Accuracy: {acc:.3f}")
            results.append((fold, acc))
        except Exception as e:
            print(f"Fold {fold:2d} → Error: {e}")

    if results:
        best_fold, best_acc = max(results, key=lambda x: x[1])
        print(f"\n→ Best checkpoint for {feature}: fold {best_fold} with accuracy {best_acc:.3f}")
    else:
        print("No valid results to report.")
