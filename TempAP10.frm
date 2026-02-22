VERSION 5.00
Begin VB.Form Temp 
   Appearance      =   0  'Flat
   BackColor       =   &H80000016&
   Caption         =   "Input Temperature"
   ClientHeight    =   6210
   ClientLeft      =   60
   ClientTop       =   345
   ClientWidth     =   8940
   LinkTopic       =   "Form1"
   ScaleHeight     =   6210
   ScaleWidth      =   8940
   StartUpPosition =   2  'CenterScreen
   Begin VB.CommandButton Command2 
      BackColor       =   &H80000014&
      Caption         =   "OK"
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
      Left            =   7200
      TabIndex        =   59
      Top             =   480
      Visible         =   0   'False
      Width           =   495
   End
   Begin VB.TextBox Text8 
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   285
      Left            =   6360
      TabIndex        =   9
      Top             =   480
      Visible         =   0   'False
      Width           =   615
   End
   Begin VB.TextBox Text3 
      BackColor       =   &H80000016&
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
      Height          =   285
      Left            =   5160
      TabIndex        =   58
      Text            =   "To What"
      Top             =   480
      Visible         =   0   'False
      Width           =   975
   End
   Begin VB.OptionButton Option4 
      Caption         =   "No"
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
      Left            =   3960
      TabIndex        =   57
      Top             =   840
      Width           =   1215
   End
   Begin VB.OptionButton Option3 
      Caption         =   "yes"
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
      Left            =   3960
      TabIndex        =   56
      Top             =   120
      Width           =   1335
   End
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
      Height          =   285
      Left            =   3960
      TabIndex        =   19
      Text            =   "Change it ?"
      Top             =   480
      Width           =   975
   End
   Begin VB.TextBox Text1 
      BackColor       =   &H80000016&
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
      Height          =   285
      Left            =   1320
      TabIndex        =   55
      Text            =   "Thermocouple Type"
      Top             =   480
      Width           =   1935
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   13
      Left            =   3360
      TabIndex        =   50
      Top             =   4320
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   20
      Left            =   4920
      TabIndex        =   49
      Top             =   5280
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   19
      Left            =   3360
      TabIndex        =   48
      Top             =   5280
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   18
      Left            =   1680
      TabIndex        =   47
      Top             =   5280
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   17
      Left            =   4920
      TabIndex        =   46
      Top             =   4800
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   16
      Left            =   3360
      TabIndex        =   45
      Top             =   4800
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   15
      Left            =   1680
      TabIndex        =   44
      Top             =   4800
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   14
      Left            =   4920
      TabIndex        =   43
      Top             =   4320
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   12
      Left            =   1680
      TabIndex        =   42
      Top             =   4320
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   11
      Left            =   4920
      TabIndex        =   41
      Top             =   3840
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   10
      Left            =   3360
      TabIndex        =   40
      Top             =   3840
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   9
      Left            =   1680
      TabIndex        =   39
      Top             =   3840
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   8
      Left            =   4920
      TabIndex        =   38
      Top             =   3360
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   7
      Left            =   3360
      TabIndex        =   37
      Top             =   3360
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   6
      Left            =   1680
      TabIndex        =   36
      Top             =   3360
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   5
      Left            =   4920
      TabIndex        =   35
      Top             =   2880
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   4
      Left            =   3360
      TabIndex        =   34
      Top             =   2880
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   3
      Left            =   1680
      TabIndex        =   33
      Top             =   2880
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   2
      Left            =   4920
      TabIndex        =   32
      Top             =   2400
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   1
      Left            =   3360
      TabIndex        =   31
      Top             =   2400
      Width           =   1215
   End
   Begin VB.TextBox Text10 
      Appearance      =   0  'Flat
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
      Height          =   285
      Index           =   0
      Left            =   1680
      TabIndex        =   30
      Top             =   2400
      Width           =   1215
   End
   Begin VB.TextBox Text4 
      Alignment       =   1  'Right Justify
      BackColor       =   &H80000016&
      BorderStyle     =   0  'None
      Height          =   255
      Index           =   7
      Left            =   480
      TabIndex        =   21
      Top             =   5280
      Width           =   735
   End
   Begin VB.TextBox Text4 
      Alignment       =   1  'Right Justify
      BackColor       =   &H80000016&
      BorderStyle     =   0  'None
      Height          =   255
      Index           =   6
      Left            =   480
      TabIndex        =   20
      Top             =   4800
      Width           =   735
   End
   Begin VB.TextBox Text4 
      Alignment       =   1  'Right Justify
      BackColor       =   &H80000016&
      BorderStyle     =   0  'None
      Height          =   255
      Index           =   5
      Left            =   480
      TabIndex        =   18
      Top             =   4320
      Width           =   735
   End
   Begin VB.TextBox Text4 
      Alignment       =   1  'Right Justify
      BackColor       =   &H80000016&
      BorderStyle     =   0  'None
      Height          =   255
      Index           =   4
      Left            =   480
      TabIndex        =   17
      Top             =   3840
      Width           =   735
   End
   Begin VB.TextBox Text4 
      Alignment       =   1  'Right Justify
      BackColor       =   &H80000016&
      BorderStyle     =   0  'None
      Height          =   255
      Index           =   3
      Left            =   480
      TabIndex        =   16
      Top             =   3360
      Width           =   735
   End
   Begin VB.TextBox Text4 
      Alignment       =   1  'Right Justify
      BackColor       =   &H80000016&
      BorderStyle     =   0  'None
      Height          =   255
      Index           =   2
      Left            =   480
      TabIndex        =   15
      Top             =   2880
      Width           =   735
   End
   Begin VB.TextBox Text4 
      Alignment       =   1  'Right Justify
      BackColor       =   &H80000016&
      BorderStyle     =   0  'None
      Height          =   255
      Index           =   1
      Left            =   480
      TabIndex        =   14
      Top             =   2400
      Width           =   735
   End
   Begin VB.TextBox Text9 
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   285
      Left            =   7080
      TabIndex        =   13
      Text            =   "Data OK"
      Top             =   1800
      Width           =   1215
   End
   Begin VB.OptionButton Option2 
      Caption         =   "No"
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
      Left            =   7080
      TabIndex        =   12
      Top             =   2040
      Width           =   1215
   End
   Begin VB.OptionButton Option1 
      Caption         =   "yes"
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
      Left            =   7080
      TabIndex        =   11
      Top             =   1320
      Width           =   1215
   End
   Begin VB.TextBox Text7 
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   285
      Left            =   4920
      TabIndex        =   2
      Top             =   1800
      Width           =   1215
   End
   Begin VB.TextBox Text6 
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   285
      Left            =   3360
      TabIndex        =   1
      Top             =   1800
      Width           =   1215
   End
   Begin VB.TextBox Text5 
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   285
      Left            =   1680
      TabIndex        =   0
      Top             =   1800
      Width           =   1215
   End
   Begin VB.TextBox Text4 
      Alignment       =   1  'Right Justify
      BackColor       =   &H80000016&
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
      Index           =   0
      Left            =   360
      TabIndex        =   29
      Text            =   "Segment"
      Top             =   1800
      Width           =   855
   End
   Begin VB.Label Label6 
      Alignment       =   2  'Center
      Caption         =   "type"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   13.5
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      ForeColor       =   &H000000FF&
      Height          =   375
      Left            =   3360
      TabIndex        =   54
      Top             =   480
      Width           =   495
   End
   Begin VB.Label Label5 
      Alignment       =   2  'Center
      Caption         =   "Rate-Hold/Min"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      ForeColor       =   &H00FF0000&
      Height          =   255
      Left            =   4800
      TabIndex        =   53
      Top             =   1440
      Width           =   1455
   End
   Begin VB.Label Label4 
      Alignment       =   2  'Center
      Caption         =   "Final Temp"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      ForeColor       =   &H00008000&
      Height          =   255
      Left            =   3360
      TabIndex        =   52
      Top             =   1440
      Width           =   1215
   End
   Begin VB.Label Label3 
      Alignment       =   2  'Center
      Caption         =   "Starting Temp"
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   400
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      ForeColor       =   &H000000FF&
      Height          =   255
      Left            =   1680
      TabIndex        =   51
      Top             =   1440
      Width           =   1335
   End
   Begin VB.Label Label1 
      Alignment       =   2  'Center
      Height          =   255
      Index           =   7
      Left            =   1200
      TabIndex        =   28
      Top             =   5280
      Width           =   255
   End
   Begin VB.Label Label1 
      Alignment       =   2  'Center
      Height          =   255
      Index           =   6
      Left            =   1200
      TabIndex        =   27
      Top             =   4800
      Width           =   255
   End
   Begin VB.Label Label1 
      Alignment       =   2  'Center
      Height          =   255
      Index           =   5
      Left            =   1200
      TabIndex        =   26
      Top             =   4320
      Width           =   255
   End
   Begin VB.Label Label1 
      Alignment       =   2  'Center
      Height          =   255
      Index           =   4
      Left            =   1200
      TabIndex        =   25
      Top             =   3840
      Width           =   255
   End
   Begin VB.Label Label1 
      Alignment       =   2  'Center
      Height          =   255
      Index           =   3
      Left            =   1200
      TabIndex        =   24
      Top             =   3360
      Width           =   255
   End
   Begin VB.Label Label1 
      Alignment       =   2  'Center
      Height          =   255
      Index           =   2
      Left            =   1200
      TabIndex        =   23
      Top             =   2880
      Width           =   255
   End
   Begin VB.Label Label1 
      Alignment       =   2  'Center
      Height          =   255
      Index           =   1
      Left            =   1200
      TabIndex        =   22
      Top             =   2400
      Width           =   255
   End
   Begin VB.Label Label2 
      Alignment       =   2  'Center
      Height          =   255
      Index           =   6
      Left            =   1080
      TabIndex        =   10
      Top             =   4440
      Width           =   255
   End
   Begin VB.Label Label2 
      Alignment       =   2  'Center
      Height          =   255
      Index           =   5
      Left            =   1080
      TabIndex        =   8
      Top             =   3960
      Width           =   255
   End
   Begin VB.Label Label2 
      Alignment       =   2  'Center
      Height          =   255
      Index           =   4
      Left            =   1080
      TabIndex        =   7
      Top             =   3480
      Width           =   255
   End
   Begin VB.Label Label2 
      Alignment       =   2  'Center
      Height          =   255
      Index           =   3
      Left            =   1080
      TabIndex        =   6
      Top             =   3000
      Width           =   255
   End
   Begin VB.Label Label2 
      Alignment       =   2  'Center
      Height          =   255
      Index           =   2
      Left            =   1080
      TabIndex        =   5
      Top             =   2520
      Width           =   255
   End
   Begin VB.Label Label2 
      Alignment       =   2  'Center
      Height          =   255
      Index           =   1
      Left            =   1080
      TabIndex        =   4
      Top             =   2400
      Width           =   255
   End
   Begin VB.Label Label1 
      Alignment       =   2  'Center
      Caption         =   "1"
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
      Index           =   0
      Left            =   1200
      TabIndex        =   3
      Top             =   1800
      Width           =   255
   End
