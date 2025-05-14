import os
import sys
import datetime
from contextlib import redirect_stdout


import tensorflow as tf
from numpy import interp
from sklearn.metrics import auc
from sklearn.metrics import roc_curve
from sklearn.model_selection import StratifiedKFold
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

sys.path.append(os.getcwd())
from categorization.models import make_model
from categorization.plot_utils import *
from categorization.data_utils import *

if __name__ == "__main__":

    image_folder_training_sick = 'data/parsed/training_sick'
    image_folder_training_healthy = 'data/parsed/training_healthy'
    image_folder_val_sick = 'data/parsed/validation_sick'
    image_folder_val_healthy = 'data/parsed/validation_healthy'

    save_path = 'categorization/model_saves/'
    face_features = ["mouth", "nose", "skin", "left_eye", "right_eye"]

    base_fpr = np.linspace(0, 1, 101)
    image_size = 128
    folds = 10

    # skfold = StratifiedKFold(n_splits=folds, shuffle=False, random_state=1)
    skfold = StratifiedKFold(n_splits=folds, shuffle=False, random_state=None)


    for feature in face_features:
        auc_sum = 0
        tprs = []
        fold_no = 1

        print("[INFO] Training %s" % (feature))

        val_images, val_labels = load_shuffled_data(
            image_folder_val_sick, image_folder_val_healthy, image_size, feature)
        images, labels = load_shuffled_data(
            image_folder_training_sick, image_folder_training_healthy, image_size, feature)

        plt.figure()

        # var to track best fold info
        best_f1_overall = 0
        best_fold = -1

        for train, test in skfold.split(images, labels):

            tf.keras.backend.clear_session()
            model = make_model(image_size, feature)

            early_stopping = EarlyStopping(
                monitor='val_F1_metric', mode='max', patience=10, verbose=1)
            model_check = ModelCheckpoint(
                save_path + str(feature) + '/model_' + str(fold_no) + '.h5', monitor='val_F1_metric', mode='max',
                verbose=1, save_best_only=True)

            history = model.fit(images[train], labels[train], epochs=50, batch_size=4,
                                callbacks=[early_stopping, model_check], validation_data=(images[test], labels[test]))

            save_history(save_path, history, feature, fold_no)

            all_saves = os.listdir(save_path + str(feature))
            for save in all_saves:
                # print(save)
                if str(fold_no) + '.h5' in save:
                    best_model_path = save_path + str(feature) + "/" + save

            saved_model = tf.keras.models.load_model(best_model_path, compile=False)
            
            val_preds = saved_model.predict(val_images)
            pred_labels = to_labels(val_preds)

            # Save confusion matrix for this fold only
            best_f1 = max(history.history['val_F1_metric'])
            if fold_no == 1 or best_f1 > best_f1_overall:
                best_f1_overall = best_f1
                best_fold = fold_no
                is_best = "best"
            else:
                is_best = ""

            conf_name = f"{feature}_fold{fold_no}_{is_best}".strip("_")
            
            print_confusion_matrix(pred_labels, val_labels, feature, folds, name=conf_name)
            
            # Track overall predictions if needed
            if fold_no == 1:
                predictions = pred_labels
            else:
                predictions = np.concatenate((predictions, pred_labels), axis=0)

            # ROC Curve
            fpr, tpr, _ = roc_curve(val_labels, val_preds)
            auc_sum += auc(fpr, tpr)
            tpr = interp(base_fpr, fpr, tpr)
            tpr[0] = 0.0
            tprs.append(tpr)

            fold_no += 1

        # TODO: testing here (do validation once)
        
        # Final testing on entire validation set
        print("\n[INFO] Final Evaluation on Entire Validation Set")

        # Predict using best models from each fold and average them
        all_preds = np.zeros((val_images.shape[0], folds))

        for i in range(1, folds + 1):
            model_path = os.path.join(save_path, feature, f"model_{i}.h5")
            model = tf.keras.models.load_model(model_path, compile=False)
            preds = model.predict(val_images)
            all_preds[:, i - 1] = preds.flatten()
            del model

        # Average predictions across all folds
        avg_preds = np.mean(all_preds, axis=1)
        avg_labels = to_labels(avg_preds)

        # Final Confusion Matrix and Accuracy
        print_confusion_matrix(avg_labels, val_labels, feature, folds, name="final")

        # print average accuracy
        acc = np.mean(avg_labels == val_labels)
        print(f"[RESULT] Final averaged accuracy for {feature}: {acc:.4f}")


        print_roc_curve(tprs, auc_sum, feature, folds)
        print_confusion_matrix(predictions, val_labels, feature, folds)



