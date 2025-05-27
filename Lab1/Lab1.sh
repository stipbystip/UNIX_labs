#!/bin/sh


WORK_DIR=$(pwd)


cleanup() {
    if [ -n "$tmp_dir" ] && [ -d "$tmp_dir" ]; then
        rm -rf "$tmp_dir"
    fi
}


trap 'cleanup; exit 130' INT TERM
trap 'cleanup; exit 1' HUP QUIT ABRT


exec 9>/tmp/script.lock
flock -n 9 || { echo "Error: Another instance is running." >&2; exit 1; }


[ $# -ne 1 ] && { echo "Usage: $0 <source_file>" >&2; exit 1; }

source_file="$1"
[ ! -f "$source_file" ] && { echo "Error: Source file not found" >&2; exit 2; }


output_name=$(grep -m1 -E '^[[:space:]]*//[[:space:]]*&Output:' "$source_file" | \
              sed 's/^[[:space:]]*\/\/[[:space:]]*&Output:[[:space:]]*//')
[ -z "$output_name" ] && { echo "Error: &Output: comment not found" >&2; exit 3; }


tmp_dir=$(mktemp -d)
[ $? -ne 0 ] && { echo "Error: Cannot create temp dir" >&2; exit 4; }


compile() {
    case "$1" in
        *.c|*.cpp|*.cc)
            compiler=$(command -v g++ || command -v clang++)
            [ -z "$compiler" ] && { echo "Error: No C++ compiler found" >&2; return 1; }
            $compiler -o "$2" "$3" >compile_output.log 2>compile_error.log || return 1
            ;;
        *.tex)
            command -v pdflatex >/dev/null || { echo "Error: pdflatex not found" >&2; return 1; }
            pdflatex -interaction=nonstopmode "$3" >compile_output.log 2>compile_error.log || return 1
            mv "$(basename "$3" .tex).pdf" "$2" || return 1
            ;;
        *) echo "Error: Unsupported file type" >&2; return 1 ;;
    esac
}


cp "$source_file" "$tmp_dir/" || { cleanup; exit 5; }
cd "$tmp_dir" || { cleanup; exit 6; }

if ! compile "$source_file" "$output_name" "$(basename "$source_file")"; then

    cat compile_error.log >&2
    cleanup
    exit 7
fi


[ ! -f "$output_name" ] && { echo "Error: Compiled file not found" >&2; cleanup; exit 8; }


cd "$WORK_DIR" || { cleanup; exit 9; }
[ -f "$output_name" ] && rm -f "$output_name"

if ! cp "$tmp_dir/$output_name" .; then
    echo "Error: Failed to copy output file" >&2
    cleanup
    exit 10
fi


[ ! -f "$output_name" ] && { echo "Error: Final file missing" >&2; cleanup; exit 11; }

chmod +x "$output_name" 2>/dev/null
echo "Success: $output_name created in $WORK_DIR"
cleanup
flock -u 9
exit 0
