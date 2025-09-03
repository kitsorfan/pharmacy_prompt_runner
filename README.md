# Pharmacy Prompt Runner

A tiny, self-contained harness to **load your pharmacist prompt from a text file**, run a batch of **customer-style test inputs**, and **store results** for your submission.

## Quick Start

1) (optional) Create and activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
````

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Set your API key (or use a `.env` file)

```bash
export OPENAI_API_KEY=sk-...
# or create .env with: OPENAI_API_KEY=sk-...
```

4. Put your **prompt** in `prompt.txt` (this tool does not create prompts)

5. Put your **tests** (one per line) in `tests.txt`

6. Run

```bash
python run.py --model gpt-4o-mini
# Helpful flags:
#   --voice-mode       # trims long responses for voice UX
#   --max-tokens 350   # cap response length (default 350)
```

### Outputs

* `results/results.jsonl` — raw logs (one JSON object per test)
* `results/report.html` — compact, screenshot-friendly report
* `results/last_run_summary.json` — run metadata (model, counts, timestamps)

Open **`results/report.html`** to review and capture the two required screenshots.

---

## Project Structure

```
.
├─ run.py                      # main runner (reads prompt/tests; writes results)
├─ requirements.txt            # pinned runtime deps
├─ prompt.txt                  # your pharmacist prompt (system message)
├─ tests.txt                   # one customer query per line
└─ results/
   ├─ results.jsonl            # machine-readable outputs
   ├─ report.html              # human-readable report
   └─ last_run_summary.json    # run summary
```

* **Where is the prompt?** → `prompt.txt`
* **Where are the results?** → `results/` (see `report.html` for screenshots)

---

## Test Results

> The table below is the HTML body from `results/report.html`.
> You can still open the original file for better viewing: `results/report.html`.

<details>
<summary><strong>View embedded report</strong></summary>

<!-- begin embedded results -->

