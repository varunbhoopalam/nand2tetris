// C_PUSH constant 10
@10
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_POP local 0
@LCL
D=M
@0
D=D+A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
// C_PUSH constant 21
@21
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 22
@22
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_POP argument 2
@ARG
D=M
@2
D=D+A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
// C_POP argument 1
@ARG
D=M
@1
D=D+A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
// C_PUSH constant 36
@36
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_POP this 6
@THIS
D=M
@6
D=D+A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
// C_PUSH constant 42
@42
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH constant 45
@45
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_POP that 5
@THAT
D=M
@5
D=D+A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
// C_POP that 2
@THAT
D=M
@2
D=D+A
@R13
M=D
@SP
M=M-1
A=M
D=M
@R13
A=M
M=D
// C_PUSH constant 510
@510
D=A
@SP
A=M
M=D
@SP
M=M+1
// C_POP temp 6
@SP
M=M-1
A=M
D=M
@11
M=D
// C_PUSH local 0
@LCL
D=M
@0
A=A+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH that 5
@THAT
D=M
@5
A=A+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// add@SP
M=M-1
A=M
D=M
A=A-1
M=M+D
// C_PUSH argument 1
@ARG
D=M
@1
A=A+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// sub@SP
M=M-1
A=M
D=M
A=A-1
M=M-D
// C_PUSH this 6
@THIS
D=M
@6
A=A+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// C_PUSH this 6
@THIS
D=M
@6
A=A+D
D=M
@SP
A=M
M=D
@SP
M=M+1
// add@SP
M=M-1
A=M
D=M
A=A-1
M=M+D
// sub@SP
M=M-1
A=M
D=M
A=A-1
M=M-D
// C_PUSH temp 6
@11
D=M
@SP
A=M
M=D
@SP
M=M+1
// add@SP
M=M-1
A=M
D=M
A=A-1
M=M+D
