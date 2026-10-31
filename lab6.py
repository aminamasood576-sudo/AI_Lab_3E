import re
import csv
import time
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from sentence_transformers import SentenceTransformer
    t0 = time.perf_counter()
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
    load_time = time.perf_counter() - t0
except Exception:
    model = None
    load_time = None

docs = {
    "late": "Assessment Policy. All coursework must be submitted before the published deadline. Late submission is normally penalized by ten percent for every day after the deadline, and work that arrives more than five days late receives no marks at all unless the course coordinator has approved a different arrangement in writing before the deadline expires. Illness extensions require medical evidence before the deadline. Students who cannot attend an exam for the same reason must follow a separate procedure and contact the exams office. Group projects follow the same rules, but each member must tell the coordinator about any problem as soon as possible. Dr. Khan keeps a record of every approved extension and shares it with the department each semester. Students should keep copies of all emails about deadlines. The learning portal shows the official time of submission and this time is final. Technical problems with the portal should be reported to the IT help desk immediately so that a ticket number can be recorded. Plagiarism is handled under a different policy and is not covered here.",
    "password": "IT Account Guide. Reset a forgotten password using the recovery link on the login page. The link is sent to the registered student email address and stays active for thirty minutes, after which a new link must be requested from the same page. Never share recovery codes with anyone, including friends, classmates and staff who claim to work for the help desk. The old method of emailing the help desk to reset a password is no longer valid and requests sent that way will not be answered. If the registered email address is no longer available, visit the IT office with a student card so that the identity can be checked in person. Passwords must contain at least twelve characters and should not be reused on other websites. Accounts are locked after five failed login attempts and are unlocked automatically after fifteen minutes. Students are encouraged to enable two step verification from the account settings page.",
    "assignment": "Assignment Submission Guide. Upload assignments through the learning portal using the submit button on the course page. Submit the final file as a PDF and name it with the course code followed by your student number. The portal accepts files up to twenty megabytes, so large images should be compressed before they are added to the document. Email submissions are not accepted for any course unless the instructor announces an exception in class. You may upload as many drafts as you like before the deadline, but only the latest version is marked and earlier versions are deleted by the system at the end of the semester. After the upload is finished, the portal displays a confirmation page with a receipt number, and students should save a screenshot of this page as proof. If the confirmation page does not appear, the upload has not worked and it must be repeated. Source code should be added as a separate zip file next to the report.",
    "contractor": "Remote Work Policy. Employees may request remote work for up to two days each week with manager approval, and the request must be renewed every six months. Contractors can work remotely only if the signed contract permits it. Employee rules do not apply to contractors, and managers cannot grant remote work to a contractor by email or verbal agreement. Remote workers must be available during core hours, which are ten in the morning to three in the afternoon. All company laptops used outside the office must have disk encryption turned on and must connect through the approved virtual private network. Confidential documents should never be printed at home or saved on personal devices. Equipment problems should be reported to the IT help desk, and the company does not pay for home internet costs unless a separate allowance has been approved. Employees who work remotely are still covered by the same health and safety rules as office staff. The human resources team reviews this policy every year.",
    "printer": "Printer Troubleshooting Guide. For blank printer pages, check ink levels and run the cleaning utility. Print a test page afterwards to see whether the problem is fixed, and repeat the cleaning step once more if the page is still faint. Blank pages can also appear when the protective tape has not been removed from a new cartridge or when the cartridge is not fully seated in its holder. Paper jams are a different problem and should be cleared by pulling the sheet out slowly in the direction of the paper path, never by force. Turn the printer off and unplug it before opening any internal cover. If the printer has power but still produces blank pages after the test page, contact the technician and give the model number found on the back label. Scanners are not covered in this guide and have their own instructions. Printing a large number of pages at once may overheat the device, so allow a short rest between long jobs.",
}

