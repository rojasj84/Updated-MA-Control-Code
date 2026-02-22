VERSION 5.00
Begin VB.Form Purge 
   Caption         =   "Purge"
   ClientHeight    =   8490
   ClientLeft      =   60
   ClientTop       =   345
   ClientWidth     =   12075
   ForeColor       =   &H8000000F&
   LinkTopic       =   "Form1"
   ScaleHeight     =   8490
   ScaleWidth      =   12075
   StartUpPosition =   2  'CenterScreen
   WindowState     =   2  'Maximized
   Begin VB.TextBox Text2 
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   375
      Left            =   5040
      TabIndex        =   12
      Text            =   "Type anything"
      Top             =   1680
      Visible         =   0   'False
      Width           =   1455
   End
   Begin VB.CommandButton Command8 
      Caption         =   "-100"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   495
      Left            =   9000
      Style           =   1  'Graphical
      TabIndex        =   11
      Top             =   3960
      Width           =   1215
   End
   Begin VB.CommandButton Command7 
      Caption         =   "+100"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   495
      Left            =   9000
      Style           =   1  'Graphical
      TabIndex        =   10
      Top             =   2880
      Width           =   1215
   End
   Begin VB.CommandButton Command6 
      Caption         =   "-100"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   495
      Left            =   3480
      Style           =   1  'Graphical
      TabIndex        =   9
      Top             =   3960
      Width           =   1215
   End
   Begin VB.CommandButton Command5 
      Caption         =   "+100"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   495
      Left            =   3480
      Style           =   1  'Graphical
      TabIndex        =   8
      Top             =   2880
      Width           =   1215
   End
   Begin VB.CommandButton Command4 
      Caption         =   "Closed"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   495
      Left            =   6840
      Style           =   1  'Graphical
      TabIndex        =   3
      Top             =   3960
      Width           =   975
   End
   Begin VB.CommandButton Command3 
      Caption         =   "Open"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   495
      Left            =   6840
      Style           =   1  'Graphical
      TabIndex        =   2
      Top             =   2880
      Width           =   975
   End
   Begin VB.CommandButton Command2 
      Caption         =   "Closed"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   495
      Left            =   1320
      MaskColor       =   &H8000000F&
      Style           =   1  'Graphical
      TabIndex        =   1
      Top             =   3960
      Width           =   975
   End
   Begin VB.CommandButton Command1 
      Caption         =   "Open"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   495
      Left            =   1320
      Style           =   1  'Graphical
      TabIndex        =   0
      Top             =   2880
      Width           =   975
   End
   Begin VB.Label Label5 
      Alignment       =   2  'Center
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   13.5
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   495
      Left            =   3360
      TabIndex        =   13
      Top             =   1080
      Width           =   6495
   End
   Begin VB.Label Label4 
      Alignment       =   2  'Center
      Caption         =   "DOWN  Motor"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   255
      Left            =   8880
      TabIndex        =   7
      Top             =   3600
      Width           =   1335
   End
   Begin VB.Label Label3 
      Alignment       =   2  'Center
      Caption         =   "UP  Motor"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   255
      Left            =   3480
      TabIndex        =   6
      Top             =   3600
      Width           =   1215
   End
   Begin VB.Label Label2 
      Alignment       =   2  'Center
      Caption         =   "DOWN  Valve"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   255
      Left            =   6720
      TabIndex        =   5
      Top             =   3600
      Width           =   1335
   End
   Begin VB.Label Label1 
      Alignment       =   2  'Center
      Caption         =   "UP  Valve"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   255
      Left            =   1200
      TabIndex        =   4
      Top             =   3600
      Width           =   1215
   End
End
Attribute VB_Name = "Purge"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Private Sub Form_Load()
    Purge.Show
    Call Sleep(1000)
    MsgBox "Close MANUAL advance valves IN and OUT"
    MsgBox "Close RETRACT valves IN and OUT "
    MsgBox "   Close MASTER press valve    "
    Pulses = 4000
    Command1.BackColor = QBColor(12)
    Command3.BackColor = QBColor(12)
    Text2.Visible = True
    Label5.Caption = "NOW purging the system --- type to Quit -"
    Text2.SetFocus
    DoEvents                                        'needed for windows refresh
    Base_AP.MSComm2.Output = "AA8;BA8;A+" + Str$(Pulses) + Chr(13) 'UpValve & DownValve ON, Move UP motor UP
    Call Sleep(500)                'delay 0.5 sec
    Base_AP.MSComm2.Output = "AA8;BA8;B+" + Str$(Pulses + 1000) + Chr(13)     ' Move Down Motor UP
    Call Sleep(5000)                'delay 5 sec
End Sub
Private Sub Text2_KeyUP(KeyCode As Integer, Shift As Integer)
    Command1.BackColor = &H8000000F
    Command3.BackColor = &H8000000F
    DoEvents                                        'needed for windows refresh
    Pulses = 4000
    Base_AP.MSComm2.Output = "AA0;A-" + Str$(Pulses) + Chr(13) 'UpValve & DownValve OFF, Move UP motor Down
    Call Sleep(500)
    Base_AP.MSComm2.Output = "BA8;B-" + Str$(Pulses + 1000) + Chr(13)       ' Move Down Motor DOWN
    Call Sleep(7000)                'delay 7 sec
    Base_AP.MSComm2.Output = "BA0" + Chr(13)                'close down valve
    Text2.Visible = False
    Label5.Caption = ""
    MsgBox "Open RETRACT valve OUT only"
    MsgBox "   Open MASTER press valve    "
    Unload Purge
End Sub
Private Sub Command1_Click()
    Base_AP.MSComm2.Output = "AA8;" + Chr(13)               'UpValve ON
    Command1.BackColor = QBColor(12)
    Command2.BackColor = &H8000000F
    Text2.SetFocus
End Sub

Private Sub Command2_Click()
    Base_AP.MSComm2.Output = "AA0;" + Chr(13)               'UpValve OFF
    Command2.BackColor = QBColor(12)
    Command1.BackColor = &H8000000F
    Text2.SetFocus
End Sub
Private Sub Command3_Click()
    Base_AP.MSComm2.Output = "BA8;" + Chr(13)               'DownValve ON
    Command3.BackColor = QBColor(12)
    Command4.BackColor = &H8000000F
    Text2.SetFocus
End Sub
Private Sub Command4_Click()
    Base_AP.MSComm2.Output = "BA0;" + Chr(13)               'DownValve OFF
    Command4.BackColor = QBColor(12)
    Command3.BackColor = &H8000000F
    Text2.SetFocus
End Sub
Private Sub Command5_Click()
    Base_AP.MSComm2.Output = "A+" + Str$(100) + Chr(13)       'Up Motor UP
    Text2.SetFocus
End Sub
Private Sub Command6_Click()
    Base_AP.MSComm2.Output = "A-" + Str$(100) + Chr(13)       'Up Motor Down
    Text2.SetFocus
End Sub
Private Sub Command7_Click()
    Base_AP.MSComm2.Output = "B+" + Str$(100) + Chr(13)       'Down Motor UP
    Text2.SetFocus
End Sub
Private Sub Command8_Click()
    Base_AP.MSComm2.Output = "B-" + Str$(100) + Chr(13)       'Down Motor Down
    Text2.SetFocus
End Sub