End
Attribute VB_Name = "Temp"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Dim YY As Integer
Dim XX As Integer
Private Sub Form_Load()
    Call ReadTexmate(CMD, 1, Result)        'Extra read needed after D/A write
    CMD = "SR170*"                          'Read NEW meter #1
    Call ReadTexmate(CMD, 1, Result)
    If Left$(Result, 3) = "253" Then TcType = "C"
    If Left$(Result, 3) = "252" Then TcType = "S"
    If Left$(Result, 3) = "251" Then TcType = "mv"
    Label6.Caption = TcType
    Call Sleep(50)
End Sub

Private Sub Text8_KeyUP(KeyCode As Integer, Shift As Integer)
    If KeyCode = 13 Then
        If Text8.Text = "c" Or Text8.Text = "C" Then CMD = "SW170 253*"  'Write "C" type meter #1
        If Text8.Text = "s" Or Text8.Text = "S" Then CMD = "SW170 252*"  'Write "S" type meter #1
        If Text8.Text = "mv" Or Text8.Text = "MV" Then CMD = "SW170 251*"  'Write "mv" type meter #1
        If Left$(CMD, 5) <> "SW170" Then
            MsgBox "SORRY only {C,S,mv} type allowed"
            Text8.Text = ""
            Text8.SetFocus
            GoTo 200
        End If
        Call ReadTexmate(CMD, 1, Result)
        Call Sleep(50)
        CMD = "SR170*"
        Call ReadTexmate(CMD, 1, Result)
        Call Sleep(50)
        If Left$(Result, 3) = "253" Then TcType = "C"
        If Left$(Result, 3) = "252" Then TcType = "S"
        If Left$(Result, 3) = "251" Then TcType = "mv"
        Label6.Caption = TcType
        Option3.Visible = False
        Option4.Visible = False
        Text2.Visible = False
        Text3.Visible = False
        Text8.Visible = False
        Command2.Visible = False
        Text5.SetFocus                  'Place
        Base_AP.Text38.Text = TcType    'set Temperature thermocoupe type --- TcType
