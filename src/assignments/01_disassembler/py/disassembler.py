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

def disassembler(bytes, start, end):
    if start >= end:
        return ""

    output_string = "bits 16\n"
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
            instruction += f"{REGISTERS[(bytes[start + 1] & 0b00111000) >> 2 | w]}, "
            instruction += f"{REGISTERS[(bytes[start + 1] & 0b00000111)] >> 2 | w}"
        else:
            raise NotImplementedError("Operation not implemented")

    elif bytes[start] & 0b11111110 == 0b11000110:
        # immediate to registr/memory
        pass
    elif bytes[start] & 0b11110000 == 0b10110000:
        # immediate to register
        pass
    else:
        raise NotImplementedError("Operation not implemented")

    output_string += instruction
    output_string += "\n"
    return output_string + disassembler(bytes, start + skip, end)

def main():
    with open("../inp/8086_mov2.out", "rb") as f:
        byte_stream = f.read()
    disassembler(byte_stream)


if __name__ == "__main__":
    main()
