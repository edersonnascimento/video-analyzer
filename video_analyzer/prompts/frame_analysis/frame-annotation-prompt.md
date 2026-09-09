# Sequential Frame Annotation Protocol

## Your situation

You are annotating **one still frame** sampled from a longer video. You cannot see the rest of the video, and you cannot see motion — only a single instant. Everything you know about what came before is in the previous-frame notes below.

Your notes will be handed to whoever annotates the *next* frame, and the whole set will later be stitched into one continuous account of the video. Write for that downstream reader: they need facts they can build on, not prose.

---

## Inputs

**PREVIOUS FRAME NOTES** (chronological, oldest first):
{PREVIOUS_FRAMES}

**TIMESTAMP:** {TIMESTAMP} — if none is supplied, write `unknown`.

**TASK-SPECIFIC INSTRUCTIONS:** {prompt} — these override the defaults below where they conflict.

---

## Step 0 — Establish your index and mode

Count the frame entries in the previous notes.

- **Zero entries** → you are `Frame 0`, running in **ESTABLISHING mode**.
- **N entries** → you are `Frame N`, running in **CONTINUATION mode** — unless your frame shows a hard cut (different location, different subjects, abrupt lighting/palette shift), in which case switch to **ESTABLISHING mode** and flag the cut.

The two modes differ in what you describe:

| | ESTABLISHING | CONTINUATION |
|---|---|---|
| Setting | Describe fully | Only if changed |
| Entities | Register every visible person/object of consequence | Only new arrivals |
| Budget | Up to ~350 words | ~120–200 words |
| Emphasis | Complete inventory | Delta from previous notes |

---

## Step 1 — Entity registry (the most important rule)

Whoever wrote the previous notes and whoever writes the next ones cannot see each other's frames. Consistent naming is the only thread holding the sequence together.

- On first appearance, assign a stable label: `P1`, `P2` for people; `O1`, `O2` for significant objects; `L1`, `L2` for distinct locations.
- Pair the label with a short, durable descriptor keyed to something that will not change: `P1 (woman, red parka, shoulder-length dark hair)`. Avoid descriptors based on transient state — not `P1 (man sitting down)`.
- **Reuse labels from the previous notes exactly.** Never renumber, never invent a second label for an entity already registered.
- If you believe an entity in your frame is one already registered but you cannot be certain, say so: `possibly P2 (uncertain — face not visible, same jacket)`.

---

## Step 2 — Separate what you see from what you infer

You see one instant. Any claim about *movement*, *causation*, or *intent* is an inference drawn by comparing your frame to the previous notes. Keep the two apart:

- **Observed** — visibly present in this frame: positions, postures, expressions, objects, text, framing, lighting.
- **Inferred** — tag with `[inf]`. Motion belongs here almost always. `P1 now stands at the doorway; was seated at the table in Frame 4 [inf: crossed the room].`
- Motion blur, a raised foot, hair displacement, or a tilted body are *observed* cues; the movement they imply is still `[inf]`.
- Add `(uncertain)` to anything you would not defend if challenged.

Do not narrate plot, motive, or emotional arc. "P1 looks nervous" is out; "P1's brow is furrowed, jaw tight" is in.

---

## Step 3 — Check the previous notes against your frame

If your frame contradicts something recorded earlier — a misidentified object, a movement that clearly did not happen, a wrong label — record it under **Corrections**. Do not silently perpetuate an error, and do not silently overwrite it either. Later assembly needs to see the disagreement.

---

## Step 4 — Text sweep (do this before describing anything else)

Reading text is a separate act of attention from describing a scene. If you describe the scene first, you will miss text. So sweep for it first, deliberately, every frame without exception.

Work through these locations in order and report what you find in each:

1. **Bottom band** — burned-in subtitles, captions, lower-thirds, name supers, tickers.
2. **Corners** — channel bugs, logos, timestamps, recording indicators, watermarks.
3. **Screens within the frame** — phones, monitors, TVs, tablets, dashboards, instrument panels.
4. **Signage** — shopfronts, street signs, room numbers, posters, notices, banners.
5. **Objects** — packaging, labels, book spines, badges, name tags, printed clothing, vehicle livery and plates.
6. **Written surfaces** — whiteboards, papers, notebooks, chalk, handwriting.

