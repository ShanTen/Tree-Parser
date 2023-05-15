class ParentErrorClass:
    def __init__(self, errorType, details):
        self.errorType = errorType
        self.details = details

    def stringify(self):
        string = f'{self.errorType}:\n{self.details}'
        return string