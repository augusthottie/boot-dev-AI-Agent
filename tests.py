from functions.run_python_file import run_python_file


def main():
    # Test 1: Run calculator main.py without args
    print("run_python_file(\"calculator\", \"main.py\"):")
    print()
    result1 = run_python_file("calculator", "main.py")
    print(result1)
    print()
    print("-" * 80)
    print()

    # Test 2: Run calculator with arguments
    print("run_python_file(\"calculator\", \"main.py\", [\"3 + 5\"]):")
    print()
    result2 = run_python_file("calculator", "main.py", ["3 + 5"])
    print(result2)
    print()
    print("-" * 80)
    print()

    # Test 3: Run calculator tests
    print("run_python_file(\"calculator\", \"tests.py\"):")
    print()
    result3 = run_python_file("calculator", "tests.py")
    print(result3)
    print()
    print("-" * 80)
    print()

    # Test 4: Try to run file outside working directory
    print("run_python_file(\"calculator\", \"../main.py\"):")
    print()
    result4 = run_python_file("calculator", "../main.py")
    print(result4)
    print()
    print("-" * 80)
    print()

    # Test 5: Try to run non-existent file
    print("run_python_file(\"calculator\", \"nonexistent.py\"):")
    print()
    result5 = run_python_file("calculator", "nonexistent.py")
    print(result5)
    print()
    print("-" * 80)
    print()

    # Test 6: Try to run non-Python file
    print("run_python_file(\"calculator\", \"lorem.txt\"):")
    print()
    result6 = run_python_file("calculator", "lorem.txt")
    print(result6)


if __name__ == "__main__":
    main()