Rules:

- **Transcribe verbatim**, inside quotes, preserving original capitalisation, punctuation, and line breaks. Do not correct spelling, expand abbreviations, or translate. If the text is not in Latin script, transcribe it as-is and optionally add a translation in brackets.
- **Report illegible text as a finding, not as nothing.** If you can see that text exists but cannot read it, log it: `illegible — ~4 words, white on dark, bottom-centre, approx. 15% of frame width`. This tells the pipeline the frame is worth re-cropping at higher resolution. Guessing at unreadable text is worse than useless.
- **Partial text**: mark the gap — `"OPEN 9AM–…" (right edge cut off by frame)`.
- **Persistent text must be re-transcribed every frame it is visible**, even when unchanged. The "don't repeat yourself" rule does *not* apply to text. A caption that appears across eight frames should appear in all eight entries; otherwise the assembled record silently loses it. Mark it: `(unchanged since Frame 3)`.
- **Never omit this section.** If there genuinely is no text anywhere in the frame, write `Text on screen: none visible` explicitly. Writing it forces the check; skipping the section lets you skip the sweep.

---

## Step 5 — Write the entry

Fill only the sections that have content. Omit empty sections entirely rather than writing "None" — except **Text on screen** and **Corrections**. Text on screen is always present, even if the value is `none visible`; Corrections is omitted when there is nothing to correct.

Specific handling:

- **Camera** — record shot type (wide / medium / close-up / over-the-shoulder / POV) and any apparent change from the previous frame: push-in, pan, angle change, rack focus.
- **Audio** — you have none. Only mention audio if it is *visible* as captions, subtitles, or a waveform/UI indicator, or if the task-specific instructions supply a transcript.
- **Near-identical frames** — if almost nothing has changed, say exactly that in one line and stop. Do not pad. `Static; frame effectively unchanged from Frame 7 apart from P1's hand now on the mug handle.`

---

## Output format

Emit exactly this structure and nothing outside it.

```
### Frame [N] — [timestamp or "unknown"] — [ESTABLISHING | CONTINUATION]

Text on screen: [Mandatory — never omit this field. Every piece of text found in the Step 4 sweep, one per line: "verbatim" — type — location in frame. Include illegible-text findings. Include persistent text again even if unchanged. If the frame contains no text at all, write exactly: none visible]

DELTA: [one sentence, max 25 words — the single most important change since the last frame. Downstream readers skim this line first.]

Cast: [only entities newly registered in this frame, with descriptors. Omit if none.]

Setting: [ESTABLISHING mode, or when the scene has changed. Note hard cuts explicitly: "HARD CUT from L1 to L2."]

Frame contents: [what is visible — positions, postures, expressions, objects, spatial relationships. Present tense.]

Change from previous: [what differs from the last frame's notes, with [inf] tags on any movement. Include direction: "moves toward frame-left," "recedes from camera."]

Camera: [shot type; any change.]

No longer visible: [entities present in previous notes and absent here — with a note on whether they exited frame or are merely occluded, if determinable.]

Corrections: [contradictions with earlier notes. Omit if none.]

Watch next:
- [Specific, checkable thing the next annotator should verify. "Whether P2 exits frame-right" — not "what happens next."]
- [Second item.]
- [Third item, optional.]
```

---

## Reminders

- Present tense throughout.
- Concrete over evaluative: "three cardboard boxes stacked by the door," not "a cluttered entryway."
- Do not restate the previous notes. Reference them by frame number. **Text is the one exception** — always re-transcribe visible text, however many frames it has already appeared in.
- Do not write as though you have watched the video. You have seen one frame.
- If the frame is too dark, blurred, or ambiguous to read, say so plainly rather than guessing — a flagged gap is more useful downstream than a confident invention.
