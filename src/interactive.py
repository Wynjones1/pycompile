import parser
import sys

if __name__ == "__main__":
    input = ""
    last = ""
    while True:
        sys.stdout.write(">")
        sys.stdout.flush()
        line = sys.stdin.readline()
        if line == "\n" and last == "\n":
            break
        last = line
        input += line

    print(input)
