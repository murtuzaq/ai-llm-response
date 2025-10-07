
import re

def strip_code_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else ""
        if s.rstrip().endswith("```"):
            s = s.rsplit("```", 1)[0]
    return s.strip()

def extract_json_region(s: str) -> str:
    start_obj = s.find("{")
    start_arr = s.find("[")
    starts = [i for i in [start_obj, start_arr] if i != -1]
    if not starts:
        return s
    start = min(starts)
    end_obj = s.rfind("}")
    end_arr = s.rfind("]")
    ends = [i for i in [end_obj, end_arr] if i != -1]
    if not ends:
        return s[start:]
    end = max(ends)
    return s[start:end+1]

def remove_trailing_commas(s: str) -> str:
    return re.sub(r",(\s*[}\]])", r"\1", s)

def balance_brackets(s: str) -> str:
    out, stack = [], []
    in_str = False
    esc = False
    quote_char = None
    for ch in s:
        out.append(ch)
        if in_str:
            if esc:
                esc = False
                continue
            if ch == "\\":
                esc = True
                continue
            if ch == quote_char:
                in_str = False
            continue
        if ch in ("\"", "'"):
            in_str = True
            quote_char = ch
            continue
        if ch == "{":
            stack.append("}")
        elif ch == "[":
            stack.append("]")
        elif ch in ("}", "]"):
            if stack and stack[-1] == ch:
                stack.pop()
            else:
                out.pop()
    while stack:
        out.append(stack.pop())
    return "".join(out)

def repair_json_structure(text: str) -> str:
    if not isinstance(text, str):
        try:
            text = str(text)
        except Exception:
            return ""
    s = strip_code_fences(text)
    s = extract_json_region(s)
    s = remove_trailing_commas(s)
    s = balance_brackets(s)
    s = remove_trailing_commas(s)
    return s.strip()
