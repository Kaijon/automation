class Funcs:
    def add(self, a, b):
        return a + b
        
fn = Funcs()

def test_add():
    assert fn.add(1, 2) == 3
