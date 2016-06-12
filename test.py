import coverage
import contextlib

data = """
function a()
{
    decl(int) x := 10;
    if(x < 10)
    {
        return;
    }

    if(x < 10)
    {}
    else
    {}

    if(x < 10)
    {}
    elif(x < 10)
    {}

    if(x < 10)
    {}
    elif(x < 10)
    {}
    else
    {}

    while(x < 10)
    {
        x := x + 1;
    }
}

function add(int a, int b) -> int
{
    return a + b;
}
"""

@contextlib.contextmanager
def collect_coverage(use_coverage):
    if use_coverage:
        cov = coverage.Coverage()
        cov.start

    try:
        yield
    finally:
        if use_coverage:
            cov.stop()
            cov.save()
            cov.html_report()

if __name__ == "__main__":
    with collect_coverage(False):
        from src import parser
        from src import lexer
        from src import intermediate

        tokens = [x for x in lexer.lex(data)]
        out = parser.parse(data)
        out.check_semantics()
        intermediate = out.to_intermediate(intermediate.TransformState())
        for x in intermediate:
            print(str(x))
            for y in x.instructions:
                print("\t" + str(y))
            print("")
