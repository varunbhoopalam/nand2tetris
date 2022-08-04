# 2. create an output file named filename.xml and prepare it for writing
# 3. create and use compilation enginge to compile input from jacktokenizer into the output file
from sys import argv

from jackanalyzer.compilationengine import CompilationEngine
from jackanalyzer.jacktokenizer import JackTokenizer


def jack_analyzer():
    input_path = argv[1]
    output_path = input_path.replace(".jack", ".vm")
    input_file = open(input_path)
    jack_tokenizer = JackTokenizer(input_file)
    tokens = []  # Build from jack_tokenizer
    output_file = open(output_path)
    compilation_engine = CompilationEngine(input_file, output_file, tokens)
    compilation_engine.compile_class()


if __name__ == "__main__":
    jack_analyzer()
