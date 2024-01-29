use std::collections::HashMap;
use std::fs::File;
use std::io;
use std::io::prelude::*;
use std::str::FromStr;

// fn get_opcode(buff: &[u8]) -> &str {
//     match buff[0] & 0b1111_1000 {
//         0b1000_1000 => "MOV"
//         _ => "",
//     };
// }

// fn get_register(reg: &[u8], w: u8) -> &str {

//     match reg {
//         0b000 => "AL",
//         0b001 => "CL",
//         0b010 => "DL",
//         0b011 => "BL",
//         0b100 => "AH",
//         0b101 => "CH",
//         0b110 => "DH",
//         0b111 => "BH",
//         _ => "",
//     }
// }

fn disassemble_instruction(first_byte: u8, second_byte: u8) -> String {
    let REG_ENCODING = HashMap::from([
        (0b000, ["al", "ax"]),
        (0b001, ["cl", "cx"]),
        (0b010, ["dl", "dx"]),
        (0b011, ["bl", "bx"]),
        (0b100, ["ah", "sp"]),
        (0b101, ["ch", "bp"]),
        (0b110, ["dh", "si"]),
        (0b111, ["bh", "di"]),
    ]);

    let assembly = String::new();

    // extract the x86 opcode from the two bytes
    let opcode = (first_byte & 0b1111_1000) >> 2;
    let d = (first_byte & 0b0000_0010) >> 1;
    let w = (first_byte & 0b0000_0001) >> 0;

    // extract the register from the two bytes
    let mode = (second_byte & 0b1100_0000) >> 6;
    let reg = (second_byte & 0b0011_1000) >> 3;
    let rm = (second_byte & 0b0000_0111) >> 0;

    match opcode {
        0b100010 => {
            // MOV
            assembly.push_str("mov ");

            // create 

            // push reg / rm first based on if d is 0 or 1 
            assembly.push_str(if d == 0 {
                REG_ENCODING[&rm][&w]
            } else {
                REG_ENCODING[&reg][&w]
            });
            assembly.push_str(", ");
            assembly.push_str(if d == 0 {
                REG_ENCODING[&reg][&w]
            } else {
                REG_ENCODING[&rm][&w]
            });
        }
        _ => {}
    }
}

fn main() -> io::Result<()> {
    // read the file
    let mut f = File::open("8086_mov")?;
    let mut buff = Vec::new();
    f.read_to_end(&mut buff)?;

    // create the output string
    let output_str = String::from_str("bits 16\n\n");
    for i in (0..buff.len()).step_by(2) {
        let assembly = disassemble_instruction(buff[i], buff[i + 1]);
        output_str.push_str(&assembly);
        // println!(
        //     "opcode={:06b} d={:01b} w={:01b} | mod={:02b} reg={:03b} rm={:03b}",
        //     opcode, d, w, mode, reg, rm
        // );
    }

    let mut output_file = File::create("8086_mov_out.asm")?;
    output_file.write_all(output_str.as_bytes())?;

    Ok(())
}
