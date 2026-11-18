import html
import itertools
import re
from typing import Any

# Supports the operators used in the course material.
_TOKEN_RE = re.compile(r"<->|<=>|↔|⊕|\bXOR\b|->|→|=>|[A-Da-d]|[()]|[&∧*]|[|∨]|[Vv]|[~¬!]")
_OPERATORS = ("&", "∧", "*", "∨", "|", "→", "->", "↔", "<->", "<=>", "⊕", "¬", "~", "!")
_OP_SYMBOL = {
    "not": "¬",
    "and": "∧",
    "or": "∨",
    "xor": "⊕",
    "implies": "→",
    "iff": "↔",
}


class LogicSyntaxError(ValueError):
    pass


def _normalize(expression: str) -> str:
    expression = expression.strip()
    # Strip exercise labels such as "a)" or "1.", but never the minus in "A -> B".
    expression = re.sub(r"^(?:[a-iA-I]|\d+)\s*[).:]\s*", "", expression)
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


def _label(tree: Any) -> str:
    operation = tree[0]
    if operation == "var":
        return tree[1]
    if operation == "not":
        inner = _label(tree[1])
        if tree[1][0] == "var":
            return "¬" + inner
        return "¬(" + inner + ")"
    left = _label(tree[1])
    right = _label(tree[2])
    if tree[1][0] not in ("var", "not"):
        left = "(" + left + ")"
    if tree[2][0] not in ("var", "not"):
        right = "(" + right + ")"
    return left + _OP_SYMBOL[operation] + right


def _variables(tree: Any) -> list[str]:
    found: set[str] = set()

    def walk(node: Any) -> None:
        if node[0] == "var":
            found.add(node[1])
        elif node[0] == "not":
            walk(node[1])
        else:
            walk(node[1])
            walk(node[2])

    walk(tree)
    return sorted(found)


def _steps(tree: Any) -> list[tuple[str, Any]]:
    steps: list[tuple[str, Any]] = []

    def walk(node: Any) -> None:
        if node[0] == "var":
            return
        if node[0] == "not":
            walk(node[1])
        else:
            walk(node[1])
            walk(node[2])
        label = "F" if node is tree else _label(node)
        if all(existing != label for existing, _ in steps):
            steps.append((label, node))

    walk(tree)
    return steps


def _why_false(tree: Any) -> str:
    operation = tree[0]
    if operation == "implies":
        return "Implikatsiya faqat chap tomon 1, o'ng tomon 0 bo'lganda 0 bo'ladi."
    if operation == "and":
        return "Kesishma 0, chunki ikkala tomon ham 1 bo'lishi shart."
    if operation == "or":
        return "Yig'indi 0, chunki ikkala tomon ham 0."
    if operation == "xor":
        return "XOR 0, chunki ikkala tomon teng."
    if operation == "iff":
        return "Ekvivalentlik 0, chunki tomonlar teng emas."
    if operation == "not":
        return "Inkor qiymatni teskarisiga o'giradi."
    return ""


def _esc(text: str) -> str:
    return html.escape(text, quote=False)


def _format_expression(expression: str) -> str:
    cleaned = _normalize(expression)
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.replace("<=>", "↔").replace("<->", "↔").replace("->", "→").replace("&", "∧")
    return cleaned.strip(" ;,.\t")


def solve_expression(expression: str) -> str:
    parser = _Parser(expression)
    tree = parser.parse()
    variables = _variables(tree)
    if not variables or len(variables) > 4:
        raise LogicSyntaxError("Expression must contain 1–4 variables (A–D)")

    steps = _steps(tree)
    columns: list[tuple[str, list[str]]] = [(label, []) for label, _ in steps]
    variable_rows: list[list[str]] = []
    false_reason = ""
    for bits in itertools.product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        variable_rows.append(["1" if bit else "0" for bit in bits])
        for index, (_, node) in enumerate(steps):
            value = _evaluate(node, assignment)
            columns[index][1].append("1" if value else "0")
            if node is tree and not value and not false_reason:
                shown_bits = ", ".join(
                    f"{name}={bit}" for name, bit in zip(variables, variable_rows[-1])
                )
                false_reason = f"Birinchi 0 qator: {shown_bits}. {_why_false(tree)}"

    headers = variables + [label for label, _ in columns]
    widths = [len(header) for header in headers]

    def format_row(cells: list[str]) -> str:
        return " | ".join(cell.ljust(widths[index]) for index, cell in enumerate(cells))

    lines = [format_row(headers)]
    lines.append("-" * len(lines[0]))
    for row_index, bits in enumerate(variable_rows):
        cells = bits + [values[row_index] for _, values in columns]
        lines.append(format_row(cells))

    result_values = columns[-1][1]
    ones = result_values.count("1")
    total = len(result_values)
    if ones == total:
        verdict = "Tautologiya: har bir qatorda rost."
    elif ones == 0:
        verdict = "Ziddiyat: hech bir qatorda rost emas."
    else:
        verdict = f"Ba'zi hollarda rost: {ones} ta qatorda 1, {total - ones} ta qatorda 0."

    shown = _esc(_format_expression(expression))
    table = _esc("\n".join(lines))
    extra = f"\n{_esc(false_reason)}" if false_reason and ones not in (0, total) else ""
    if ones == 0 and false_reason:
        extra = f"\n{_esc(false_reason)}"
    return (
        f"<b>{shown}</b>\n"
        f"<pre>{table}</pre>\n"
        f"Yakuniy qiymatlar: <code>{''.join(result_values)}</code>\n"
        f"{_esc(verdict)}{extra}"
    )


def solve_logic_text(text: str) -> list[str]:
    """Find and solve logical-formula lines in OCR or user-provided text."""
    answers: list[str] = []
    seen: set[str] = set()
    for line in text.splitlines():
        for candidate in re.split(r";", line):
            normalized = _normalize(candidate)
            if not any(operator in normalized for operator in _OPERATORS):
                continue
            if len(set(re.findall(r"[A-D]", normalized.upper()))) < 1:
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
