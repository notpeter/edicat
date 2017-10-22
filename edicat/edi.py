# TODO: Better tests for '\r\n' and'

class EDI():
    def __init__(self, edi):
        if isinstance(edi, str):
            self.text = edi.strip()
        # file, io.TextIOWrapper, etc
        elif hasattr(edi, 'read'):
            self.text = edi.read()
        else:
            raise ValueError(f"EDI passed unknown type: {type(edi)}")

        if self.text.startswith('UN'):
            if self.text.startswith('UNA'):
                self.sep_seg = self.text[8:self.text.find('UNB')]
            else:
                self.sep_seg = "'"
            self.lol = [li for li in self.text.split(self.sep_seg) if li.strip()]

    def __str__(self):
        lb = f"{self.sep_seg.strip()}\n"
        return lb.join(line for line in self.lol)

    def __repr__(self):
        return f"EDI({repr(self.text)}"
