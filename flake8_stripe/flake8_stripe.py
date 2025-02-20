# Hint: if you're developing this plugin, test changes with:
#   venv/bin/tox -e lint -r
# so that tox re-installs the plugin from the local directory
import ast
from typing import Iterator, Tuple


class TypingImportsChecker:
    name = __name__
    version = "0.1.0"

    # Rules:
    # * typing_extensions v4.1.1 is the latest that supports Python 3.6
    # so don't depend on anything from a more recent version than that.
    #
    # If we need something newer, maybe we can provide it for users on
    # newer versions with a conditional import, but we'll cross that
    # bridge when we come to it.

    # If a symbol exists in both `typing` and `typing_extensions`, which
    # should you use? Prefer `typing_extensions` if the symbol available there.
    # in 4.1.1. In typing_extensions 4.7.0, `typing_extensions` started re-exporting
    # EVERYTHING from `typing` but this is not the case in v4.1.1.
    allowed_typing_extensions_imports = [
        "Literal",
        "NoReturn",
        "Protocol",
        "TYPE_CHECKING",
        "Type",
        "TypedDict",
        "Self",
    ]

    allowed_typing_imports = [
        "Any",
        "ClassVar",
        "Optional",
        "TypeVar",
        "Union",
        "cast",
        "overload",
        "Dict",
        "List",
        "Generic",
    ]

    def __init__(self, tree: ast.AST):
        self.tree = tree

        intersection = set(self.allowed_typing_imports) & set(
            self.allowed_typing_extensions_imports
        )
        if len(intersection) > 0:
            raise AssertionError(
                "TypingImportsChecker: allowed_typing_imports and allowed_typing_extensions_imports must not overlap. Both entries contained: %s"
                % (intersection)
            )

    def run(self) -> Iterator[Tuple[int, int, str, type]]:
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "typing":
                    for name in node.names:
                        if name.name not in self.allowed_typing_imports:
                            msg = None
                            if (
                                name.name
                                in self.allowed_typing_extensions_imports
                            ):
                                msg = (
                                    "SPY100 Don't import %s from 'typing', instead import from 'typing_extensions'"
                                    % (name.name)
                                )
                            else:
                                msg = (
                                    "SPY101 Importing %s from 'typing' is prohibited. Do you need to add to the allowlist in flake8_stripe.py?"
                                    % (name.name)
                                )
                            yield (
                                name.lineno,
                                name.col_offset,
                                msg,
                                type(self),
                            )
                elif node.module == "typing_extensions":
                    for name in node.names:
                        if (
                            name.name
                            not in self.allowed_typing_extensions_imports
                        ):
                            msg = None
                            if name.name in self.allowed_typing_imports:
                                msg = (
                                    "SPY102 Don't import '%s' from 'typing_extensions', instead import from 'typing'"
                                    % (name.name)
                                )
                            else:
                                msg = (
                                    "SPY103 Importing '%s' from 'typing_extensions' is prohibited. Do you need to add to the allowlist in flake8_stripe.py?"
                                    % (name.name)
                                )
                            yield (
                                name.lineno,
                                name.col_offset,
                                msg,
                                type(self),
                            )
