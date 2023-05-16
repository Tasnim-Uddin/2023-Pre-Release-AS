# Skeleton Program for the AQA AS Summer 2023 examination
# this code should be used in conjunction with the Preliminary Material
# written by the AQA Programmer Team
# developed in a Python 3 environment

# Version number: 0.0.0


EMPTY_STRING = ""
HI_MEM = 20  # memory has 20 places -- memory array is used for storing program as well as stack
MAX_INT = 127  # 8 bits available for operand (two's complement integer)
PC = 0  # pc is represented by the zeroth position in Registers[]
ACC = 1  # acc is represented by the first position in Registers[]
STATUS = 2  # status is represented by the second position in Registers[]
TOS = 3  # top of stack is represented by the third position in Registers[]
ERR = 4  # error is represented by the fourth position in Registers[]


class AssemblerInstruction:
    # Description: This class provides a template for objects of these will be stored in the Memory array
    # with each object representing opcode, operand and value (can be data or memory location for direct addressing)

    def __init__(self):
        self.OpCode = EMPTY_STRING
        self.OperandString = EMPTY_STRING
        self.OperandValue = 0


def DisplayMenu():
    # Parameters: None
    # Return: None
    # Description: Displays the options to the user
    print()
    print("Main Menu")
    print("=========")
    print("L - Load a program file")
    print("D - Display source code")
    print("E - Edit source code")
    print("A - Assemble program")
    print("R - Run the program")
    print("X - Exit simulator")
    print()


def GetMenuOption():
    # Parameters: None
    # Return: String
    # Description: gets the choice of the user and returns it
    Choice = EMPTY_STRING
    while len(Choice) != 1:
        Choice = input("Enter your choice: ")
    return Choice[0]


def ResetSourceCode(SourceCode):
    # Parameters: List (of strings)
    # Return: List (of strings)
    # Description: fills SourceCode[] with empty strings

    for LineNumber in range(HI_MEM):
        SourceCode[LineNumber] = EMPTY_STRING
    return SourceCode


def ResetMemory(Memory):
    # Parameters: List (of objects)
    # Return: List (of objects)
    # Description: Makes each object in Memory[] have default values
    for LineNumber in range(HI_MEM):
        Memory[LineNumber].OpCode = EMPTY_STRING
        Memory[LineNumber].OperandString = EMPTY_STRING
        Memory[LineNumber].OperandValue = 0
    return Memory


def DisplaySourceCode(SourceCode):
    # Parameters: List (of strings)
    # Return: None
    # Description: Prints each line of SourceCode[]
    print()
    NumberOfLines = int(SourceCode[0])
    for LineNumber in range(0, NumberOfLines + 1):
        print("{:>2d} {:<40s}".format(LineNumber, SourceCode[LineNumber]))
    print()


def LoadFile(SourceCode):
    """
    Parameters: List (of strings)
    Return: List (of strings)
    Description: First checks if the file exists, then reads each line into Instruction, and stores it into SourceCode
    If the file does not exist or if file is corrupt, then it returns an error
    SourceCode[0] stores the number of lines that can be read without errors as a string
    """
    FileExists = False
    SourceCode = ResetSourceCode(SourceCode)
    LineNumber = 0
    FileName = input("Enter filename to load: ")
    try:
        FileIn = open(FileName + ".txt", 'r')
        FileExists = True
        Instruction = FileIn.readline()
        while Instruction != EMPTY_STRING:
            LineNumber += 1
            SourceCode[LineNumber] = Instruction[:-1]  # remove the "\n"
            Instruction = FileIn.readline()
        FileIn.close()
        SourceCode[0] = str(LineNumber)  # first index represents the number of lines read from the file
    except:
        if not FileExists:
            print("Error Code 1")  # text file does not exist
        else:
            print("Error Code 2")  # file is corrupt / file does not have right encoding
            SourceCode[0] = str(LineNumber - 1)  # first index represents the number of lines read without error
    if LineNumber > 0:
        DisplaySourceCode(SourceCode)  # display assembly code if at least one line is read
    return SourceCode


def EditSourceCode(SourceCode):
    # Parameters: List (of strings)
    # Return: List (of strings)
    # Description: Lets the user changes lines in the SourceCode []
    LineNumber = int(input("Enter line number of code to edit: "))
    print(SourceCode[LineNumber])  # show the line to be edited
    Choice = EMPTY_STRING
    while Choice != "C":
        Choice = EMPTY_STRING
        while Choice != "E" and Choice != "C":
            print("E - Edit this line")
            print("C - Cancel edit")
            Choice = input("Enter your choice: ")
        if Choice == "E":
            SourceCode[LineNumber] = input("Enter the new line: ")  # change the line in array if user
            # has not cancelled the edit
        DisplaySourceCode(SourceCode)
    return SourceCode