200
   End If
End Sub
Public Sub Command2_Click()
    If Text8.Text = "c" Or Text8.Text = "C" Then CMD = "SW170 253*"  'Write "C" type meter #1
    If Text8.Text = "s" Or Text8.Text = "S" Then CMD = "SW170 252*"   'Write "S" type meter #1
    If Text8.Text = "mv" Or Text8.Text = "MV" Then CMD = "SW170 251*"   'Write "mv" type meter #1
    If Left$(CMD, 5) <> "SW170" Then
        MsgBox "SORRY only {C,S,mv} type allowed"
        Text8.Text = ""
        Text8.SetFocus
        GoTo 200
    End If
    Call ReadTexmate(CMD, 1, Result)
    Call Sleep(50)
    CMD = "SR170*"
    Call ReadTexmate(CMD, 1, Result)
    Call Sleep(50)
    If Left$(Result, 3) = "253" Then TcType = "C"
    If Left$(Result, 3) = "252" Then TcType = "S"
    If Left$(Result, 3) = "251" Then TcType = "mv"
    Label6.Caption = TcType
    Option3.Visible = False
    Option4.Visible = False
    Text2.Visible = False
    Text3.Visible = False
    Text8.Visible = False
    Command2.Visible = False
    Text5.SetFocus                  'Place
    Base_AP.Text38.Text = TcType       'set Temperature thermocoupler type --- TcType