queries = [
    {"query": "What is required for illness extensions?", "doc": "late", "evidence": "Illness extensions require medical evidence before the deadline.", "split": "dev"},
    {"query": "How do I reset a forgotten password?", "doc": "password", "evidence": "Reset a forgotten password using the recovery link on the login page.", "split": "dev"},
    {"query": "Where do I upload assignments?", "doc": "assignment", "evidence": "Upload assignments through the learning portal using the submit button on the course page.", "split": "dev"},
    {"query": "Can contractors work remotely?", "doc": "contractor", "evidence": "Contractors can work remotely only if the signed contract permits it.", "split": "dev"},
    {"query": "What do I do for blank printer pages?", "doc": "printer", "evidence": "For blank printer pages, check ink levels and run the cleaning utility.", "split": "test"},
    {"query": "How can I recover my login access?", "doc": "password", "evidence": "Reset a forgotten password using the recovery link on the login page.", "split": "test"},
    {"query": "How should I hand in my coursework?", "doc": "assignment", "evidence": "Upload assignments through the learning portal using the submit button on the course page.", "split": "test"},
    {"query": "What proof is needed when I was ill?", "doc": "late", "evidence": "Illness extensions require medical evidence before the deadline.", "split": "test"},
    {"query": "What are tomorrow's flight prices?", "doc": None, "evidence": None, "split": "test"},
    {"query": "Who won the football match?", "doc": None, "evidence": None, "split": "test"},
]


def windows(text, size=40, overlap=10, offset=0):
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Require size > 0 and 0 <= overlap < size")
    spans = [(m.start(), m.end()) for m in re.finditer(r"\S+", text)]
    result = []
    for i in range(0, len(spans), size - overlap):
        j = min(i + size, len(spans))
        result.append((offset + spans[i][0], offset + spans[j - 1][1]))
        if j == len(spans):
            break
    return result


def sentence_chunks(text, size=40):
    cuts = [0]
    for m in re.finditer(r"[.!?]\s+", text):
        cuts.append(m.end())
    cuts.append(len(text))
    out = []
    pending = None
    count = 0
    for a, b in zip(cuts, cuts[1:]):
        n = len(text[a:b].split())
        if n == 0:
            continue
        if n > size:
            if pending is not None:
                out.append(pending)
            out.extend(windows(text[a:b], size, 0, a))
            pending = None
            count = 0
        elif pending is not None and count + n <= size:
            pending = (pending[0], b)
            count = count + n
        else:
            if pending is not None:
                out.append(pending)
            pending = (a, b)
            count = n
    if pending is not None:
        out.append(pending)
    return out


def make_chunks(documents, strategy):
    result = []
    for doc_id, text in documents.items():
        if strategy == "sentence":
            spans = sentence_chunks(text)
        else:
            spans = windows(text, 40, int(strategy))
        for i, (a, b) in enumerate(spans):
            result.append({"id": doc_id + ":" + str(i), "doc": doc_id, "start": a, "end": b, "text": text[a:b]})
    return result


def get_scores(method, texts, query_texts):
    if method == "tfidf":
        vec = TfidfVectorizer()
        C = vec.fit_transform(texts)
        Q = vec.transform(query_texts)
        return (Q @ C.T).toarray()
    C = model.encode(texts, normalize_embeddings=True)
    Q = model.encode(query_texts, normalize_embeddings=True)
    return Q @ C.T


def top3(row):
    return [int(i) for i in np.argsort(-row, kind="stable")[:3]]


def is_good(chunk, q):
    return chunk["doc"] == q["doc"] and q["evidence"] in chunk["text"]


def ranks_of(row, chunks, q):
    ranks = []
    for rank, i in enumerate(top3(row), 1):
        if is_good(chunks[i], q):
            ranks.append(rank)
    return ranks


def evaluate(scores, chunks, items):
    hits = []
    rr = []
    for row, q in zip(scores, items):
        if q["doc"] is None:
            continue
        ranks = ranks_of(row, chunks, q)
        hits.append(1 if ranks else 0)
        rr.append(1 / ranks[0] if ranks else 0)
    return float(np.mean(hits)), float(np.mean(rr))


print("===== TASK 1: TOKENS =====")
samples = ["AI, search!", "I can't log in.", "help@example.com", "CS4944", "", "یہ ایک مثال ہے", "2.1 version 4944CS"]
for text in samples:
    ws = text.split()
    words = re.findall(r"\b\w+\b", text)
    print("Original:", repr(text))
    print("  Whitespace:", ws, len(ws))
    print("  Word-like :", words, len(words))
if model is not None:
    for text in samples[:2]:
        print("Model tokens:", text, model.tokenizer.tokenize(text))
