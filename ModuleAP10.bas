Attribute VB_Name = "Module"
Option Explicit
'Public Declare Sub PortOut Lib "IO.DLL" (ByVal Port As Integer, ByVal Data As Integer)
'Public Declare Function PortIn Lib "IO.DLL" (ByVal Port As Integer) As Byte
Public Declare Sub Sleep Lib "kernel32.DLL" (ByVal dwMilliseconds As Long)
Public Declare Sub Beep Lib "kernel32.DLL" (ByVal dwFreq As Long, ByVal dwDuration As Long)
                                'Variables here are GLOBAL
                                
Public ReDo As Integer
Public Meter As Integer
Public DaxError As Integer
Public DtoA As Integer
Public Comm1, Comm2 As Integer
Public Volt As Double
Public CMD As String
Public Meter1, Meter3 As String
Global Result As String
Public ReceiveA As String
Public ReceiveB As String
Public Success As Boolean
Public Cont As Boolean
Public BaudRate(4) As String

Public StartTemp As Integer
Public StartPress As Integer
Public MotorTicks As Integer

Public TSN As Integer
Public MaxTSN As Integer
Public TStart(8) As Double         'For Temperature
Public TEnd(8) As Double
Public TRate(8) As Double

Public PSN As Integer            'Variables here are GLOBAL
Public MaxPSN As Integer
Public PStart(8) As Double      'For Pressure
Public PEnd(8) As Double
Public TcType As String         'For Thermocouple Type
Public PRate(8) As Double



Public Sub ReadTexmate(CMD As String, Meter As Integer, Result As String)
Dim OutString As String
    If Meter = 1 Then OutString = Chr(27) + Chr(2) + "A" + CMD      'ESC + Chr 2 + A + >>>>
    If Meter = 2 Then OutString = Chr(27) + Chr(2) + "B" + CMD
    If Meter = 3 Then OutString = Chr(27) + Chr(2) + "C" + CMD
    If Meter = 4 Then OutString = Chr(27) + Chr(2) + "D" + CMD
    Base_AP.MSComm1.Output = OutString
    Call Sleep(120)                          'not any lower time than 70
    Result = Base_AP.MSComm1.Input
End Sub
Public Sub VOUT(DtoA As Integer, Volt As Double)
Dim MVolt, length As Single
Dim StringVolt As String
    If Volt < 0 Then Volt = 0
    If Volt > 10 Then Volt = 10
    MVolt = Int(Volt * 1000)
    StringVolt = Str(MVolt)
    length = Len(StringVolt)
    StringVolt = Right(StringVolt, length - 1)
    If length = 1 Then StringVolt = "+00000" + StringVolt + ".00"
    If length = 2 Then StringVolt = "+0000" + StringVolt + ".00"
    If length = 3 Then StringVolt = "+000" + StringVolt + ".00"
    If length = 4 Then StringVolt = "+00" + StringVolt + ".00"
    If length = 5 Then StringVolt = "+0" + StringVolt + ".00"
    If length = 6 Then StringVolt = "+" + StringVolt + ".00"
    CMD = Chr(27) + Chr(2) + "E" + "$1AO" + StringVolt + Chr(13)
    Base_AP.MSComm1.Output = CMD
End Sub                                            'END OF VOUT
Public Sub InitTexmate(Meter As Integer)

    For Meter = 1 To 4
        CMD = "SR22*"
        Call ReadTexmate(CMD, Meter, Result)
        Call Sleep(50)
        If Result <> "" Then BaudRate(Meter) = "Y"
        
        If Meter = 1 Then GoTo 10
        
        'To Manually switch off lights
        'PROG+UPARROW   at the same time
        'bri-->PROG
        'CAL-->PROG
        'Cod_1-->UPARROW to 200
        'Depress PROG through all codes
        CMD = "SW130 200*"                 'No alarm set points
        Call ReadTexmate(CMD, Meter, Result)
        Call Sleep(50)
