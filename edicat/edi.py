# TODO: Better tests for '\r\n' and such.


class EDI():
    def __init__(self, edi):
        if isinstance(edi, str):
            self.text = edi
        # file, io.TextIOWrapper, etc
        elif hasattr(edi, 'read'):
            self.text = edi.read()
        else:
            raise ValueError(f"EDI passed unknown type: {type(edi)}")

        if self.text.startswith('UNA'):
            self.sep_seg = self.text[8]
        elif self.text.startswith('UNB'):
            self.sep_seg = "'"
        elif self.text.startswith('ISA'):
            raise NotImplementedError("EDI X12 not supported.")
        else:
            raise NotImplementedError("Unknown EDI format.")

        self.lol = []
        for li in self.text.split(self.sep_seg):
            if li.strip('\r\n'):
                self.lol.append(li.strip('\r\n') + self.sep_seg)

    def __str__(self):
        return "\n".join(line for line in self.lol).rstrip()

    def __repr__(self):
        return f"EDI({repr(self.text)}"
