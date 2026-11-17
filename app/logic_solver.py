import itertools
import re
from typing import Any

# Supports the operators used in the course material.
_TOKEN_RE = re.compile(r"<->|<=>|↔|⊕|\bXOR\b|->|→|=>|[A-Da-d]|[()]|[&∧*]|[|∨]|[Vv]|[~¬!]")


class LogicSyntaxError(ValueError):
    pass


def _normalize(expression: str) -> str:
    expression = expression.strip()
    expression = re.sub(r"^[a-iA-I]\s*[).:-]\s*", "", expression)
    expression = expression.replace("−", "-").replace("–", "-")
    expression = expression.replace("⟷", "↔").replace("⇔", "↔").replace("⇒", "→")
    expression = expression.replace("≡", "↔")
    expression = re.sub(r"\b(?:xor)\b", "⊕", expression, flags=re.IGNORECASE)
    expression = re.sub(r"\b[vV]\b", "∨", expression)
    expression = re.sub(r"(?<![<>=])-(?=\s*[A-Da-d(])", "¬", expression)
    # The handout may use lowercase a,b,c,d for logical variables.
    expression = re.sub(r"\b([a-d])\b", lambda match: match.group(1).upper(), expression)
    return expression


class _Parser:
    def __init__(self, expression: str):
        self.tokens = [match.group(0) for match in _TOKEN_RE.finditer(_normalize(expression))]
        self.position = 0
        if not self.tokens:
            raise LogicSyntaxError("No logical expression found")

    def _peek(self) -> str | None:
        return self.tokens[self.position] if self.position < len(self.tokens) else None

    def _take(self) -> str:
        token = self._peek()
        if token is None:
            raise LogicSyntaxError("Unexpected end of expression")
        self.position += 1
        return token

    def parse(self) -> Any:
        tree = self._equivalence()
        if self._peek() is not None:
            raise LogicSyntaxError(f"Unexpected token: {self._peek()}")
        return tree

    def _equivalence(self) -> Any:
        node = self._implication()
        while self._peek() in ("↔", "<->", "<=>"):
            self._take()
            node = ("iff", node, self._implication())
        return node

    def _implication(self) -> Any:
        node = self._disjunction()
        if self._peek() in ("→", "->", "=>"):
            self._take()
            return ("implies", node, self._implication())
        return node

    def _disjunction(self) -> Any:
        node = self._xor()
        while self._peek() in ("∨", "|"):
            self._take()
            node = ("or", node, self._xor())
        return node

    def _xor(self) -> Any:
        node = self._conjunction()
        while self._peek() in ("⊕", "XOR"):
            self._take()
            node = ("xor", node, self._conjunction())
        return node

    def _conjunction(self) -> Any:
        node = self._unary()
        while self._peek() in ("&", "∧", "*"):
            self._take()
            node = ("and", node, self._unary())
        return node

    def _unary(self) -> Any:
        token = self._peek()
        if token in ("¬", "~", "!"):
            self._take()
            return ("not", self._unary())
        if token == "(":
            self._take()
            node = self._equivalence()
            if self._take() != ")":
                raise LogicSyntaxError("Missing closing parenthesis")
            return node
        if token and token.upper() in "ABCD" and len(token) == 1:
            self._take()
            return ("var", token.upper())
        raise LogicSyntaxError(f"Expected a variable or parenthesis, got {token!r}")


def _evaluate(tree: Any, values: dict[str, bool]) -> bool:
    operation = tree[0]
    if operation == "var":
        return values[tree[1]]
    if operation == "not":
        return not _evaluate(tree[1], values)
    left = _evaluate(tree[1], values)
    right = _evaluate(tree[2], values)
    if operation == "and":
        return left and right
    if operation == "or":
        return left or right
    if operation == "xor":
        return left != right
    if operation == "implies":
        return not left or right
    if operation == "iff":
        return left == right
    raise LogicSyntaxError("Unknown logical operation")


def _format_expression(expression: str) -> str:
    cleaned = _normalize(expression)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.replace("->", "→").replace("<->", "↔").replace("&", "∧")
    return cleaned.strip(" ;,.\t")


def solve_expression(expression: str) -> str:
    parser = _Parser(expression)
    tree = parser.parse()
    variables = sorted(set(re.findall(r"[A-D]", _normalize(expression).upper())))
    if not variables or len(variables) > 4:
        raise LogicSyntaxError("Expression must contain 1–4 variables (A–D)")

    header = " ".join(variables) + " | F"
    rows = [header, "-" * len(header)]
    result_values: list[str] = []
    for bits in itertools.product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        output = _evaluate(tree, assignment)
        result_values.append("1" if output else "0")
        rows.append(" ".join("1" if bit else "0" for bit in bits) + " | " + ("1" if output else "0"))

    return (
        f"<b>{_format_expression(expression)}</b>\n"
        f"<pre>{'&#10;'.join(rows)}</pre>"
        f"Yakuniy qiymatlar: <code>{''.join(result_values)}</code>"
    )


def solve_logic_text(text: str) -> list[str]:
    """Find and solve logical-formula lines in OCR or user-provided text."""
    answers: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        # Avoid parsing the XOR/implication definitions often printed above exercises.
        if "=" in line:
            continue
        for candidate in re.split(r";", line):
            normalized = _normalize(candidate)
            if not any(operator in normalized for operator in ("&", "∧", "∨", "→", "->", "↔", "⊕", "¬", "~")):
                continue
            if len(set(re.findall(r"[A-D]", normalized.upper()))) < 2:
                continue
            key = re.sub(r"\s+", "", normalized).lower()
            if key in seen:
                continue
            try:
                answer = solve_expression(candidate)
            except LogicSyntaxError:
                continue
            seen.add(key)
            answers.append(answer)
    return answers
