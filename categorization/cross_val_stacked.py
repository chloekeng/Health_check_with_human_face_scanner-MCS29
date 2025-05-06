### Cross-validation for stacked model
'''Loads training and validation image sets (stacked features: mouth, nose, skin, eye).
Initializes and saves individual feature models.
Uses StratifiedKFold to perform 10-fold cross-validation.
For each fold:
    Loads the individual models and defines a stacked model.
    Trains the stacked model with early stopping and model checkpointing.
    Saves training history and the best model.
    Evaluates on the validation set (not the test fold).
    Stores predictions and calculates the ROC curve and AUC.
After the loop, it plots a combined ROC curve and prints a confusion matrix. 
'''
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from numpy import interp
from sklearn.metrics import auc, roc_curve
from sklearn.model_selection import StratifiedKFold
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import tensorflow as tf

# ensure project root is on PYTHONPATH
sys.path.append(os.getcwd())

from categorization.models import make_model, load_all_models, define_stacked_model
from categorization.plot_utils import print_roc_curve, print_confusion_matrix
from categorization.data_utils import make_stacked_sets, to_labels, majority_vote

if __name__ == "__main__":
    # --- paths & parameters ---
    image_folder_training_sick   = 'data/parsed/training_sick'
    image_folder_training_healthy= 'data/parsed/training_healthy'
    image_folder_val_sick        = 'data/parsed/validation_sick'
    image_folder_val_healthy     = 'data/parsed/validation_healthy'
    save_path                    = 'categorization/model_saves'
    face_features                = ["mouth", "nose", "skin", "eye"]
    image_size                   = 128
    folds                        = 10
    base_fpr                     = np.linspace(0, 1, 101)

    # --- data loading ---
    images, labels     = make_stacked_sets(
        image_folder_training_sick,
        image_folder_training_healthy,
        image_size
    )
    val_images, val_labels = make_stacked_sets(
        image_folder_val_sick,
        image_folder_val_healthy,
        image_size
    )

    # --- prepare for voting ensemble ---
    preds_per_feat = { feat: [] for feat in face_features }

    # --- initialize empty base models for stacking ---
    print("Creating empty models...")
    for feature in face_features:
        print(f"  {feature}...")
        mdl = make_model(image_size, feature, mcompile=False)
        mdl.save(os.path.join(save_path, feature, "model.h5"))

    # --- 10-fold cross-validation for stacked model ---
    skfold = StratifiedKFold(n_splits=folds, shuffle=False)
    plt.figure()
    tprs = []
    auc_sum = 0
    fold_no = 1

    for train_idx, test_idx in skfold.split(images[0], labels):
        print(f"\n--- Fold {fold_no} ---")

        # load and train stacked model for this fold
        all_models = load_all_models(save_path, face_features)
        stacked    = define_stacked_model(all_models, face_features)

        es  = EarlyStopping(monitor="val_F1_metric", mode='max', patience=10, verbose=1)
        ck  = ModelCheckpoint(
            os.path.join(save_path, 'stacked', f"model_{fold_no}.h5"),
            monitor="val_F1_metric", mode='max', verbose=1, save_best_only=True
        )

        history = stacked.fit(
            x=[images[i][train_idx] for i in range(len(face_features))],
            y=labels[train_idx],
            epochs=50,
            batch_size=4,
            callbacks=[es, ck],
            validation_data=(
                [images[i][test_idx] for i in range(len(face_features))],
                labels[test_idx]
            )
        )

        # save history
        from categorization.data_utils import save_history
        save_history(save_path, history, 'stacked', fold_no)

        # evaluate stacked model on VAL set
        stacked_best = tf.keras.models.load_model(
            os.path.join(save_path, 'stacked', f"model_{fold_no}.h5"),
            compile=False
        )
        pred_proba = stacked_best.predict(
            [val_images[i] for i in range(len(face_features))]
        )
        # accumulate for ROC
        fpr, tpr, _ = roc_curve(val_labels, pred_proba)
        auc_sum    += auc(fpr, tpr)
        plt.plot(fpr, tpr, 'b', alpha=0.15)
        tpr_interp = interp(base_fpr, fpr, tpr)
        tpr_interp[0] = 0.0
        tprs.append(tpr_interp)

        # accumulate preds for confusion matrix (stacked)
        bin_pred = to_labels(pred_proba)
        if fold_no == 1:
            stacked_preds = bin_pred
        else:
            stacked_preds = np.concatenate((stacked_preds, bin_pred), axis=0)

        # --- collect per-feature votes for this fold ---
        for i, feat in enumerate(face_features):
            feat_model = tf.keras.models.load_model(
                os.path.join(save_path, feat, f"model_{fold_no}.h5"),
                compile=False
            )
            proba = feat_model.predict(val_images[i])
            preds_per_feat[feat].append(to_labels(proba).flatten())

        fold_no += 1

    # --- final stacked-model metrics ---
    print_roc_curve(tprs, auc_sum, 'stacked', fold_no)
    print_confusion_matrix(stacked_preds, val_labels, 'stacked', fold_no)

    # --- Voting-ensemble evaluation ---
    # concatenate each feature's fold predictions
    final_list = [
        np.concatenate(preds_per_feat[feat], axis=0)
        for feat in face_features
    ]
    # continuous vote score for ROC
    votes      = np.stack(final_list, axis=0).sum(axis=0)
    vote_score = votes / len(face_features)

    # ROC for voting
    fpr_v, tpr_v, _ = roc_curve(val_labels, vote_score)
    auc_v          = auc(fpr_v, tpr_v)
    plt.figure()
    plt.plot(fpr_v, tpr_v, 'g', label=f'Voting AUC={auc_v:.3f}')
    plt.plot([0,1], [0,1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC – Voting Ensemble')
    plt.legend()
    plt.show()

    # hard-vote labels and confusion
    ensemble_labels = majority_vote(final_list)
    print_confusion_matrix(ensemble_labels, val_labels, 'voting', folds)