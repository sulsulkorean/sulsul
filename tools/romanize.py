"""Revised Romanization of Hangul, computed rather than guessed.

GPT invents plausible-looking romanization with real errors (예 as "yae",
있어요 as "it-seo-yo"), and wrong pronunciation is worse for a Korean speaking
product than a thin post. So the code owns this, the way it owns cover images.
"""

BASE = 0xAC00
LAST = 0xD7A3

ONSETS = [
    "g", "kk", "n", "d", "tt", "r", "m", "b", "pp",
    "s", "ss", "", "j", "jj", "ch", "k", "t", "p", "h",
]
VOWELS = [
    "a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa",
    "wae", "oe", "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i",
]
# Jamo names for the 28 final slots (index 0 = no final).
CODA_JAMO = [
    "", "g", "kk", "gs", "n", "nj", "nh", "d", "l", "lg", "lm",
    "lb", "ls", "lt", "lp", "lh", "m", "b", "bs", "s", "ss",
    "ng", "j", "c", "k", "t", "p", "h",
]
# How a final is pronounced when nothing follows it.
CODA_FINAL = {
    "": "", "g": "k", "kk": "k", "gs": "k", "n": "n", "nj": "n", "nh": "n",
    "d": "t", "l": "l", "lg": "k", "lm": "m", "lb": "p", "ls": "l",
    "lt": "l", "lp": "p", "lh": "l", "m": "m", "b": "p", "bs": "p",
    "s": "t", "ss": "t", "ng": "ng", "j": "t", "c": "t", "k": "k",
    "t": "t", "p": "p", "h": "t",
}
# A two-consonant final keeps one sound and hands the other to the next
# syllable when that syllable starts with a vowel.
CLUSTER_SPLIT = {
    "gs": ("k", "s"), "nj": ("n", "j"), "nh": ("n", ""), "lg": ("l", "g"),
    "lm": ("l", "m"), "lb": ("l", "b"), "ls": ("l", "s"), "lt": ("l", "t"),
    "lp": ("l", "p"), "lh": ("l", ""), "bs": ("p", "s"),
}
# Coda + next onset -> (coda sound, onset sound). Only the rules that actually
# show up in everyday speech; anything unlisted falls through unchanged.
ASSIMILATION = {
    ("k", "n"): ("ng", "n"), ("k", "m"): ("ng", "m"), ("k", "r"): ("ng", "n"),
    ("t", "n"): ("n", "n"), ("t", "m"): ("n", "m"), ("t", "r"): ("n", "n"),
    ("p", "n"): ("m", "n"), ("p", "m"): ("m", "m"), ("p", "r"): ("m", "n"),
    ("n", "r"): ("l", "l"), ("l", "n"): ("l", "l"),
    ("ng", "r"): ("ng", "n"), ("m", "r"): ("m", "n"),
    ("h", "g"): ("", "k"), ("h", "d"): ("", "t"), ("h", "j"): ("", "ch"),
    ("h", "s"): ("", "ss"), ("h", "n"): ("n", "n"),
}


COMPOUND_OVERRIDES = {
    "지하철역": "jihacheollyeok",
    "학여울": "hangnyeoul",
    "알약": "allyak",
    "꽃잎": "kkonnip",
    "색연필": "saengnyeonpil",
    "서울역": "seoullyeok",
    "종착역": "jongchangnyeok",
    "신문로": "sinmunno",
}


def _decompose(ch):
    code = ord(ch) - BASE
    return code // 588, (code % 588) // 28, code % 28


def is_hangul(ch):
    return BASE <= ord(ch) <= LAST


def romanize(text):
    """Romanize the Hangul runs in text, leaving everything else untouched."""
    out = []
    run = []
    for ch in text:
        if is_hangul(ch):
            run.append(ch)
        else:
            if run:
                out.append(_romanize_run(run))
                run = []
            out.append(ch)
    if run:
        out.append(_romanize_run(run))
    return "".join(out)


