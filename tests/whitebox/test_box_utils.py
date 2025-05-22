# tests/whitebox/test_box_utils.py
import sys, os
# go up two levels to the project root
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, root)
import cv2
import numpy as np
import pytest
from pathlib import Path

import categorization.box_utils as bu

# ── Test W04: No face detected ──
def test_no_face_detected(tmp_path, monkeypatch):
    # 1) write a blank image to disk
    img_path = tmp_path / "blank.png"
    cv2.imwrite(str(img_path), np.zeros((100, 100, 3), dtype=np.uint8))

    # 2) stub out the cascade to return no faces
    class EmptyCascade:
        def detectMultiScale(self, *args, **kwargs):
            return []
    monkeypatch.setattr(bu, "faceCascade", EmptyCascade())

    # 3) calling get_face_boxes should raise RuntimeError("No face found")
    with pytest.raises(RuntimeError, match="No face found"):
        bu.get_face_boxes(str(img_path))


# ── Test W05: Successful face detection and box generation ──
def test_successful_box_generation(tmp_path, monkeypatch):
    # 1) write a dummy white image
    img_path = tmp_path / "face.png"
    cv2.imwrite(str(img_path), np.ones((200, 200, 3), dtype=np.uint8) * 255)

    # 2) stub the cascade to return exactly one face box (10,20,50,50)
    class DummyCascade:
        def detectMultiScale(self, *args, **kwargs):
            return [(10, 20, 50, 50)]
    monkeypatch.setattr(bu, "faceCascade", DummyCascade())

    # 3) stub getDominantColor to a constant
    monkeypatch.setattr(bu, "getDominantColor", lambda img: (128, 128, 128))

    # 4) stub extractFeatures to return predictable landmarks:
    #    here we return a (68,2) array where points 0–16 map to a small
    #    region inside the face box so we can test mouth coordinates.
    def dummy_extractFeatures(face, detector, predictor, color, status, stem):
        # create 68 points along the diagonal
        pts = np.vstack([np.linspace(0, 49, 68), np.linspace(0, 49, 68)]).T
        return pts
    monkeypatch.setattr(bu, "extractFeatures", dummy_extractFeatures)

    # 5) override the landmark index mapping to test just "mouth"
    monkeypatch.setattr(bu, "FACIAL_LANDMARKS_IDXS", {"mouth": np.arange(0, 17)})

    # 6) call the function
    boxes = bu.get_face_boxes(str(img_path))

    # 7) assertions
    #    - must contain a "face" key with exactly the tuple we returned
    assert boxes["face"] == [10, 20, 50, 50]
    #    - must contain a "mouth" key whose box is within [10,20,50,50]
    mx, my, mw, mh = boxes["mouth"]
    assert 10 <= mx <= 10+50
    assert 20 <= my <= 20+50
    assert mw > 0 and mh > 0
