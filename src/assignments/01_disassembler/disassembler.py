import click

REG_ENCODING = {
    0b000: ['al', 'ax'],
    0b001: ['cl', 'cx'],
    0b010: ['dl', 'dx'],
    0b011: ['bl', 'bx'],
    0b100: ['ah', 'sp'],
    0b101: ['ch', 'bp'],
    0b110: ['dh', 'si'],
    0b111: ['bh', 'di'],
}


@click.command()
@click.argument('filename', type=click.Path(exists=True), default='8086_mov')
@click.option('--output', '-o', type=click.Path(), default='8086_mov_out.asm')
def disassemble(filename, output):
    """Disassemble a file."""
    with open(filename, 'rb') as f:
        data = f.read()

    output_str = "bits 16\n\n"
    for i in range(0, len(data), 2):
        assembly = disassemble_instruction(data[i:i+2])
        output_str += f'{assembly}\n'

    with open(output, 'w') as f:
        f.write(output_str)


def disassemble_instruction(sixteen_bits):
    assembly = ''

    opcode = (sixteen_bits[0] & 0b1111_1100) >> 2
    d = (sixteen_bits[0] & 0b0000_0010) >> 1
    w = (sixteen_bits[0] & 0b0000_0001) >> 0

    mod = (sixteen_bits[1] & 0b1100_0000) >> 6
    reg = (sixteen_bits[1] & 0b0011_1000) >> 3
    rm = (sixteen_bits[1] & 0b0000_0111) >> 0

    if opcode == 0b100010:
        assembly += 'mov'

        first_reg = reg if d else rm
        second_reg = rm if d else reg
        first = REG_ENCODING[first_reg][w]
        second = REG_ENCODING[second_reg][w]

        return f'{assembly} {first}, {second}'
    else:
        raise Exception('Unknown opcode')

if __name__ == '__main__':
    disassemble()