200
End Sub

Private Sub Option1_Click()                 'Data OK ---- YES
    'Debug.Print "From Input Temperature"
    'For XX = 1 To TSN - 1
    '    Debug.Print XX, TStart(XX), TEnd(XX), TRate(XX)
    'Next XX
    MaxTSN = TSN
    If Str$(TStart(TSN)) = 0 Then MaxTSN = TSN - 1
    Unload Temp
    StartTemp = 1
    ReDo = 1                'replot after exit
End Sub
Private Sub Option2_Click()                 'Data OK ---- No
    YY = 0
    For XX = 1 To TSN - 1
        Text4(XX).Text = ""
        Label1(XX).Caption = ""
        TStart(XX) = "0"
        Text10(0 + YY).Text = ""
        TEnd(XX) = "0"
        Text10(1 + YY).Text = ""
        TRate(XX) = "0"
        Text10(2 + YY).Text = ""
        YY = YY + 3
    Next XX
    Label1(0).Caption = "1"
    TSN = 0
    YY = 0
    Text5.SetFocus
    Option2.Value = False           'clear selection dot
End Sub
Private Sub Option3_Click()             'Yes change TC
    Text3.Visible = True
    Text8.Visible = True
    Command2.Visible = True
    Text8.SetFocus
End Sub
Private Sub Option4_Click()                     'NO change
    Text5.SetFocus
End Sub
Private Sub Text5_KeyUP(KeyCode As Integer, Shift As Integer)
    TSN = Val(Label1(0).Caption)
    TStart(TSN) = Val(Text5.Text)
    If KeyCode = 13 Then Text6.SetFocus
End Sub
Private Sub Text6_KeyUP(KeyCode As Integer, Shift As Integer)
    TEnd(TSN) = Val(Text6.Text)
    If KeyCode = 13 Then Text7.SetFocus
End Sub
Private Sub Text7_KeyUP(KeyCode As Integer, Shift As Integer)
    TRate(TSN) = Val(Text7.Text)
    If (KeyCode = 13) Then
        If TSN = 1 Then YY = 0
        If TSN = 8 Then
            MsgBox "Can't make another Segment"
            GoTo 200
        End If
        If TRate(TSN) = 0 Then
            MsgBox "Rate of ZERO not allowed"
            Text7.Text = ""
            Text7.SetFocus
            GoTo 200
        End If
        Text4(TSN).Text = "Segment"
        Label1(TSN).Caption = TSN
        Text10(0 + YY).Text = Str$(TStart(TSN))
        Text10(1 + YY).Text = Str$(TEnd(TSN))
        Text10(2 + YY).Text = Str$(TRate(TSN))
        YY = YY + 3
    TSN = Val(Label1(TSN).Caption) + 1
    Label1(0).Caption = TSN
    Text5.SetFocus
    Text5.Text = ""
    Text6.Text = ""
    Text7.Text = ""
200
    End If
End Sub

