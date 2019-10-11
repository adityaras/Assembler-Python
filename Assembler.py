import sys

sym_table = dict()
opcode_table = list()
literal_table = dict()
label_logs = list()
variable_logs = list()
opcode_conversion_table ={
        "CLA" : "0000",
        "LAC" : "0001",
        "SAC" : "0010",
        "ADD" : "0011",
        "SUB" : "0100",
        "BRZ" : "0101",
        "BRN" : "0110",
        "BRP" : "0111",
        "INP" : "1000",
        "DSP" : "1001",
        "MUL" : "1010",
        "DIV" : "1011",
        "STP" : "1100"
    }


def check_comment(instruction_line):
    if instruction_line[:2] == "//":
        return True
    elif instruction_line[:2] == "/*" and instruction_line[-2:] == "*/":
        return True
    else:
        return False


def check_label(instruction_line):
    if instruction_line[(instruction_line.find(" ") - 1)] == ":" and instruction_line[0] == "L":
        return True
    else:
        return False

def check_variables(instruction_line):
    ind_ws_1 = instruction_line.find(" ")
    ind_ws_2 = instruction_line.find(" ",ind_ws_1+1)
    if instruction_line[:ind_ws_1].isalpha() and instruction_line[ind_ws_1+1:ind_ws_2] == "DW" and instruction_line[ind_ws_2+1:].isdigit():
        if int(instruction_line[ind_ws_2+1:])>4095:
            print("E09: Memory Not Available - Allot a Memory Space b/w (0-4095)")
            sys.exit()
        else:
            return True
    else:
        return False


def check_opcode(instruction_line):
    if len(instruction_line) > 3:
        if instruction_line[3] == " " and instruction_line[:3].isalpha():
            return True
        else:
            return False
    elif instruction_line == "CLA" or instruction_line == "STP":
        return True
    else:
        return False


def check_literal(instruction_line):
    index_start = instruction_line.find("'")
    if index_start != -1:
        index_end = instruction_line.find("'", index_start + 1)
        if index_end != -1:
            str_checker = instruction_line[index_start+1:index_end]
            if str_checker.isdigit():
                return 0, index_start+1, index_end
            else:
                return -1, 0, 0
        else:
            return -1, 0, 0
    else:
        return 1, 0, 0


def check_label_used(instruction_line, loc_ctr):
    if instruction_line[:3] == "BRZ" or instruction_line[:3] == "BRN" or instruction_line[:3] == "BRP":
        if instruction_line[4:].isdigit():
            if int(instruction_line[4:]) > 4095:
                return 1
            else:
                return -1
        elif instruction_line[4] == "L":
            if not instruction_line[4:] in sym_table.keys():
                sym_table[instruction_line[4:]] = -1
            else:
                return -2
        else:
            return -3
    else:
        return 0

def variable_declared(instruction_line):
    if instruction_line[4:].isalpha():
        return True
    else:
        return False

def verify_opcode(instruction_line):
    if len(instruction_line)>3:
        opcode = instruction_line[:3]
    else:
        opcode=instruction_line
    if opcode.isalpha():
        if opcode == "CLA":
            return len(instruction_line)==3
        elif opcode == "LAC":
            return instruction_line[3] == " " and instruction_line[4:].isdigit()
        elif opcode == "SAC":
            return instruction_line[3] == " " and instruction_line[4:].isdigit()
        elif opcode == "ADD":
            return instruction_line[3] == " " and (variable_declared(instruction_line) or instruction_line[4:].isdigit() or check_literal(instruction_line) == (0,instruction_line.find("'")+1,instruction_line.find("'", instruction_line.find("'")+1)))
        elif opcode == "SUB":
            return instruction_line[3] == " " and (variable_declared(instruction_line) or instruction_line[4:].isdigit() or check_literal(instruction_line) == (0,instruction_line.find("'")+1,instruction_line.find("'", instruction_line.find("'")+1)))
        elif opcode == "MUL":
            return instruction_line[3] == " " and (variable_declared(instruction_line) or instruction_line[4:].isdigit() or check_literal(instruction_line) == (0,instruction_line.find("'")+1,instruction_line.find("'", instruction_line.find("'")+1)))
        elif opcode == "DIV":
            return instruction_line[3] == " " and (variable_declared(instruction_line) or instruction_line[4:].isdigit() or check_literal(instruction_line) == (0,instruction_line.find("'")+1,instruction_line.find("'", instruction_line.find("'")+1)))
        elif opcode == "BRP":
            return instruction_line[3] == " "
        elif opcode == "BRZ":
            return instruction_line[3] == " "
        elif opcode == "BRN":
            return instruction_line[3] == " "
        elif opcode == "INP":
            return  instruction_line[3] == " " and (instruction_line[4:].isdigit() or instruction_line[4:].isalpha())
        elif opcode == "DSP":
            return  instruction_line[3] == " " and (instruction_line[4:].isdigit() or instruction_line[4:].isalpha())
        elif opcode == "STP":
            return len(instruction_line) == 3
        else:
            return False
    else:
        return  False


