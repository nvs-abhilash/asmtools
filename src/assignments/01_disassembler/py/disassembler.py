import os
from pathlib import Path
import click

REGISTERS = {
    0b0000: "al",
    0b0001: "ax",
    0b0010: "cl",
    0b0011: "cx",
    0b0100: "dl",
    0b0101: "dx",
    0b0110: "bl",
    0b0111: "bx",
    0b1000: "ah",
    0b1001: "sp",
    0b1010: "ch",
    0b1011: "bp",
    0b1100: "dh",
    0b1101: "si",
    0b1110: "bh",
    0b1111: "di",
}

EFFECTIVE_ADDRESS = {
    0b000: "bx + si",
    0b001: "bx + di",
    0b010: "bp + si",
    0b011: "bp + di",
    0b100: "si",
    0b101: "di",
    0b110: "bp", # direct address when mod = 0b00
    0b111: "bx",
}


def disassembler(bytes, start, end):
    if start >= end:
        return ""

    output_string = "bits 16\n\n" if start == 0 else ""
    instruction = ""
    skip = 2

    # find operation
    if bytes[start] & 0b11111100 == 0b10001000:
        # mov
        d = (bytes[start] & 0b00000010) >> 1
        w = bytes[start] & 0b00000001
        instruction += "mov "

        mod = (bytes[start + 1] & 0b11000000) >> 6
        if mod == 0b11:
            # register to register
            reg = REGISTERS[(((bytes[start + 1] & 0b00111000) >> 3) << 1) | w]
            rm = REGISTERS[(((bytes[start + 1] & 0b00000111) >> 0) << 1) | w]
            dst = reg if d == 1 else rm
            src = rm if d == 1 else reg
            instruction += f"{dst}, {src}"
        elif mod == 0b00:
            # memory mode, no displacement*
            reg = REGISTERS[(((bytes[start + 1] & 0b00111000) >> 3) << 1) | w]
            rm = f"[{EFFECTIVE_ADDRESS[bytes[start + 1] & 0b00000111]}]"

            dst = reg if d == 1 else rm
            src = rm if d == 1 else reg
            instruction += f"{dst}, {src}"
        elif mod == 0b01:
            # memory mode, byte displacement
            reg = REGISTERS[(((bytes[start + 1] & 0b00111000) >> 3) << 1) | w]
            d8 = bytes[start + 2]
            skip += 1
            rm = f"[{EFFECTIVE_ADDRESS[bytes[start + 1] & 0b00000111]} + {d8}]"
            dst = reg if d == 1 else rm
            src = rm if d == 1 else reg
            instruction += f"{dst}, {src}"
        elif mod == 0b10:
            # memory mode, word displacement
            reg = REGISTERS[(((bytes[start + 1] & 0b00111000) >> 3) << 1) | w]
            d16 = (bytes[start + 3] << 8) + bytes[start + 2]
            skip += 2
            rm = f"[{EFFECTIVE_ADDRESS[bytes[start + 1] & 0b00000111]} + {d16}]"
            dst = reg if d == 1 else rm
            src = rm if d == 1 else reg
            instruction += f"{dst}, {src}"
        else:
            return ""
            raise NotImplementedError("Operation not implemented")

    elif bytes[start] & 0b11111110 == 0b11000110:
        # immediate to registr/memory
        return ""
        raise NotImplementedError("Operation not implemented")
    elif bytes[start] & 0b11110000 == 0b10110000:
        # immediate to register
        w = (bytes[start] & 0b00001000) >> 3
        reg = REGISTERS[(((bytes[start] & 0b00000111) >> 0) << 1) | w]

        data = bytes[start + 1]
        if w == 1:
            data += bytes[start + 2] << 8
            skip += 1
        instruction += f"mov {reg}, {data}"
    else:
        return ""
        raise NotImplementedError("Operation not implemented")

    output_string += instruction
    output_string += "\n"
    return output_string + disassembler(bytes, start + skip, end)


@click.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default="a.asm")
@click.option("--test", "-t", is_flag=True, default=False, help="Run test")
def main(filename, output, test):
        # convert asm file to binary file
    os.system(f"nasm {filename} -o {filename}.bin")
    try:
        with open(f"{filename}.bin", "rb") as f:
            byte_stream = f.read()
        output_string = disassembler(byte_stream, 0, len(byte_stream))

        print(output_string)
        with open(output, "w") as f:
            f.write(output_string)

        if test:
            run_test(output, f"{filename}.bin")

    finally:
        # cleanup
        os.system(f"rm {filename}.bin")

def run_test(output, testfile):
    # assemble using nasm and compare the binary files
    os.system(f"nasm {output} -o {output}.bin")
    with open(f"{output}.bin", "rb") as f:
        output_bytes = f.read()
    with open(testfile, "rb") as f:
        test_bytes = f.read()
    if output_bytes == test_bytes:
        print("Test passed")
    else:
        print("Test failed")

    # cleanup
    os.system(f"rm {output}.bin")


if __name__ == "__main__":
    main()
