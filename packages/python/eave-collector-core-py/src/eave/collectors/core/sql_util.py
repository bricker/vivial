import re
from typing import Any, Callable, ClassVar, Type, cast

import sqlparse

from eave.collectors.core.datastructures import DatabaseOperation
from eave.collectors.logging import EAVE_LOGGER


_TABLE_MATCHER = r"[`\"']?([a-zA-Z0-9_\.\-]+)[`\"']?"
_TABLE_MATCHER_FLAGS = re.IGNORECASE | re.MULTILINE
_LEADING_COMMENT_MATCHER = re.compile(r"^/\*.*?\*/")

class SQLStatementInspector:
    # This is _deliberately_ a global, shared dict. The default empty dict is not a mistake.
    _global_parsecache: ClassVar[dict[str, sqlparse.sql.Statement]] = {}

    _raw_statement: str
    _parsed_statement: sqlparse.sql.Statement | None
    __memo__: dict[str, Any]

    @classmethod
    def parse_sql_statement(cls, statement: str) -> sqlparse.sql.Statement | None:
        if statement in cls._global_parsecache:
            return cls._global_parsecache[statement]

        parsed = sqlparse.parse(statement)
        if len(parsed) == 0:
            return None

        parsed_stmt = cast(sqlparse.sql.Statement, parsed[0])
        cls._global_parsecache[statement] = parsed_stmt
        return parsed_stmt

    def __init__(self, statement: str) -> None:
        self.__memo__ = {}
        self._raw_statement = statement
        self._parsed_statement = SQLStatementInspector.parse_sql_statement(statement)

    def get_operation(self) -> DatabaseOperation | None:
        if not self._parsed_statement:
            return None

        memokey = "get_operation"
        if memokey in self.__memo__:
            return self.__memo__[memokey]

        optype = self._parsed_statement.get_type()

        v = DatabaseOperation.from_str(optype)
        self.__memo__[memokey] = v
        return v

    def get_table_name(self) -> str | None:
        if not self._parsed_statement:
            return None

        memokey = "get_table_name"
        if memokey in self.__memo__:
            return self.__memo__[memokey]

        def _memoize[T](v: T) -> T:
            self.__memo__[memokey] = v
            return v

        tablename = None

        # There are many cases where these simple algorithms won't work.
        # For example, it does nothing to handle nested queries or joins.
        # These algorithms should cover the most basic and common cases, and fail gracefully otherwise.
        match self.get_operation():
            case DatabaseOperation.INSERT:
                # Example: "INSERT INTO my_table ..."
                # The algorithm for INSERT is:
                # 1. Find the first Keyword token with value "INTO"
                # 1. Find the closest Identifier token following the "INTO" token.
                # 1. If no Identifier is found, look for the closest Function token following the "INTO" token.
                # 1. If a Function token is found, get the first child Identifier token.
                # 1. If an Identifier token has been acquired, this is assumed to be the table name.
                # 1. Return the Identifier's value.

                # INSERT >>INTO<< ...
                if (next_kw_token := self._first_token_of_ttype_with_idx(self._parsed_statement, ttype=sqlparse.tokens.Keyword, value="INTO")) is None: # case IN-sensitive
                    return _memoize(None)

                kw_idx, _kw_token = next_kw_token

                # INSERT INTO >>my_table<< VALUES (value, value, value)
                if (next_id_token := self._first_token_of_class(self._parsed_statement, tclass=sqlparse.sql.Identifier, start_idx=kw_idx)) is None:
                    # INSERT INTO >>my_table (column, column, column)<<< VALUES (value, value, value)
                    if (next_func_token := self._first_token_of_class(self._parsed_statement, tclass=sqlparse.sql.Function, start_idx=kw_idx)) is None:
                        return _memoize(None)

                    # INSERT INTO >>my_table<< (column, column, column) VALUES (value, value, value)
                    if (next_id_token := self._first_token_of_class(next_func_token, tclass=sqlparse.sql.Identifier)) is None:
                        return _memoize(None)

                tablename = next_id_token.value

            case DatabaseOperation.UPDATE:
                # Example: "UPDATE my_table ..."
                # The algorithm for UPDATE is:
                # 1. Find the first Identifier token. This is assumed to be the table identifier.
                # 1. Return the Identifier's value.
                if (next_id_token := self._first_token_of_class(self._parsed_statement, tclass=sqlparse.sql.Identifier)) is None:
                    return _memoize(None)

                tablename = next_id_token.value

            case DatabaseOperation.DELETE:
                # Example: "DELETE FROM my_table ..."
                # The algorithm for DELETE is:
                # 1. Find the first Keyword token with value "FROM"
                # 1. Find the closest Identifier token following the "FROM" token. This is assumed to be the table identifier.
                # 1. Return the Identifier's value.
                if (next_kw_token := self._first_token_of_ttype_with_idx(self._parsed_statement, ttype=sqlparse.tokens.Keyword, value="FROM")) is None: # case IN-sensitive
                    return _memoize(None)

                kw_idx, _kw_token = next_kw_token

                if (next_id_token := self._first_token_of_class(self._parsed_statement, tclass=sqlparse.sql.Identifier, start_idx=kw_idx)) is None:
                    return _memoize(None)

                tablename = next_id_token.value

            case DatabaseOperation.SELECT:
                # Example: "SELECT a,b,c FROM my_table ..."
                # The algorithm for SELECT is:
                # 1. Find the first Keyword token with value "FROM"
                # 1. Find the closest Identifier token following the "FROM" token. This is assumed to be the table identifier.
                # 1. Return the Identifier's value.
                if (next_kw_token := self._first_token_of_ttype_with_idx(self._parsed_statement, ttype=sqlparse.tokens.Keyword, value="FROM")) is None: # case IN-sensitive
                    return _memoize(None)

                kw_idx, _kw_token = next_kw_token

                if (next_id_token := self._first_token_of_class(self._parsed_statement, tclass=sqlparse.sql.Identifier, start_idx=kw_idx)) is None:
                    return _memoize(None)

                tablename = next_id_token.value

            case _:
                return _memoize(None)

        if not tablename:
            return _memoize(None)

        v = tablename.strip("\"'`")
        return _memoize(v)

    def get_insert_cols(self) -> list[str] | None:
        if not self.get_operation() == DatabaseOperation.INSERT:
            raise ValueError("get_insert_cols only applicable to INSERT statements")

        if not self._parsed_statement:
            return None

        memokey = "get_insert_cols"
        if memokey in self.__memo__:
            return self.__memo__[memokey]

        def _memoize[T](v: T) -> T:
            self.__memo__[memokey] = v
            return v

        # If a Function token is found, then columns were given.
        # sqlparse parses an INSERT statement this way (simplified for brevity here):

        # "INSERT INTO teams (name, updated) VALUES ($1::VARCHAR, $2::TIMESTAMP)"
        #
        #   |- 0 DML 'INSERT'
        #   |- 1 Whitespace ' '
        #   |- 2 Keyword 'INTO'
        #   |- 3 Whitespace ' '
        #   |- 4 Function 'teams ...'
        #   |  |- 0 Identifier 'teams'
        #   |  `- 2 Parenthesis '(name,...'
        #   |     |- 1 IdentifierList 'name, ...'
        #   |     |  |- 0 Identifier 'name'
        #   |     |  `- 3 Identifier 'updated'
        #   |- 6 Values 'VALUES...'
        #   |  |- 0 Keyword 'VALUES'
        #   |  `- 2 Parenthesis '($1::V...'
        #   |     |- 1 IdentifierList '$1::VA...'
        #   |     |  |- 0 Identifier '$1::VA...'
        #   |     |  |  |- 0 Placeholder '$1'
        #   |     |  |  |- 1 Punctuation '::'
        #   |     |  |  `- 2 Builtin 'VARCHAR'
        #   |     |  `- 3 Identifier '$2::TI...'
        #   |     |     |- 0 Placeholder '$2'
        #   |     |     |- 1 Punctuation '::'
        #   |     |     `- 2 Builtin 'TIMEST...'

        if (func_token := self._first_token_of_class(self._parsed_statement, tclass=sqlparse.sql.Function)) is None:
            # This is a normal case - it means no columns were specified, so the INSERT statement is implicitly giving values for all columns.
            return _memoize(None)

        # If a Function was found, then we traverse and grab the column names.
        if (paren_token := self._first_token_of_class(func_token, tclass=sqlparse.sql.Parenthesis)) is None:
            return _memoize(None)

        if (id_list_token := self._first_token_of_class(paren_token, tclass=sqlparse.sql.IdentifierList)) is None:
            return _memoize(None)

        id_tokens = self._excluding_tokens_of_ttypes(id_list_token, ttypes=(sqlparse.tokens.Whitespace, sqlparse.tokens.Punctuation))
        return [t.value for t in id_tokens]

    def get_update_cols(self) -> list[str] | None:
        if not self.get_operation() == DatabaseOperation.UPDATE:
            raise ValueError("get_update_cols only applicable to UPDATE statements")

        if not self._parsed_statement:
            return None

        memokey = "get_update_cols"
        if memokey in self.__memo__:
            return self.__memo__[memokey]

        def _memoize[T](v: T) -> T:
            self.__memo__[memokey] = v
            return v

        if (next_kw_token := self._first_token_of_ttype_with_idx(self._parsed_statement, ttype=sqlparse.tokens.Keyword, value="SET")) is None: # case IN-sensitive
            return _memoize(None)

        kw_idx, _kw_token = next_kw_token

        if (id_list_token := self._first_token_of_class(self._parsed_statement, tclass=sqlparse.sql.IdentifierList, start_idx=kw_idx)) is None:
            return _memoize(None)

        # Comparison class is unreliable. If parsing is done incorrectly, `left` and `right` may be missing.
        comp_tokens = self._matching_tokens_of_class(id_list_token, tclass=sqlparse.sql.Comparison)
        # This cast is for you
        cols = [cast(str, t.left.value) for t in comp_tokens]
        return cols

    # These are wrappers around some sqlparse utility functions, with some better support for typechecking
    def _excluding_tokens_of_classes(self, token_list: sqlparse.sql.TokenList, tclasses: tuple[Type[sqlparse.sql.Token], ...], start_idx: int = 0) -> list[sqlparse.sql.Token]:
        if len(token_list.tokens) <= start_idx:
            return []

        matches = [t for t in token_list.tokens[start_idx:] if not any(isinstance(t, c) for c in tclasses)]
        return matches

    def _matching_tokens_of_classes(self, token_list: sqlparse.sql.TokenList, tclasses: tuple[Type[sqlparse.sql.Token], ...], start_idx: int = 0) -> list[sqlparse.sql.Token]:
        if len(token_list.tokens) <= start_idx:
            return []

        matches = [t for t in token_list.tokens[start_idx:] if any(isinstance(t, c) for c in tclasses)]
        return matches

    def _matching_tokens_of_class[T: sqlparse.sql.Token](self, token_list: sqlparse.sql.TokenList, tclass: Type[T], start_idx: int = 0) -> list[T]:
        if len(token_list.tokens) <= start_idx:
            return []

        matches = [t for t in token_list.tokens[start_idx:] if isinstance(t, tclass)]
        return matches

    def _first_token_of_class[T: sqlparse.sql.Token](self, token_list: sqlparse.sql.TokenList, tclass: Type[T], start_idx: int = 0) -> T | None:
        v = self._first_token_of_class_with_idx(token_list=token_list, tclass=tclass, start_idx=start_idx)
        return None if v is None else v[1]

    def _first_token_of_class_with_idx[T: sqlparse.sql.Token](self, token_list: sqlparse.sql.TokenList, tclass: Type[T], start_idx: int = 0) -> tuple[int, T] | None:
        if len(token_list.tokens) <= start_idx:
            return None

        match = token_list.token_next_by(i=tclass, idx=start_idx - 1)
        if not match:
            return None

        i, t = match
        if i is None or t is None:
            return None

        return i, t

    def _excluding_tokens_of_ttypes(self, token_list: sqlparse.sql.TokenList, ttypes: tuple[sqlparse.tokens._TokenType, ...], start_idx: int = 0) -> list[sqlparse.sql.Token]:
        tokens = cast(list[sqlparse.sql.Token], token_list.tokens)

        if len(tokens) <= start_idx:
            return []

        matches = [t for t in tokens[start_idx:] if not any(t.match(ttype=ttype, values=None) for ttype in ttypes)]
        return matches

    def _matching_tokens_of_ttype(self, token_list: sqlparse.sql.TokenList, ttype: sqlparse.tokens._TokenType, value: str | None = None, start_idx: int = 0) -> list[sqlparse.sql.Token]:
        tokens = cast(list[sqlparse.sql.Token], token_list.tokens)

        if len(tokens) <= start_idx:
            return []

        matches = [t for t in tokens[start_idx:] if t.match(ttype=ttype, values=value)]
        return matches

    def _first_token_of_ttype(self, token_list: sqlparse.sql.TokenList, ttype: sqlparse.tokens._TokenType, value: str | None = None, start_idx: int = 0) -> sqlparse.sql.Token | None:
        v = self._first_token_of_ttype_with_idx(token_list=token_list, ttype=ttype, value=value, start_idx=start_idx)
        return None if v is None else v[1]

    def _first_token_of_ttype_with_idx(self, token_list: sqlparse.sql.TokenList, ttype: sqlparse.tokens._TokenType, value: str|None = None, start_idx: int = 0) -> tuple[int, sqlparse.sql.Token] | None:
        if len(token_list.tokens) <= start_idx:
            return None

        match = token_list.token_next_by(m=(ttype, value), idx=start_idx - 1)
        if not match:
            return None

        i, t = match
        if i is None or t is None:
            return None

        return i, t