else:
    print("Model tokenizer not available on this computer")

print()
print("===== TASK 1: FAQ CHATBOT =====")
faq = [
    {"question": "How do I reset my password?", "answer": "Use the recovery link on the login page.", "source": "it_help.txt"},
    {"question": "Where do I submit my assignment?", "answer": "Use the assignment upload page in the learning portal.", "source": "assessment.txt"},
    {"question": "Can illness justify a late submission?", "answer": "Request an extension with medical evidence before the deadline.", "source": "handbook.txt"},
    {"question": "What are the library opening hours?", "answer": "The library is open from 8 am to 8 pm on weekdays.", "source": "library.txt"},
    {"question": "How do I connect to the campus wifi?", "answer": "Select the campus network and log in with your student account.", "source": "it_help.txt"},
]
faq_texts = []
for f in faq:
    faq_texts.append(f["question"] + " " + f["answer"])


def reply(query):
    if query.strip() == "":
        return "Please enter a question."
    for f in faq:
        if query.strip().lower() == f["question"].lower():
            return f["answer"] + " [source: " + f["source"] + "]"
    scores = get_scores("tfidf", faq_texts, [query])[0]
    if scores.max() == 0:
        return "No matching FAQ. Please contact the help desk."
    lines = ["Possible matches; choose or rephrase your question:"]
    for i in np.argsort(-scores)[:3]:
        if scores[i] > 0:
            lines.append("  " + faq[i]["question"] + " (similarity " + str(round(float(scores[i]), 3)) + ")")
    return "\n".join(lines)


for q in ["How do I reset my password?", "How do I connect to the campus wifi?", "password recovery", "", "volcano geology"]:
    print("You:", q)
    print("Bot:", reply(q))

print()
print("===== TASK 2: CHUNKING =====")
for doc_id in docs:
    print(doc_id, "words:", len(docs[doc_id].split()))

print("Edge case tests:")
print("  empty text ->", windows(""))
print("  short text ->", windows("short text"))
try:
    windows("a b", 2, 2)
except ValueError as e:
    print("  invalid overlap -> ValueError:", e)
long_sentence = " ".join(["word"] * 95) + "."
parts = sentence_chunks(long_sentence)
print("  95 word sentence ->", len(parts), "chunks, sizes", [len(long_sentence[a:b].split()) for a, b in parts])
pieces = re.split(r"(?<=[.!?])\s+", docs["late"])
for i, piece in enumerate(pieces):
    if piece.endswith("Dr."):
        print("  abbreviation split:", repr(piece), "|", repr(pieces[i + 1][:30]))

print("Comparison (40 word budget):")
total_words = sum(len(t.split()) for t in docs.values())
for strategy in ["0", "10", "sentence"]:
    chunks = make_chunks(docs, strategy)
    sizes = []
    for c in chunks:
        assert c["text"] == docs[c["doc"]][c["start"]:c["end"]]
        sizes.append(len(c["text"].split()))
    evidences = []
    for q in queries:
        if q["doc"] is not None and q["evidence"] not in evidences:
            evidences.append(q["evidence"])
    kept = 0
    for e in evidences:
        for c in chunks:
            if e in c["text"]:
                kept = kept + 1
                break
    print("  strategy", strategy, "| chunks:", len(chunks), "| avg words:", round(sum(sizes) / len(sizes), 1), "| max words:", max(sizes), "| repeated words:", sum(sizes) - total_words, "| evidence kept whole:", kept, "of", len(evidences))

print()
print("Semantic suggestions (sentence chunks):")
sent_chunks = make_chunks(docs, "sentence")
sent_texts = [c["text"] for c in sent_chunks]
para = ["How can I regain access to my account?", "How should I hand in my coursework?", "Can freelancers work from home?"]
methods = ["tfidf"]
if model is not None:
    methods.append("embedding")
for method in methods:
    scores = get_scores(method, sent_texts, para)
    for q, row in zip(para, scores):
        i = top3(row)[0]
        print(" ", method, "|", q, "->", sent_chunks[i]["id"], round(float(row[i]), 3))
if model is None:
    print("  embedding: not run (sentence-transformers model not available)")

