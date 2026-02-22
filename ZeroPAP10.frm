VERSION 5.00
Begin VB.Form ZeroP 
   Caption         =   "Zero Pressure"
   ClientHeight    =   5175
   ClientLeft      =   60
   ClientTop       =   345
   ClientWidth     =   8925
   LinkTopic       =   "Form1"
   ScaleHeight     =   5175
   ScaleWidth      =   8925
   StartUpPosition =   2  'CenterScreen
   Begin VB.TextBox Text5 
      BackColor       =   &H80000000&
      BorderStyle     =   0  'None
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
      Left            =   5400
      TabIndex        =   7
      Text            =   "New  Reading"
      Top             =   2040
      Visible         =   0   'False
      Width           =   1815
   End
   Begin VB.TextBox Text4 
      BackColor       =   &H80000000&
      BorderStyle     =   0  'None
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
      Left            =   2160
      TabIndex        =   6
      Text            =   "Current Reading"
      Top             =   2040
      Width           =   1815
   End
   Begin VB.TextBox Text3 
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   12
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   375
      Left            =   4800
      TabIndex        =   5
      Text            =   "Zero Pressure reading ?"
      Top             =   2400
      Visible         =   0   'False
      Width           =   2655
   End
   Begin VB.OptionButton Option2 
      Caption         =   "No"
      Height          =   495
      Left            =   4920
      TabIndex        =   4
      Top             =   2880
      Visible         =   0   'False
      Width           =   1215
   End
   Begin VB.OptionButton Option1 
      Caption         =   "Yes"
      Height          =   495
      Left            =   4920
      TabIndex        =   3
      Top             =   1800
      Visible         =   0   'False
      Width           =   1215
   End
   Begin VB.TextBox Text2 
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   12
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   375
      Left            =   1800
      TabIndex        =   2
      Top             =   2400
      Width           =   2175
   End
   Begin VB.CommandButton Command1 
      Caption         =   "Exit"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   495
      Left            =   7440
      TabIndex        =   1
      Top             =   4440
      Width           =   1215
   End
   Begin VB.TextBox Text1 
      BackColor       =   &H80000000&
      BorderStyle     =   0  'None
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   375
      Left            =   2160
      TabIndex        =   0
      Text            =   "Make sure NO pressure exists on the press valves"
      Top             =   1200
      Width           =   5295
   End
End
Attribute VB_Name = "ZeroP"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False

Private Sub Form_Load()
    ZeroP.Show
    MsgBox "Open MAIN PRESS valve "
    MsgBox "Open MANUAL ADVANCE valve "
    MsgBox "Open MANUAL BLEED valve "
    DoEvents
    CMD = "SR*"                             'Read Pressure Meters
    Call ReadTexmate(CMD, 2, Result)        'clear first reading
    Call Sleep(50)
    Call ReadTexmate(CMD, 2, Result)
    Text2.Text = Result
    Option1.Visible = True
    Option2.Visible = True
    Text3.Visible = True
End Sub
Private Sub Command1_Click()               '(EXIT) Unload form
    Unload ZeroP
End Sub
Private Sub Option1_Click()
    Result = Text2.Text
    Result = Left(Result, 5)
    CMD = "SW028 " & -Result & "*"       'Zero Pressure scale if needed
    Call ReadTexmate(CMD, 2, Result)
    Call Sleep(50)
    CMD = "SR*"                             'Read Pressure Meters
    Call ReadTexmate(CMD, 2, Result)
    Text3.Text = Result
    Text5.Visible = True
    Option1.Visible = False
    Option2.Visible = False
End Sub
Private Sub Option2_Click()
    Unload ZeroP
End Sub
