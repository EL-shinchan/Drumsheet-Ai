# Reviewer Checklist

The review agent should check every pushed commit against this list.

## 1. Regression check
- Did the patch break previously fixed placement?
- Did hi-hat/snare/kick drift off the intended grid?
- Did difficulty behavior regress?

## 2. Pipeline-stage check
Review the change by layer:
1. audio detection
2. quantization
3. groove reconstruction
4. notation encoding
5. visual rendering

The reviewer should identify which layer likely contains the bug instead of reporting only the surface symptom.

## 3. Music sanity check
Especially for beginner mode:
- beat 1 visible
- snare on 2/4 unless strong contrary evidence
- kick on musically believable downbeats
- hi-hat pulse readable and not over-segmented
- no nonsense density beyond the chosen pulse

## 4. Debug visibility check
- Are debug outputs still useful after the patch?
- Can the failure be traced through the pipeline?
- Are source tags (`skeleton`, `override`, `detected`, `fallback`) still honest?

## 5. User-facing report format
Reviewer outcome should include:
- pass / concern / fail
- exact concern
- likely layer causing it
- recommended next fix