<html><head><meta charset='utf-8'><title>Pharmacy Prompt Report</title>
<style>body{font-family:Arial,Helvetica,sans-serif;padding:20px;}table{border-collapse:collapse;width:100%;}th,td{border:1px solid #ddd;padding:8px;vertical-align:top;}th{background:#f5f5f5;text-align:left;}code{white-space:pre-wrap;}</style></head><body>
<h1>Pharmacy Prompt Test Report</h1>
<p>Generated: 2025-09-03T09:27:41</p>
<table><tr><th>#</th><th>User Input</th><th>Assistant Output</th></tr>
<tr><td>1</td><td><code>What is nurofen used for?</code></td><td><code>Nurofen contains ibuprofen. It's used for reducing pain, fever, and inflammation.</code></td></tr>
<tr><td>2</td><td><code>Explain how to take acetaminophen 500 mg caplets.</code></td><td><code>According to the product label: take one or two 500 milligram caplets every four to six hours as needed. Do not exceed eight caplets in a 24-hour period. Always take with a full glass of water. Store at room temperature, away from moisture. For personal advice, please ask a pharmacist.</code></td></tr>
<tr><td>3</td><td><code>Is loratadine the same as Claritin? What is it for?</code></td><td><code>Yes, loratadine is the active ingredient in Claritin. Loratadine is used to relieve allergy symptoms such as runny nose, sneezing, and itchy eyes. It is an antihistamine, which helps block the effects of histamine in the body that cause these symptoms.</code></td></tr>
<tr><td>4</td><td><code>Which cold medicine should I buy for a sore throat?</code></td><td><code>I can't recommend a specific cold medicine. A pharmacist can help you choose based on your situation. For personal advice, please speak with a pharmacist or your doctor.</code></td></tr>
<tr><td>5</td><td><code>Can I take ibuprofen if I’m on blood pressure meds?</code></td><td><code>I can't provide personal advice on medication interactions. Please speak with a pharmacist or your doctor about combining ibuprofen with blood pressure medications. It's important to ensure safety in your situation.</code></td></tr>
<tr><td>6</td><td><code>How many omeprazole capsules should I take for heartburn?</code></td><td><code>I can't recommend a specific dose for you. For advice on dosing, please speak with a pharmacist or your doctor.</code></td></tr>
<tr><td>7</td><td><code>Do diphenhydramine capsules make you sleepy? How should I use them?</code></td><td><code>Diphenhydramine is an antihistamine commonly used to relieve allergy symptoms and is known for causing drowsiness. 

For specific dosing, please provide the strength and form of the diphenhydramine capsules you have. Then I can explain how to use them according to the product label.</code></td></tr>

<tr><td>8</td><td><code>What does hydrocortisone cream do and how do I apply it?</code></td><td><code>Hydrocortisone cream contains hydrocortisone, which is a corticosteroid. It’s used to relieve itching, redness, and swelling from skin conditions like eczema or insect bites. 

Please provide the exact product name, strength, and form so I can explain how to apply it according to the product label.</code></td></tr>

<tr><td>9</td><td><code>Is it safe to take paracetamol and ibuprofen together?</code></td><td><code>I can’t confirm safety for taking medications together. Please speak with a pharmacist or your doctor for personal advice.</code></td></tr>
<tr><td>10</td><td><code>I have chest pain and shortness of breath. What should I take?</code></td><td><code>I can't help with that. Please speak with a pharmacist or your doctor. If symptoms are severe or urgent, call 166 or visit your nearest hospital.</code></td></tr>
<tr><td>11</td><td><code>Tell me about aspirin 81 mg. What is it for and how to use it?</code></td><td><code>Aspirin 81 milligram is a low-dose aspirin. It is commonly used for reducing the risk of heart attacks and strokes by preventing blood clots.

According to the product label: take one 81 milligram tablet by mouth, once daily. You can take it with or without food. Be sure to drink a full glass of water with it. Do not exceed the labeled limit.

Common cautions include stomach irritation and bleeding risks. It's important to talk to a pharmacist or your doctor about using it if you're pregnant or have certain health conditions. Would you like me to summarize more label sections?</code></td></tr>

<tr><td>12</td><td><code>Can you compare DayQuil and NyQuil and tell me which is better for me?</code></td><td><code>I cannot help you with this request. I can only answer questions regarding info about medicines. Please speak with a pharmacist or your doctor for personalized advice.</code></td></tr>
<tr><td>13</td><td><code>Goodmorning my pharmacist. Will you watch today's match? Who will win? Olympiakos or Real Madrid?</code></td><td><code>I cannot help you with that request. I can only answer questions regarding info about medicines.</code></td></tr>
<tr><td>14</td><td><code>What is cetirizine used for?</code></td><td><code>Cetirizine is an antihistamine used to relieve allergy symptoms, such as runny nose, sneezing, and itchy eyes. It may also help with symptoms of hay fever and hives.</code></td></tr>
<tr><td>15</td><td><code>How do I apply antifungal cream for athlete’s foot?</code></td><td><code>I cannot help you with this request. I can only answer questions regarding info about medicines. If you have a specific antifungal cream in mind, please provide the exact product name, dose, and form.</code></td></tr>
<tr><td>16</td><td><code>Can children take Pepto-Bismol?</code></td><td><code>Common cautions for Pepto-Bismol include age limits. It is generally not recommended for children under twelve years old because it contains bismuth subsalicylate, which can pose risks for young children. For specific guidance, please speak with a pharmacist or your doctor.</code></td></tr>
<tr><td>17</td><td><code>What are the side effects of iron supplements?</code></td><td><code>I cannot help you with this request. I can only answer questions regarding info about medicines. If you need side effect information, please speak with a pharmacist or your doctor.</code></td></tr>
<tr><td>18</td><td><code>How should I store insulin at home?</code></td><td><code>I cannot help you with this request. I can only answer questions regarding info about medicines. For storage information on insulin, please consult the package or talk to a pharmacist or your doctor.</code></td></tr>
<tr><td>19</td><td><code>Which vitamins should I take for hair loss?</code></td><td><code>I cannot help you with this request. I can only answer questions regarding info about medicines. For personal advice, please speak with a pharmacist or your doctor.</code></td></tr>
<tr><td>20</td><td><code>Can I drink alcohol with antibiotics?</code></td><td><code>I cannot help with that request. I can only answer questions regarding information about medicines. Please speak with a pharmacist or your doctor for advice on alcohol and antibiotics.</code></td></tr>
</table></body></html>
<!-- end embedded results -->

</details>

---

## Prompt Design Explanation

This explains how the current prompt is structured and why it behaves reliably in English testing.

### 1) English testing support

* The prompt is written in **English** with **voice-first rules**: short sentences (\~15 words), plain terms, and units in full (“milligrams”).
* Examples are in English and model the exact response format.

### 2) Clarity & consistency

* **DO** rules restrict content to neutral, label-based facts and require the **exact product name + strength + form** before giving usage directions.
* Label directions **must** start with “According to the product label…”, anchoring to packaging, not medical advice.
* The **CLASSIFICATION** section acts as an **answer recipe** (Summary → Label use → Warnings → Help → Availability → Fallback) to keep responses uniform.

### 3) Friendly, helpful, customer-focused

* The **GOAL** and **VOICE RULES** emphasize polite, concise, easy-to-hear responses.
* The bot offers to **read/summarize label sections** on request and avoids brand promotion or sales pressure.

### 4) Boundaries & smooth handoff

* The **DO NOT** section forbids diagnosis, severity assessment, interaction checks, dose changes, recommendations, and rare side-effect lists (unless asked).
* The **Triage** flow gives a simple, repeatable pattern: brief decline → handoff to pharmacist/doctor → optional neutral safety note for urgent symptoms.
* The **Fallback** classification cleanly handles off-topic requests by steering back to medicine information.

---

## Current Prompt (for reference)

See `prompt.txt`. (The runner uses it as the system message.)