def _romanize_run(chars):
    word = "".join(chars)
    if word in COMPOUND_OVERRIDES:
        return COMPOUND_OVERRIDES[word]
    syls = [_decompose(c) for c in chars]
    onsets = [ONSETS[s[0]] for s in syls]
    vowels = [VOWELS[s[1]] for s in syls]
    codas = [CODA_JAMO[s[2]] for s in syls]

    for i in range(len(syls) - 1):
        coda = codas[i]
        if not coda:
            continue
        # Next syllable starts with a vowel: the final moves across.
        if onsets[i + 1] == "":
            if coda == "h":
                codas[i] = ""
                continue
            if coda in CLUSTER_SPLIT:
                keep, move = CLUSTER_SPLIT[coda]
                codas[i] = keep
                onsets[i + 1] = move
            else:
                codas[i] = ""
                onsets[i + 1] = "r" if coda == "l" else coda
            continue

        nxt = onsets[i + 1]
        # Match on the written final first: ㅎ is neutralised to "t" in
        # isolation, which would hide the ㅎ+ㄱ and ㅎ+ㄷ rules (joko, nota).
        if (coda, nxt) in ASSIMILATION:
            sound, nxt = ASSIMILATION[(coda, nxt)]
        else:
            sound = CODA_FINAL.get(coda, coda)
            if (sound, nxt) in ASSIMILATION:
                sound, nxt = ASSIMILATION[(sound, nxt)]
        codas[i] = sound
        onsets[i + 1] = nxt

    codas[-1] = CODA_FINAL.get(codas[-1], codas[-1])
    return "".join(o + v + c for o, v, c in zip(onsets, vowels, codas))


# --- Numbers -----------------------------------------------------------------
# "2호선" has to be read 이호선, but "2잔" is 두 잔. Which set of numerals wins
# depends on the counter that follows, so only convert when the counter is known
# and leave the digits alone otherwise.

SINO_DIGITS = ["", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
NATIVE_ATTRIBUTIVE = {
    1: "한", 2: "두", 3: "세", 4: "네", 5: "다섯", 6: "여섯",
    7: "일곱", 8: "여덟", 9: "아홉", 10: "열", 11: "열한", 12: "열두",
    20: "스무", 30: "서른", 40: "마흔",
}
SINO_COUNTERS = [
    "호선", "인분", "원", "번", "호", "층", "분", "월", "일", "년",
    "시간", "개월", "퍼센트", "%",
]
NATIVE_COUNTERS = [
    "개", "잔", "병", "명", "마리", "그릇", "권", "살", "컵", "시", "사람",
]


def sino_number(n):
    if n == 0:
        return "영"
    parts = []
    for unit, name in ((10000, "만"), (1000, "천"), (100, "백"), (10, "십")):
        q, n = divmod(n, unit)
        if q:
            # A leading 1 is silent: 만 원, 백 명, not 일만 / 일백.
            head = "" if q == 1 else sino_number(q)
            parts.append(head + name)
    if n:
        parts.append(SINO_DIGITS[n])
    return "".join(parts)


def native_number(n):
    if n in NATIVE_ATTRIBUTIVE:
        return NATIVE_ATTRIBUTIVE[n]
    if 10 < n < 20:
        return "열" + NATIVE_ATTRIBUTIVE.get(n - 10, sino_number(n - 10))
    return None


_COUNTER_ALT = "|".join(
    sorted(SINO_COUNTERS + NATIVE_COUNTERS, key=len, reverse=True)
)
NUMBER_RE = __import__("re").compile(
    r"(\d[\d,]*)\s*(" + _COUNTER_ALT + r")"
)


def spell_numbers(text):
    """Replace digit+counter with the Korean reading, when the counter tells us
    which numeral set applies."""
    def sub(m):
        raw, counter = m.group(1), m.group(2)
        n = int(raw.replace(",", ""))
        if counter in NATIVE_COUNTERS:
            word = native_number(n)
            if word is None:
                return m.group(0)
            return f"{word} {counter}"
        return f"{sino_number(n)}{counter}"

    return NUMBER_RE.sub(sub, text)
