from app.lexer.detector import detect_from_extension, detect_language


def test_extension_detection():
    assert detect_from_extension("main.py") == "python"
    assert detect_from_extension("Solver.java") == "java"
    assert detect_from_extension("app.jsx") == "javascript"
    assert detect_from_extension("vector_math.cpp") == "cpp"
    assert detect_from_extension("README.md") is None


def test_heuristic_detection_python():
    src = "def add(a, b):\n    return a + b\n\nif __name__ == '__main__':\n    print(add(1, 2))"
    assert detect_language(src) == "python"


def test_heuristic_detection_cpp():
    src = '#include <iostream>\nusing namespace std;\nint main() {\n    std::cout << "hi";\n    return 0;\n}'
    assert detect_language(src) == "cpp"


def test_heuristic_detection_java():
    src = (
        "public class Main {\n"
        "    public static void main(String[] args) {\n"
        "        System.out.println(\"hi\");\n"
        "    }\n"
        "}"
    )
    assert detect_language(src) == "java"


def test_heuristic_detection_javascript():
    src = "const greet = (name) => {\n  console.log(`hi ${name}`);\n};\nlet x = 1;"
    assert detect_language(src) == "javascript"


def test_extension_overrides_heuristic():
    # content looks python-ish, but an explicit .java filename should win
    src = "def weird(): pass"
    assert detect_language(src, filename="Thing.java") == "java"


def test_empty_input_has_a_deterministic_default():
    assert detect_language("") == "python"
