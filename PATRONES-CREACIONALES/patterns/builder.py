
class Messag():

class MessageBuilder:
    def __init__(self) -> None:
        self._to = 'desconocido'
        self._subject = 'no subject'
        self._body = 'empty'
        self._from = 'anonymous'


    

    def subject (self, value: str) -> "MessageBuilder":
        self._subject = value
        return self
    
    def add_tag(self, value: str)-> "MessageBuilder":
        self._to = value
        return self
    