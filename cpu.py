"""CPU functionality."""

import sys

'''
* `LDI`: load "immediate", store a value in a register, or "set this register to
  this value".
* `PRN`: a pseudo-instruction that prints the numeric value stored in a
  register.
* `HLT`: halt the CPU and exit the emulator.
'''
# day 1
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111

# day 2
MUL = 0b10100010
ADD = 0b10100000
SUB = 0b10100001
DIV = 0b10100011

# day 3
PUSH = 0b01000101
POP = 0b01000110

# day 4
CALL = 0b01010000
RET = 0b00010001

#SPRINT MVP NEEDS
CMP = 0b10100111 # Compare the values in two registers.
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

# stack pointer lives in register spot 7
SP = 7

class CPU:
  
    def __init__(self):
        """Construct a new CPU."""

        #256 bytes of memory
        self.ram = [0] * 256

        # a word is 8 bit
        self.reg = [0] * 8

        # program counter
        self.program_counter = 0

        # A branchtable, or jump table, will help alleviate if-elif-else chain and DRY up code
        ### self.branchtable is a dictionary 
        self.branchtable = {}
        # [PRN] would be a pointer to the corresponding function in the branchtable
        ### [PRN] would be the key in the key:value pair
        ### self.handle_prn would be the value
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        self.branchtable[CALL] = self.handle_call
        self.branchtable[RET] = self.handle_ret
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[CMP] = self.handle_cmp
        self.branchtable[JEQ] = self.handle_jeq
        self.branchtable[JMP] = self.handle_jmp
        self.branchtable[JNE] = self.handle_jne

        #The flag register `FL` holds the current flags status
        # 0b00000LGE
        self.fl = 0b00000000 # set to 0
        self.equal_to = 0b00000001
        self.less_than = 0b000000100
        self.greater_than = 0b00000010

    def ram_read(self,mem_address):
        return self.ram[mem_address]

    def ram_write(self, mem_data, mem_address):
        self.ram[mem_address] = mem_data


    def handle_ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.program_counter += 3

    def handle_prn(self, operand_a, operand_b):
        print(f"Printing: {self.reg[operand_a]}")
        self.program_counter += 2

    def handle_mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        self.program_counter += 3

    def handle_pop(self, operand_a, operand_b):
        popped_val = self.ram[self.reg[SP]]
        self.reg[operand_a] = popped_val
        self.reg[SP] += 1
        self.program_counter += 2

    def handle_push(self, operand_a, operand_b):
        pushed_val = self.reg[operand_a]
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = pushed_val
        self.program_counter += 2

    def handle_call(self, operand_a, operand_b):
        return_address = self.program_counter + 2
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = return_address

        reg_num = operand_a
        self.program_counter = self.reg[reg_num]

    def handle_ret(self, operand_a, operand_b):
        # pop the value from top of the stack and store it in the pc
        self.program_counter = self.ram[self.reg[SP]]
        self.reg[SP] += 1

    #sprint
    def handle_cmp(self, operand_a, operand_b):
        self.alu('CMP', operand_a, operand_b)
        self.program_counter += 3 # three steps for next instruction

    #Jump to the address stored in the given register.
    #Set the `PC` to the address stored in the given register.
    def handle_jmp(self, operand_a, operand_b):
        self.program_counter = self.reg[operand_a]


    #If `equal` flag is set (true), jump to the address stored in the given register.
    def handle_jeq(self, *args):
        # *args allow you to pass multiple arguments or keyword arguments to a function
        if self.fl== 0b00000001:
            self.handle_jmp(*args)
        else:
            self.program_counter += 2 # two steps for next instruction

    #If `E` flag is clear (false, 0), jump to the address stored in the given register.
    def handle_jne(self, *args):
        # *args allow you to pass multiple arguments or keyword arguments to a function
        if self.fl == 0b00000100:
            self.handle_jmp(*args)
        else:
            self.program_counter += 2 # two steps to next instruction
    
    def load(self, filename):
        """Load a program into memory."""

        address = 0

        program = []

        with open(filename) as f:
            #read all the lines
                for line in f:
                    # parse out comments
                    # print(line)
                    split = line.split('#')
                    # ignore blank lines

                    #cast numbers from strings to ints
                    value = split[0].strip()
                    if value == "":
                        continue
                    final_val = int(value, 2)
                    self.ram[address] = final_val
                    address += 1 # iterates!

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == 'ADD':
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 'SUB':
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'DIV':
            if self.reg[reg_b] == 0:
                print("Error: cannot divide by 0 silly")
                sys.exit()
            self.reg[reg_a] /= self.reg[reg_b]

        #sprint

        #`FL` bits: `00000LGE`

        elif op == 'CMP':
            if self.reg[reg_a] == self.reg[reg_b]:
                #0000000E
                self.fl = self.equal_to
            elif self.reg[reg_a] < self.reg[reg_b]:
                #00000L00
                self.fl = self.less_than
            elif self.reg[reg_a] > self.reg[reg_b]:
                #000000G0
                self.fl = self.greater_than
            else:
                # set to 0
                self.fl = 0b00000000
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.program_counter,
            #self.fl,
            #self.ie,
            self.ram_read(self.program_counter),
            self.ram_read(self.program_counter + 1),
            self.ram_read(self.program_counter + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # Perform REPL style execution
        running = True
        # Before the loop starts, initialize stack pointer in R7
        self.reg[SP] = 0xF4
        while running:
            # Start the CPU. start storing instructions in instruction_register
            instruction_register = self.ram_read(self.program_counter)
            operand_a = self.ram_read(self.program_counter+1)
            operand_b = self.ram_read(self.program_counter+2)

            # For some reason, 
            # loop would try to go on after HLT instruction 
            # it would go to instruction_register = 1 and throw exception message
            if instruction_register == HLT:
                running = False
                break
            # try to engage the reads from program and excecute branchtable instructions
            try:
                self.branchtable[instruction_register](operand_a, operand_b)
            except:
                print(f"Bad instruction register: {instruction_register}")
                sys.exit(1)