def UpdateSymbolTable(SymbolTable, ThisLabel, LineNumber):
    # Parameters: dictionary, string, int
    # Return: dictionary
    # Description: add unique labels to symbol table
    if ThisLabel in SymbolTable:  # if label already exists in the symbol table
        print("Error Code 3")
    else:
        SymbolTable[ThisLabel] = LineNumber
    return SymbolTable


def ExtractLabel(Instruction, LineNumber, Memory, SymbolTable):
    # Parameters: string, int, list (of objects), dictionary
    # Return: dictionary, list (of objects)
    # Description: separates first 5 characters (label) in the instruction to add to the dictionary
    if len(Instruction) > 0:
        ThisLabel = Instruction[0:5]  # first 5 characters
        ThisLabel = ThisLabel.strip()
        if ThisLabel != EMPTY_STRING:
            if Instruction[5] != ':':  # checks if sixth character is not a colon
                print("Error Code 4")
                Memory[0].OpCode = "ERR"  # first index of Memory[] is updated if colon is not found
            else:
                SymbolTable = UpdateSymbolTable(SymbolTable, ThisLabel, LineNumber)  # SymbolTable is updated
                # to keep track of labels
    return SymbolTable, Memory


def ExtractOpCode(Instruction, LineNumber, Memory):
    """
        Parameters: string, integer, list (of objects)
        Return: list (of objects)
        Description: separates the opcode in the instruction, checks if it is a valid opcode otherwise
        first index of memory is updated with opcode ERR
    """

    if len(Instruction) > 9:  # all valid instructions with opcodes are a minimum 10 characters (0-9) long
        OpCodeValues = ["LDA", "STA", "LDA#", "HLT", "ADD", "JMP", "SUB", "CMP#", "BEQ", "SKP", "JSR", "RTN", "   "]
        Operation = Instruction[7:10]  # extract opcode from characters at position 7-9
        if len(Instruction) > 10:  # check if there are characters after opcode
            AddressMode = Instruction[10:11]  # get the 10th character
            if AddressMode == '#':  # check if the 10th character is a hash
                Operation += AddressMode  # add the # to the opcode
        if Operation in OpCodeValues:  # check if the extracted opcode is one of the 13 specified values
            Memory[LineNumber].OpCode = Operation  # Memory is updated with opcode
        else:
            if Operation != EMPTY_STRING:  # checks if opcode is in the list OpCodeValues
                print("Error Code 5")
                Memory[0].OpCode = "ERR"  # Memory is updated if opcode is not found
    return Memory


def ExtractOperand(Instruction, LineNumber, Memory):
    """
        Parameters: string, integer, list (of objects)
        Return: list (of objects)
        Description: separates the operand in the instruction, operand does not include the comment
    """
    if len(Instruction) >= 13:  # all valid instructions with operands are minimum 13 characters long
        Operand = Instruction[12:]
        # In an instruction, label takes 5 characters (0-4), colon is 5th, space is 6th,
        # space or opcode (mnemonics) for characters 7-9
        # space or # (address mode) for 10th, space for 11th
        # Hence operand starts at 12th position
        ThisPosition = -1
        for Position in range(len(Operand)):
            if Operand[Position] == '*':  # checks if there is a comment in the operand
                ThisPosition = Position
        if ThisPosition >= 0:
            Operand = Operand[:ThisPosition]  # if there is a comment, the operand stops before the comment
        Operand = Operand.strip()  # any spaces in beginning and end of operand are stripped
        Memory[LineNumber].OperandString = Operand  # Memory is updated with extracted operand
    return Memory


def PassOne(SourceCode, Memory, SymbolTable):
    # Parameters: list (of strings), list (of objects), dictionary
    # Return: list (of objects), dictionary
    # Description: used for extracting opcode, operand into memory and updating the dictionary with label
    NumberOfLines = int(SourceCode[0])  # specifies number of lines to trace
    for LineNumber in range(1, NumberOfLines + 1):
        Instruction = SourceCode[LineNumber]
        SymbolTable, Memory = ExtractLabel(Instruction, LineNumber, Memory,
                                           SymbolTable)  # unique labels are extracted and put in symbol table,
        # memory is updated if error is found
        Memory = ExtractOpCode(Instruction, LineNumber, Memory)  # Memory is updated with extracted opcode or error code
        Memory = ExtractOperand(Instruction, LineNumber, Memory)  # Memory is updated with extracted operand

    return Memory, SymbolTable