10  Next Meter
   
    'To Manually set the Zero Ice Point to ZERO Depress
    'PROG+UPARROW   at the same time
    'br-->PROG
    'cal-->to 101         1=cal,   0=Manual,    1=channel 1
    'off_1-->set to +-??       offset to zero
    'PROG--> back to 000 -->PROG
    
    'CMD = "SW025 1.0000*"               'Temperature scale = 1.0000
    'Call ReadTexmate(CMD, 1, Result)
    'Call Sleep(50)
        
    CMD = "SR170*"                          'Read NEW meter #1  TC type
    Call ReadTexmate(CMD, 1, Result)
    Call Sleep(50)
    If Left$(Result, 3) = "253" Then TcType = "C"
    If Left$(Result, 3) = "252" Then TcType = "S"
    If Left$(Result, 3) = "251" Then TcType = "mv"
    Base_AP.Text38.Text = TcType           'Set thermocouple type on read of new meter
           
    'CMD = "SW200 000*"                  'TC meter No dec pt
    'Call ReadTexmate(CMD, 1, Result)
    'Call Sleep(50)
        
    CMD = "SW025 2.0000*"               'Pressure scale = 2.0000
    Call ReadTexmate(CMD, 2, Result)
    Call Sleep(50)
        
    CMD = "SW028 0.0*"            'Zero Pressure scale if needed
    Call ReadTexmate(CMD, 2, Result)
    Call Sleep(50)
        
    CMD = "SW200 006*"                  'Pressure meter  display 00.0
    Call ReadTexmate(CMD, 2, Result)
    Call Sleep(50)
        
    CMD = "SW025 1.000*"          'Voltage scale use a 9000/1000 resistor divider
    Call ReadTexmate(CMD, 3, Result)    'this will allow the meter to measure over
    Call Sleep(50)                      '30 volts for a La/Cr heater
        
    CMD = "SW028 .01*"          'Zero Voltage scale if needed
    Call ReadTexmate(CMD, 3, Result)
    Call Sleep(50)
        
    CMD = "SW200 005*"                  'Volt meters  display 0.00
    Call ReadTexmate(CMD, 3, Result)
    Call Sleep(50)
        
    CMD = "SW025 .300*"         'Current scale = 0.300 use 300/5 xformer
    Call ReadTexmate(CMD, 4, Result)
    Call Sleep(50)
        
    CMD = "SW028 .1*"           'Zero Current scale if needed
    Call ReadTexmate(CMD, 4, Result)
    Call Sleep(50)
        
    CMD = "SW200 006*"                  'Current meter  display 00.0
    Call ReadTexmate(CMD, 4, Result)
    Call Sleep(50)
     
    If BaudRate(1) = "Y" Or BaudRate(2) = "Y" Or BaudRate(3) = "Y" Or BaudRate(4) = "Y" Then BaudRate(0) = "Baud = 9600"
End Sub
Public Sub SetZero(ReceiveA As String, ReceiveB As String, Success As Boolean)
        Dim TimeInc As Double
        Dim InBuff As String
        
        If Base_AP.MSComm2.PortOpen = False Then GoTo 210       'SKIP if No Ports available
        Base_AP.Label1(22).Caption = "Up Valve Closed"
        Base_AP.Label1(22).ForeColor = QBColor(0)
        Base_AP.Label1(23).Caption = "Down Valve Closed"
        Base_AP.Label1(23).ForeColor = QBColor(0)
        Base_AP.Label1(24).Caption = Format(0 / 300, "#.##")
        Base_AP.Label1(25).Caption = Format(0 / 300, "#.##")
        Base_AP.MSComm2.Output = "AA0;BA0;AM-600;BM-600" + Chr(13) 'UP & DOWN VALVE OFF
        Call Sleep(100)
        
150     If Timer > 86398 Then GoTo 150                      '2 seconds from midnight
        TimeInc = Timer
        Do While Timer < TimeInc + 11                       'Not shorter than 11 sec
            Base_AP.MSComm2.Output = "*^" + Chr(13)         'Read all motor motion
            Call Sleep(100)
            Beep 1250, 100
            DoEvents                                        'needed for windows refresh
            If ReceiveA = "A0" And ReceiveB = "B0" Then Success = True: GoTo 200
        Loop
        DaxError = DaxError + 1
        Base_AP.Label1(39).Caption = DaxError
        
155     If Timer > 86398 Then GoTo 155                      '2 seconds from midnight
        TimeInc = Timer
        Do While Timer < TimeInc + 60                       'Wait 60 sec then continue
            DialogAP.Show
            If Cont = True Then GoTo 160                    'Was OK depressed--continue
            DoEvents                                        'needed for windows refresh
            'Cont = MsgBox("Communication problems --- Switch the DAX Power off/on then depress OK", 4)
            'If Cont = 6 Then GoTo 175
        Loop
160     Cont = False                                        'reset continue flag
        DialogAP.Hide
        
Rem  ***********************************************************************************
Rem  Attempt to reconnect to Comport
        Base_AP.MSComm2.PortOpen = False
        Base_AP.MSComm2.CommPort = Comm2                  'What COMM port
        Base_AP.MSComm2.Settings = "9600,n,8,1"             'For AMS motor controller
        Base_AP.MSComm2.RThreshold = 1                      'For Motor Valve and pressure control
        Base_AP.MSComm2.SThreshold = 1
        Base_AP.MSComm2.PortOpen = True                     'If not available -- an error is generated
        
        Base_AP.MSComm2.Output = "&P3" + Chr(13)            'FIRST 4 CHARS
        Call Sleep(1500)
        InBuff = Base_AP.MSComm2.Input                      'Dump UART Buffer
        Base_AP.MSComm2.Output = "AZ" + Chr(13)             'Read motor position
        Call Sleep(50)
        InBuff = Base_AP.MSComm2.Input                      'Dump UART Buffer
        Call Sleep(50)
        If InBuff = "" Then Success = False Else Success = True
200     Base_AP.MSComm2.Output = "A+50;B+50" + Chr(13)      'move off zero
210     MotorTicks = 0
End Sub