def pass_one(loc_ctr,prog_ctr):

    loc_ctr = 0
    instruction_table = list()
    f = open("input.txt", "r")
    if f.mode == "r":
        for line in f:
            if line[-1] == "\n":
                line = line[:-1]
            instruction_table.append(line)
    for line in instruction_table:
        if not check_comment(line):

            if check_label(line):
                if line[:line.find(":")] not in label_logs:
                    label_end_index = line.find(":")
                    sym_table[line[:label_end_index]] = prog_ctr
                    label_logs.append(line[:label_end_index])
                    if check_opcode(line[label_end_index + 2:]):
                        opcode_table.append(line[label_end_index + 2:])
                        if variable_declared(line[label_end_index + 2:]):
                            variable_logs.append(line[label_end_index + 6:])
                            sym_table[line[label_end_index + 6:]] = prog_ctr
                    if line[label_end_index+2:].count(" ")>=2:
                        print("E08: Incorrect Syntax - Additional Whitespaces")
                        sys.exit()
                else:
                    print(" E01: Label declared more than once")
                    sys.exit()
            elif check_variables(line):
                ind_ws = line.find(" ")
                if line[:ind_ws] in variable_logs:
                    variable_logs.remove(line[:ind_ws])
                    sym_table[line[:ind_ws]] = line[ind_ws + 4:]
                else:
                    print(" E02: Variable Declared but not Used")
                    sym_table[line[:ind_ws]] = line[ind_ws+4:]
            elif check_opcode(line):
                opcode_table.append(line)
                if not verify_opcode(line):
                    print(" E03: Incorrect Syntax For Opcode")
                    sys.exit()
                label_checker = check_label_used(line, loc_ctr)
                if label_checker == -1:
                    print(" E04: Memory Not Available-Memory Limit Exceeded")
                    sys.exit()
                if label_checker == -3:
                    print(" E05: Syntax Error in defining Literal")
                    sys.exit()
            else:
                print(" E06: Instruction Not an Opcode/Label Declaration/Comment")
                sys.exit()
            checker, inds, inde = check_literal(line)

            if checker == 0:
                literal_table[line[inds:inde]] = str(bin(int(line[inds:inde])))[2:]
            elif checker == -1:
                print(" E07: Error in Literal Declaration")
                sys.exit()
            if variable_declared(line) and not line[:2] == "DW":
                variable_logs.append(line[4:])
                sym_table[line[4:]] = prog_ctr
            loc_ctr = loc_ctr + 20
            prog_ctr = prog_ctr + 1
    if len(variable_logs)>0:
        print(" E08: Variable(s) ",variable_logs," used but not declared")
        sys.exit()

def pass_two():
    f = open("Result.txt","w+")
    zero='0'
    for line in opcode_table:
        str_instruction=''
        str_instruction = str_instruction + opcode_conversion_table[line[:3]]+' '
        str_temp = ''
        if len(line)>3:
            if line[4:].isdigit():
                str_temp = str(bin(int(line[4:])))[2:]
                str_temp = zero * (20 - len(str_temp)) + str_temp + '\n'
            elif line[4:] in sym_table.keys():
                str_temp = str(bin(int(sym_table[line[4:]])))[2:]
                str_temp = zero * (20 - len(str_temp)) + str_temp + '\n'
            elif line[5:line.find("'",5)] in literal_table.keys():
                str_temp=literal_table[line[5:line.find("'",5)]]
                str_temp = zero * (20 - len(str_temp)) + str_temp + '\n'
        else:
            str_temp='\n'
        str_instruction=str_instruction+str_temp
        f.write(str_instruction)


if __name__ == '__main__':
    loc_ctr = 0
    prog_ctr = 0
    pass_one(loc_ctr,prog_ctr)
    pass_two()