def PassTwo(Memory, SymbolTable, NumberOfLines):
    """
        Parameters: list (of objects), dictionary, integer
        Return: list (of objects)
        Description: used for updating memory with operand values based on
        whether the operand is a label (direct addressing) or an integer (immediate addressing)
    e.g. in memory, the instruction SUB NUM1 looks like {'OpCode': 'SUB', 'OperandString': 'NUM1', 'OperandValue': 10}
    """
    for LineNumber in range(1, NumberOfLines + 1):
        Operand = Memory[LineNumber].OperandString  # get the operand from memory
        if Operand != EMPTY_STRING:
            if Operand in SymbolTable:  # check if any operand is a label
                OperandValue = SymbolTable[Operand]  # get line number associated with the label
                Memory[LineNumber].OperandValue = OperandValue  # update memory with line number for
                # operands that are labels
            else:
                try:
                    OperandValue = int(Operand)
                    Memory[LineNumber].OperandValue = OperandValue  # update memory for operands that are integers
                except:
                    print("Error Code 6")
                    Memory[0].OpCode = "ERR"
                    print(SymbolTable)
    return Memory


def DisplayMemoryLocation(Memory, Location):
    print("*  {:<5s}{:<5d} |".format(Memory[Location].OpCode, Memory[Location].OperandValue), end='')


def DisplaySourceCodeLine(SourceCode, Location):
    print(" {:>3d}  |  {:<40s}".format(Location, SourceCode[Location]))


def DisplayCode(SourceCode, Memory):
    print("*  Memory     Location  Label  Op   Operand Comment")
    print("*  Contents                    Code")
    NumberOfLines = int(SourceCode[0])
    DisplayMemoryLocation(Memory, 0)
    print("   0  |")
    for Location in range(1, NumberOfLines + 1):
        DisplayMemoryLocation(Memory, Location)
        DisplaySourceCodeLine(SourceCode, Location)


def Assemble(SourceCode, Memory):
    """
        Parameters: string array, objects array
        Return: objects array
        Description: performs pass one and pass two
            PassOne --> to separate the label, instruction and operand in each instruction,
            PassTwo --> update operand value in memory
    """
    Memory = ResetMemory(Memory)
    NumberOfLines = int(SourceCode[0])
    SymbolTable = {}
    Memory, SymbolTable = PassOne(SourceCode, Memory, SymbolTable)  # extract opcode, operand and label
    if Memory[0].OpCode != "ERR":  # checks if there is error in pass one
        Memory[0].OpCode = "JMP"  # if no error, makes the first opcode as jump instruction
        if "START" in SymbolTable:
            Memory[0].OperandValue = SymbolTable["START"]  # memory operand value is updated to the
            # line number specified by Start
        else:
            Memory[0].OperandValue = 1  # if there is no start, jumps to line 1 by default
        Memory = PassTwo(Memory, SymbolTable, NumberOfLines)  # update operand value
    return Memory


def ConvertToBinary(DecimalNumber):
    # Parameters: integer
    # Return: string
    # Description: Gives binary representation of positive decimals, appends 0s at the LHS if minimum length is not 3
    BinaryString = EMPTY_STRING
    while DecimalNumber > 0:
        Remainder = DecimalNumber % 2
        Bit = str(Remainder)
        BinaryString = Bit + BinaryString
        DecimalNumber = DecimalNumber // 2
    while len(BinaryString) < 3:  # append zeros to make binary string of length 3
        BinaryString = '0' + BinaryString
    return BinaryString


def ConvertToDecimal(BinaryString):
    # Parameters: string
    # Return: integer
    # Description: Converts binary string to decimal value for positive values
    DecimalNumber = 0
    for Bit in BinaryString:
        BitValue = int(Bit)
        DecimalNumber = DecimalNumber * 2 + BitValue
    return DecimalNumber


def DisplayFrameDelimiter(FrameNumber):
    if FrameNumber == -1:
        print("***************************************************************")
    else:
        print("****** Frame", FrameNumber, "************************************************")


def DisplayCurrentState(SourceCode, Memory, Registers):
    print("*")
    DisplayCode(SourceCode, Memory)
    print("*")
    print("*  PC: ", Registers[PC], " ACC: ", Registers[ACC], " TOS: ", Registers[TOS])
    print("*  Status Register: ZNV")
    print("*                  ", ConvertToBinary(Registers[STATUS]))  # display status flags as binary
    DisplayFrameDelimiter(-1)


