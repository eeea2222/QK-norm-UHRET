# Dashboard integration

Feature: inspect a real NASA camera1 frame, display the measured/model-corrected luminous ridge and its time trajectory, show unavailable frames explicitly, and compare the derived nominal-mm/s trajectory with the separately sourced phase-reference rates. Do not present a universal risk ranking or interchangeable material response.

## Request schema

```json
{"type":"object","required":["frame_path","camera_id","image_mapping","material","units"],"additionalProperties":false,"properties":{"frame_path":{"type":"string"},"camera_id":{"const":"C1"},"image_mapping":{"const":"NASA_mapped"},"material":{"const":"SIBAL"},"units":{"const":"mm"},"timestamp_ms":{"type":"number","description":"finite original Unix epoch milliseconds, optional"}}}
```

The image must be original, unresized RGB1702x1226. The caller supplies a dark/backlight-off image from the audited camera setup. The API returns a dict; all unsupported setup fields error explicitly. Missing or non-finite timestamp values error. C1 ridge x near the boundary or absent/abnormal luminous statistics returns null and OOD reasons. Input statistics envelopes are broader than the observed development values; they are not exact training-point matching.

## Executed sample

Paths below reflect the environment where the sample ran; replace frame_path with your local original frame.

```json
{
  "request": {
    "frame_path": "/content/saffire_b_reproduction/data/frames/Mapped_S1C1-1465937331457.jpeg",
    "camera_id": "C1",
    "image_mapping": "NASA_mapped",
    "material": "SIBAL",
    "units": "mm",
    "timestamp_ms": 1465937331457
  },
  "response": {
    "model_id": "model_b",
    "model_version": "0.1.0",
    "quantity": "luminous_ridge_x_from_image_left",
    "value": 220.28979111936016,
    "unit": "mm",
    "value_kind": "predicted",
    "position_px": 484.63754046259237,
    "raw_extracted_position_px": 505.0,
    "raw_extracted_value_kind": "derived",
    "ood": {
      "flag": false,
      "reasons": []
    },
    "warnings": [
      "Linear correction uses a coordinate outside its development-fit range; later-block error is reported separately, with no cross-experiment guarantee"
    ],
    "applicable_domain": {
      "mission": "Saffire-I",
      "material": "SIBAL",
      "camera_id": "C1",
      "mapping": "NASA mapped",
      "size_px": [
        1702,
        1226
      ],
      "illumination": "dark/backlight off",
      "ridge_band_y_px": [
        500,
        720
      ],
      "development_time_s": [
        30,
        200
      ],
      "development_frame_count": 18,
      "independent_samples": 1,
      "claim": "within-view measurement agreement with agent visual annotations; no cross-experiment prediction"
    },
    "uncertainty": null,
    "uncertainty_note": "Spacing scatter is a repeatability diagnostic, not a full physical calibration uncertainty. Nominal grid square tolerance and mapping systematic error unavailable.",
    "calibration_nominal": true,
    "interpretation": "Median luminous-ridge position in image rows500:720. This is not a danger score or a prediction for a new burn.",
    "timestamp_ms": 1465937331457
  }
}
```

`quantity` is luminous_ridge_x_from_image_left, not distance from the physical ignition wire. `raw_extracted_position_px` is deterministic/derived. Learned-corrected `position_px` and its calibrated `value` are model predictions of the agent-defined ridge center and tagged predicted. `unit` is nominal mm because full calibration tolerance is unavailable. `uncertainty=null` explicitly conveys that no valid complete interval was established. `warnings` identifies coordinate correction outside development-fit support. `applicable_domain` documents the one-sample, one-camera measurement scope. `ood` is an availability/input-quality check, not a validated universal novelty score.

Trajectory speed is negative slope of corrected position versus original time because the observed ridge moves right-to-left. Keep it separate from published whole-burn source rates and from model_a's predicted PMMA spread. The rate comparison can be labeled “Different materials/scales/quantity definitions: descriptive comparison only.” Values from model_a must retain its own validation and applicability metadata. No model_a code or dashboard is changed by this project.