print()
print("===== TASK 3: RETRIEVAL EVALUATION =====")
query_texts = [q["query"] for q in queries]
if model is not None:
    print("Model load seconds:", round(load_time, 2))
    for strategy in ["0", "10", "sentence"]:
        texts = [c["text"] for c in make_chunks(docs, strategy)] + query_texts
        lengths = [len(model.tokenizer(t, truncation=False)["input_ids"]) for t in texts]
        print("Token audit strategy", strategy, "| longest:", max(lengths), "| limit:", model.max_seq_length)
else:
    print("Token audit: not run (model not available)")

dev_idx = [i for i, q in enumerate(queries) if q["split"] == "dev"]
test_idx = [i for i, q in enumerate(queries) if q["split"] == "test"]
results = {}
store = {}
log = []
for strategy in ["0", "10", "sentence"]:
    chunks = make_chunks(docs, strategy)
    texts = [c["text"] for c in chunks]
    for method in methods:
        t0 = time.perf_counter()
        scores = get_scores(method, texts, query_texts)
        seconds = time.perf_counter() - t0
        dev = evaluate(scores[dev_idx], chunks, [queries[i] for i in dev_idx])
        test = evaluate(scores[test_idx], chunks, [queries[i] for i in test_idx])
        results[(strategy, method)] = (dev, test)
        store[(strategy, method)] = (chunks, scores)
        print("Strategy", strategy, "|", method, "| chunks:", len(chunks), "| time:", round(seconds, 4), "s")
        print("   dev  Hit@3 =", round(dev[0], 3), " MRR@3 =", round(dev[1], 3))
        print("   test Hit@3 =", round(test[0], 3), " MRR@3 =", round(test[1], 3))
        for q, row in zip(queries, scores):
            for rank, i in enumerate(top3(row), 1):
                c = chunks[i]
                log.append({"strategy": strategy, "method": method, "query": q["query"], "split": q["split"], "rank": rank, "score": round(float(row[i]), 4), "chunk_id": c["id"], "start": c["start"], "end": c["end"], "text": c["text"], "answerable": q["doc"] is not None})

with open("retrieval_log.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(log[0]))
    writer.writeheader()
    writer.writerows(log)
print("Log saved to retrieval_log.csv")

best = None
for key in results:
    if best is None or results[key][0][1] > results[best][0][1]:
        best = key
print()
print("Selected on dev MRR:", best, "| dev:", results[best][0], "| held-out test:", results[best][1])

chunks, scores = store[best]
print()
print("Failed answerable queries for selected setting:")
for q, row in zip(queries, scores):
    if q["doc"] is not None and not ranks_of(row, chunks, q):
        i = top3(row)[0]
        print(" ", q["query"], "| top chunk:", chunks[i]["id"], "| score:", round(float(row[i]), 3))
        print("    top text:", chunks[i]["text"][:90])

print()
print("Unanswerable queries (top result still returned if score > 0):")
for q, row in zip(queries, scores):
    if q["doc"] is None:
        i = top3(row)[0]
        print(" ", q["query"], "->", chunks[i]["id"], "score:", round(float(row[i]), 3))

print()
print("===== TASK 3: DOCUMENT CHATBOT =====")
chosen_method = best[1]


def doc_reply(query):
    if query.strip() == "":
        return ["Please enter a question."]
    row = get_scores(chosen_method, [c["text"] for c in chunks], [query])[0]
    if row.max() <= 0:
        return ["No candidate evidence; rephrase or contact a human."]
    lines = ["Candidate evidence; relevance must be checked:"]
    for n, i in enumerate(top3(row), 1):
        c = chunks[i]
        lines.append("  " + str(n) + " " + c["id"] + " score=" + str(round(float(row[i]), 3)) + " characters " + str(c["start"]) + "-" + str(c["end"]))
    return lines


for q in ["Can contractors work remotely?", "", "Who won the football match?"]:
    print("Question:", q)
    for line in doc_reply(q):
        print(line)

row = get_scores(chosen_method, [c["text"] for c in chunks], ["Can contractors work remotely?"])[0]
c = chunks[top3(row)[0]]
print("User chooses 1")
print("Retrieved passage:", c["text"])
print("Source:", c["doc"], "characters", c["start"], c["end"])
