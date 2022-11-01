import math
import os
import sys
from base64 import b64decode, b64encode

from splunklib.searchcommands import (
    Configuration,
    Option,
    StreamingCommand,
    dispatch,
    validators,
)


@Configuration()
class Base64Command(StreamingCommand):
    """
    Encode a string to Base64
    Decode a Base64 content
     | base64 [action=(encode|decode)] field=<field> [mode=(replace|append)] [special_chars=(keep|remove|hash)]
    """

    field = Option(name="field", require=True)
    action = Option(name="action", require=False, default="encode")
    mode = Option(name="mode", require=False, default="replace")
    special_chars = Option(name="special_chars", require=False, default="keep")
    convert_newlines = Option(
        name="convert_newlines",
        require=False,
        default=True,
        validate=validators.Boolean(),
    )
    fix_padding = Option(
        name="fix_padding", require=False, default=True, validate=validators.Boolean()
    )
    suppress_error = Option(
        name="suppress_error",
        require=False,
        default=False,
        validate=validators.Boolean(),
    )

    def stream(self, events):
        module = sys.modules["base64"]

        if self.action == "decode":
            func = b64decode
        else:
            func = b64encode

        if self.mode == "append":
            dest_field = self.field + "_base64"
        else:
            dest_field = self.field

        for event in events:

            if not self.field in event:
                continue

            try:
                if isinstance(event[self.field], str):
                    original = event[self.field].encode("utf-8")
                else:
                    original = event[self.field]

                event[dest_field] = func(original).decode("utf-8")

            except Exception as e:
                if not self.suppress_error:
                    raise e

            yield event


dispatch(Base64Command, sys.argv, sys.stdin, sys.stdout, __name__)
