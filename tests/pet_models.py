from specd.sdk import BaseModel


class Pet(BaseModel):
    def speak(self):
        return "woof" if self.name == "doggie" else "hello"

    def clone(self, **kw):
        return self.instantiate(self.definitions.Pet, self._as_dict(), **kw)
