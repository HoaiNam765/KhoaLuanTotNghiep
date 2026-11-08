# NAFLD Insight — Design System v3 · Simple, human-centered research UI

Design decisions follow UI/UX Pro Max accessibility and interaction guidance, adapted to Streamlit (not a supported dedicated stack in the source skill).

## Audiences / navigation

One navigation bar with four entries: **Giới thiệu**, **Dự đoán**, **Giải thích**, **Nghiên cứu**. The first three focus on everyday users; Nghiên cứu contains detailed frozen scientific evidence and citations. No duplicated user/research sidebar hierarchies.

## Design tokens

- `accent`: `#176A72` — calm teal, actions, selected options, explanatory positive contributions; never a severity level.
- `canvas`: `#F7F8F6` — gentle warm off-white.
- `surface`: `#FFFFFF` — form fields and evidence tables.
- `ink`: `#1B3137` — primary readable text.
- `muted`: `#506469` — captions and secondary explanatory text.
- `divider`: `#DDE5E3`.
- `chart.secondary`: `#9F7450` — contributions below the baseline (not 'healthy' or diagnosis).
- `message.caution`: `#FFF4E9` with contrast text `#604220` — research limits and medical caution.
- `message.info`: `#E9F3F1` with contrast text `#23474B` — non-urgent guidance.

No bright AI-looking gradients, dark giant hero, floaty animated glows, or emoji used as navigation. Consistent gentle 1px borders and 10–16px corner radii.

## Typography and forms

- System font stack, base 16px; readable 1.65 line height.
- Maximum text width 1130px; on mobile, Streamlit native columns stack.
- Distinct section hierarchy; 44px controls; visible 3px amber focus outline; respect reduced motion.
- All 26 fields have Vietnamese visible labels, units and concise contextual help. Numeric blanks map to missing; a real zero remains zero.
- Four collapsed-by-default? First G1 expanded, others progressively disclosed; no 26-field wall visible immediately.
- Category radios have **no freeform editable search input**.
- One primary action “Xem kết quả dự đoán”; auto-selects **frozen F1 OOF threshold**. Alternative threshold methodology stays in research evidence only.

## Results

- User result prioritizes: numerical model probability, explicit research-label classification, one short explanation, medical limits.
- Group probability and Fusion weight available through disclosure. Never portray weight as clinical importance.
- Optional local permutation Shapley from 12 frozen VAL background examples and 24 permutations: distinct from week-9 SHAP global on VAL.
- Never claim the user is clinically diagnosed or free of NAFLD based on this output.

## CSV

- Downloadable UTF-8-BOM CSV 26-column template with two fictional cases; any order allowed if column codes exactly match the contract.
- 100 rows and 1 MB per upload; validate all numeric and category values; accept either comma or semicolon delimiter; show errors by row.
- Export predictions without raw input features. No persistent server database or automatic incorporation of uploaded data into research.

## Scientific reproducibility

- Unchanged SHA256 manifest and 11 frozen model/preprocessing/weight/threshold files.
- No TEST reads, refits or generation of new experimental metrics.
- Researcher tables are read-only from week-5–9 source CSV with TRAIN CV / OOF / VAL source caption.
- Python regression tests for inferencing, CSV and research evidence; browser/manual 15-flow acceptance is separate.