def SetFlags(Value, Registers):
    if Value == 0:
        Registers[STATUS] = ConvertToDecimal("100")  # 3rd position of Registers is set to 4, to show that
        # Zero flag is set
    elif Value < 0:
        Registers[STATUS] = ConvertToDecimal("010")  # 3rd position of Registers is set to 2, to show that
        # Negative flag is set
    elif Value > MAX_INT or Value < -(MAX_INT + 1):  # checks if value inbetween 127 and -128
        Registers[STATUS] = ConvertToDecimal("001")  # 3rd position of Registers is set to 1, to show that
        # Value flag is set
    else:
        Registers[STATUS] = ConvertToDecimal("000")  # 3rd position of Registers is set to 0, to show that
        # all flags are reset
    return Registers


def ReportRunTimeError(ErrorMessage, Registers):
    print("Run time error:", ErrorMessage)
    Registers[ERR] = 1
    return Registers


def ExecuteLDA(Memory, Registers, Address):
    Registers[ACC] = Memory[Address].OperandValue  # get the value in memory location and load into accumulator
    Registers = SetFlags(Registers[ACC], Registers)  # update flags
    return Registers


def ExecuteSTA(Memory, Registers, Address):
    Memory[Address].OperandValue = Registers[ACC]  # Stores the value in the accumulator to the memory location
    return Memory


def ExecuteLDAimm(Registers, Operand):
    Registers[ACC] = Operand  # Loads the accumulator with the operand value
    Registers = SetFlags(Registers[ACC], Registers)
    return Registers


def ExecuteADD(Memory, Registers, Address):
    Registers[ACC] = Registers[ACC] + Memory[Address].OperandValue  # value in accumulator + value stored in the
    # memory location, store the answer in accumulator
    Registers = SetFlags(Registers[ACC], Registers)
    if Registers[STATUS] == ConvertToDecimal("001"):
        ReportRunTimeError("Overflow", Registers)  # report overflow error if V flag is set
    return Registers


def ExecuteSUB(Memory, Registers, Address):
    Registers[ACC] = Registers[ACC] - Memory[Address].OperandValue  # value in accumulator - value stored in the
    # memory location, store the answer in accumulator
    Registers = SetFlags(Registers[ACC], Registers)
    if Registers[STATUS] == ConvertToDecimal("001"):
        ReportRunTimeError("Overflow", Registers)  # report overflow error if V flag is set
    return Registers


def ExecuteCMPimm(Registers, Operand):
    Value = Registers[ACC] - Operand  # value in accumulator - operand value
    Registers = SetFlags(Value, Registers)  # update flags if the value in accumulator is equal to operand (Z flag)
    # or less than operand value (N flag)
    return Registers


def ExecuteBEQ(Registers, Address):
    StatusRegister = ConvertToBinary(Registers[STATUS])  # get the binary value of status register
    FlagZ = StatusRegister[0]
    if FlagZ == "1":  # check if Z flag is set (accumulator is equal to operand)
        Registers[PC] = Address
    return Registers


def ExecuteJMP(Registers, Address):
    Registers[PC] = Address  # update pc with the operand value
    return Registers


def ExecuteSKP():
    return


def DisplayStack(Memory, Registers):
    print("Stack contents:")
    print(" ----")
    for Index in range(Registers[TOS], HI_MEM):
        print("|{:>3d} |".format(Memory[Index].OperandValue))
    print(" ----")


def ExecuteJSR(Memory, Registers, Address):
    StackPointer = Registers[TOS] - 1
    Memory[StackPointer].OperandValue = Registers[PC]  # return address is stored on the top of the stack
    Registers[PC] = Address  # pc is updated to new address specified by the operand
    Registers[TOS] = StackPointer  # top of the stack pointer is updated
    DisplayStack(Memory, Registers)
    return Memory, Registers


def ExecuteRTN(Memory, Registers):
    StackPointer = Registers[TOS]  # get return address from top of the stack
    Registers[TOS] += 1  # update top of stack
    Registers[PC] = Memory[StackPointer].OperandValue  # return address is copied to the pc
    return Registers


