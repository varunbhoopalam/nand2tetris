// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

  (LOOP)

    @KBD
    D=M         // Get keyboard input value

    @PRESSED
    D;JNE       // if not 0 jump to pressed

    @SCREEN
    D=A

    @Pointer
    M=D     // SCREEN address

    @8192
    D=A

    @Index
    M=D

  (NOTPRESSEDLOOP)
    @Pointer
    D=M         // Store Pointer Address
    M=M+1       // Change Pointer to next row in screen

    A=D         // Go to Pointer Address
    M=0         // Set Row in screen to white

    @Index
    M=M-1
    D=M

    @LOOP
    D;JEQ       // jump to start if index is 0

    @NOTPRESSEDLOOP
    0;JMP


  (PRESSED)

    @SCREEN
    D=A

    @Pointer
    M=D     // SCREEN address

    @8192
    D=A

    @Index
    M=D

  (PRESSEDLOOP)
    @Pointer
    D=M         // Store Pointer Address
    M=M+1       // Change Pointer to next row in screen

    A=D         // Go to Pointer Address
    M=-1        // Set Row in screen to black

    @Index
    M=M-1
    D=M

    @LOOP
    D;JEQ       // jump to start if index is 0

    @PRESSEDLOOP
    0;JMP