def Execute(SourceCode, Memory):
    Registers = [0, 0, 0, 0, 0]  # pc, acc, status, tos, err --> are all set to 0 by default
    Registers = SetFlags(Registers[ACC], Registers)  # update status based on value of accumulator
    Registers[PC] = 0  # reset pc to 0
    Registers[TOS] = HI_MEM  # reset tos to 20
    FrameNumber = 0  # reset frame number to 0
    DisplayFrameDelimiter(FrameNumber)
    DisplayCurrentState(SourceCode, Memory, Registers)
    OpCode = Memory[Registers[PC]].OpCode  # get the first opcode from Memory[0],
    # possible values are EMPTYSTRING or ERR or JMP
    while OpCode != "HLT":
        FrameNumber += 1
        print()
        DisplayFrameDelimiter(FrameNumber)
        Operand = Memory[Registers[PC]].OperandValue  # get operand value of instruction specified by pc
        print("*  Current Instruction Register: ", OpCode, Operand)
        Registers[PC] = Registers[PC] + 1  # increment pc
        if OpCode == "LDA":
            Registers = ExecuteLDA(Memory, Registers, Operand)  # operand is an address
        elif OpCode == "STA":
            Memory = ExecuteSTA(Memory, Registers, Operand)  # operand is an address
        elif OpCode == "LDA#":
            Registers = ExecuteLDAimm(Registers, Operand)
        elif OpCode == "ADD":
            Registers = ExecuteADD(Memory, Registers, Operand)  # operand is an address
        elif OpCode == "JMP":
            Registers = ExecuteJMP(Registers, Operand)  # operand is an address
        elif OpCode == "JSR":
            Memory, Registers = ExecuteJSR(Memory, Registers, Operand)  # operand is an address
        elif OpCode == "CMP#":
            Registers = ExecuteCMPimm(Registers, Operand)
        elif OpCode == "BEQ":
            Registers = ExecuteBEQ(Registers, Operand)  # operand is an address
        elif OpCode == "SUB":
            Registers = ExecuteSUB(Memory, Registers, Operand)  # operand is an address
        elif OpCode == "SKP":
            ExecuteSKP()
        elif OpCode == "RTN":
            Registers = ExecuteRTN(Memory, Registers)
        if Registers[ERR] == 0:  # checks if there is runtime error
            OpCode = Memory[Registers[PC]].OpCode  # get opcode of instruction specified by pc
            DisplayCurrentState(SourceCode, Memory, Registers)
        else:
            OpCode = "HLT"
    print("Execution terminated")


def AssemblerSimulator():
    SourceCode = [EMPTY_STRING for Lines in range(HI_MEM)]  # Initialise with 20 empty strings
    Memory = [AssemblerInstruction() for Lines in range(HI_MEM)]  # Initialise 20 Objects containing opcode, operand
    # string and operand value
    SourceCode = ResetSourceCode(SourceCode)  # Making the array empty
    Memory = ResetMemory(Memory)  # Making the objects attributes empty
    Finished = False
    while not Finished:
        # whenever source code is loaded or edited, memory containing the objects is reset to initial values
        DisplayMenu()  # 6 options displayed
        MenuOption = GetMenuOption()  # get valid user input
        # for Lines in range(HI_MEM):
        #     print(Memory[Lines].__dict__)
        if MenuOption == 'L':
            SourceCode = LoadFile(SourceCode)  # assembly code loaded into array, first index reads
            # number of lines read from file
            Memory = ResetMemory(Memory)  # Making the objects attributes empty
        elif MenuOption == 'D':
            if SourceCode[0] == EMPTY_STRING:
                print("Error Code 7")  # no assembly source code to display
            else:
                DisplaySourceCode(SourceCode)
        elif MenuOption == 'E':
            if SourceCode[0] == EMPTY_STRING:
                print("Error Code 8")  # no assembly source code to edit
            else:
                SourceCode = EditSourceCode(SourceCode)
                Memory = ResetMemory(Memory)  # Making the objects attributes empty
        elif MenuOption == 'A':
            if SourceCode[0] == EMPTY_STRING:
                print("Error Code 9")  # no assembly source code to assemble
            else:
                Memory = Assemble(SourceCode, Memory)
        elif MenuOption == 'R':
            if Memory[0].OperandValue == 0:  # pass one is unsuccessful
                print("Error Code 10")
            elif Memory[0].OpCode == "ERR":  # pass two is unsuccessful
                print("Error Code 11")
            else:
                Execute(SourceCode, Memory)  # called when pass one and two are error free
        elif MenuOption == 'X':
            Finished = True
        else:
            print("You did not choose a valid menu option. Try again")
    print("You have chosen to exit the program")


if __name__ == "__main__":
    AssemblerSimulator()


