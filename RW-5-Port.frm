VERSION 5.00
Object = "{648A5603-2C6E-101B-82B6-000000000014}#1.1#0"; "MSCOMM32.OCX"
Begin VB.Form Base 
   Caption         =   "Read/Write 5 Ports"
   ClientHeight    =   8805
   ClientLeft      =   540
   ClientTop       =   3015
   ClientWidth     =   9375
   FillStyle       =   0  'Solid
   ForeColor       =   &H00000000&
   LinkTopic       =   "Form1"
   ScaleHeight     =   8805
   ScaleMode       =   0  'User
   ScaleTop        =   1
   ScaleWidth      =   9375
   StartUpPosition =   2  'CenterScreen
   Begin VB.TextBox Text23 
      Alignment       =   2  'Center
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Left            =   2880
      TabIndex        =   80
      Text            =   "D/A output"
      Top             =   5760
      Width           =   1095
   End
   Begin VB.CommandButton Command12 
      Caption         =   "-"
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
      Left            =   3240
      Style           =   1  'Graphical
      TabIndex        =   79
      Top             =   6120
      Width           =   375
   End
   Begin VB.TextBox Text22 
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
      Left            =   4200
      TabIndex        =   78
      Top             =   5760
      Width           =   2175
   End
   Begin VB.CommandButton Command11 
      Caption         =   "+"
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
      Left            =   3240
      Style           =   1  'Graphical
      TabIndex        =   77
      Top             =   5280
      Width           =   375
   End
   Begin VB.TextBox Text21 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   315
      Left            =   2040
      TabIndex        =   76
      Text            =   "Write  -> $1AO+01000.00"
      Top             =   4320
      Visible         =   0   'False
      Width           =   2175
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   20
      Left            =   6480
      TabIndex        =   75
      Top             =   1800
      Visible         =   0   'False
      Width           =   1455
   End
   Begin VB.CommandButton Command10 
      BackColor       =   &H000000FF&
      Caption         =   "      Initilize the OMEGA  D3181 D/A        "
      BeginProperty Font 
         Name            =   "MS Sans Serif"
         Size            =   9.75
         Charset         =   0
         Weight          =   700
         Underline       =   0   'False
         Italic          =   0   'False
         Strikethrough   =   0   'False
      EndProperty
      Height          =   735
      Left            =   1920
      MaskColor       =   &H00808080&
      Style           =   1  'Graphical
      TabIndex        =   74
      Top             =   1080
      Visible         =   0   'False
      Width           =   4335
   End
   Begin VB.TextBox Text19 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Left            =   6000
      TabIndex        =   73
      Text            =   "Port 5"
      Top             =   120
      Width           =   855
   End
   Begin VB.TextBox Text50 
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
      Left            =   5880
      TabIndex        =   72
      Top             =   480
      Width           =   1095
   End
   Begin VB.TextBox Text18 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Left            =   4800
      TabIndex        =   71
      Text            =   "Port 4"
      Top             =   120
      Width           =   855
   End
   Begin VB.TextBox Text17 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Left            =   3480
      TabIndex        =   70
      Text            =   "Port 3"
      Top             =   120
      Width           =   855
   End
   Begin VB.TextBox Text16 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Left            =   2040
      TabIndex        =   69
      Text            =   "Port 2"
      Top             =   120
      Width           =   855
   End
   Begin VB.TextBox Text15 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Left            =   600
      TabIndex        =   68
      Text            =   "Port 1"
      Top             =   120
      Width           =   1095
   End
   Begin VB.TextBox Text50 
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
      Left            =   4680
      TabIndex        =   67
      Top             =   480
      Width           =   1095
   End
   Begin VB.TextBox Text50 
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
      Left            =   3240
      TabIndex        =   66
      Top             =   480
      Width           =   1095
   End
   Begin VB.TextBox Text50 
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
      Left            =   1800
      TabIndex        =   65
      Top             =   480
      Width           =   1095
   End
   Begin VB.TextBox Text50 
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
      Left            =   360
      TabIndex        =   64
      Top             =   480
      Width           =   1095
   End
   Begin VB.CommandButton Command9 
      Caption         =   "   Record  All   4  Ports"
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
      Left            =   480
      Style           =   1  'Graphical
      TabIndex        =   63
      Top             =   5760
      Width           =   1455
   End
   Begin VB.TextBox Text14 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Left            =   7680
      TabIndex        =   62
      Top             =   120
      Visible         =   0   'False
      Width           =   1215
   End
   Begin VB.CommandButton Command7 
      Caption         =   "STOP RECORDING"
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
      Left            =   4560
      Style           =   1  'Graphical
      TabIndex        =   61
      Top             =   7440
      Width           =   1335
   End
   Begin VB.CommandButton Command6 
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
      Left            =   5520
      Style           =   1  'Graphical
      TabIndex        =   60
      Top             =   2400
      Visible         =   0   'False
      Width           =   735
   End
   Begin VB.CommandButton Command5 
      Caption         =   "Send"
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
      Left            =   5040
      Style           =   1  'Graphical
      TabIndex        =   59
      Top             =   3960
      Visible         =   0   'False
      Width           =   735
   End
   Begin VB.TextBox Text13 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H000000FF&
      Height          =   315
      Left            =   2400
      TabIndex        =   58
      Text            =   "Finished Writing DATA"
      Top             =   4920
      Visible         =   0   'False
      Width           =   2175
   End
   Begin VB.TextBox Text9 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   315
      Left            =   600
      TabIndex        =   57
      Text            =   "Write DATA to -->"
      Top             =   1920
      Visible         =   0   'False
      Width           =   1575
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   19
      Left            =   7080
      TabIndex        =   56
      Top             =   7560
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   18
      Left            =   7080
      TabIndex        =   55
      Top             =   7200
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   17
      Left            =   7080
      TabIndex        =   54
      Top             =   6840
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   16
      Left            =   7080
      TabIndex        =   53
      Top             =   6480
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   15
      Left            =   7080
      TabIndex        =   52
      Top             =   6120
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   14
      Left            =   7080
      TabIndex        =   51
      Top             =   5760
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   13
      Left            =   7080
      TabIndex        =   50
      Top             =   5400
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   12
      Left            =   7080
      TabIndex        =   49
      Top             =   5040
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   11
      Left            =   7080
      TabIndex        =   48
      Top             =   4680
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   10
      Left            =   7080
      TabIndex        =   47
      Top             =   4320
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   9
      Left            =   7080
      TabIndex        =   46
      Top             =   3960
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   8
      Left            =   7080
      TabIndex        =   45
      Top             =   3600
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   7
      Left            =   7080
      TabIndex        =   44
      Top             =   3240
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   6
      Left            =   7080
      TabIndex        =   43
      Top             =   2880
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   5
      Left            =   7080
      TabIndex        =   42
      Top             =   2520
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   4
      Left            =   7080
      TabIndex        =   41
      Top             =   2160
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   3
      Left            =   7080
      TabIndex        =   40
      Top             =   1800
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   2
      Left            =   7080
      TabIndex        =   39
      Top             =   1440
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Index           =   1
      Left            =   7080
      TabIndex        =   38
      Top             =   1080
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text30 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   255
      Index           =   0
      Left            =   7080
      TabIndex        =   37
      Top             =   720
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   36
      Top             =   720
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text12 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Left            =   7080
      TabIndex        =   35
      Text            =   "Address"
      Top             =   360
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text11 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Left            =   8400
      TabIndex        =   34
      Text            =   "Read"
      Top             =   360
      Visible         =   0   'False
      Width           =   855
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   33
      Top             =   7560
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   32
      Top             =   7200
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   31
      Top             =   6840
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   30
      Top             =   6480
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   29
      Top             =   6120
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   28
      Top             =   5760
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   27
      Top             =   5400
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   26
      Top             =   5040
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   25
      Top             =   4680
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   24
      Top             =   4320
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   23
      Top             =   3960
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   22
      Top             =   3600
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   21
      Top             =   3240
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   20
      Top             =   2880
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   19
      Top             =   2520
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   18
      Top             =   2160
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   17
      Top             =   1800
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   16
      Top             =   1440
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text20 
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
      Left            =   8040
      TabIndex        =   15
      Top             =   1080
      Visible         =   0   'False
      Width           =   1095
   End
   Begin VB.TextBox Text6 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Left            =   6120
      TabIndex        =   14
      Text            =   " - Read -"
      Top             =   3720
      Visible         =   0   'False
      Width           =   975
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
      Left            =   5880
      TabIndex        =   13
      Top             =   3960
      Visible         =   0   'False
      Width           =   1335
   End
   Begin VB.TextBox Text1 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Left            =   600
      TabIndex        =   12
      Text            =   "Select  Port #"
      Top             =   2760
      Width           =   1455
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
      Left            =   3360
      TabIndex        =   11
      Text            =   "SR22"
      Top             =   3960
      Visible         =   0   'False
      Width           =   1575
   End
   Begin VB.TextBox Text4 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   315
      Left            =   2040
      TabIndex        =   10
      Text            =   "Read -> SR22"
      Top             =   3960
      Visible         =   0   'False
      Width           =   1335
   End
   Begin VB.CommandButton Command4 
      Caption         =   "Another Port"
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
      Left            =   480
      Style           =   1  'Graphical
      TabIndex        =   9
      Top             =   6360
      Width           =   1455
   End
   Begin VB.CommandButton Command3 
      Caption         =   "Record All Addresses"
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
      Left            =   480
      Style           =   1  'Graphical
      TabIndex        =   8
      Top             =   5160
      Width           =   1455
   End
   Begin VB.CommandButton Command2 
      Caption         =   "Read 20 Address"
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
      Left            =   480
      Style           =   1  'Graphical
      TabIndex        =   7
      Top             =   4560
      Width           =   1455
   End
   Begin VB.CommandButton Command1 
      Caption         =   "Single R/W"
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
      Left            =   480
      Style           =   1  'Graphical
      TabIndex        =   6
      Top             =   3960
      Width           =   1455
   End
   Begin VB.TextBox Text3 
      BackColor       =   &H8000000F&
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
      ForeColor       =   &H00000000&
      Height          =   195
      Left            =   600
      TabIndex        =   5
      Text            =   "Select one"
      Top             =   3600
      Width           =   1095
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
      Left            =   2040
      TabIndex        =   4
      Text            =   "1"
      Top             =   2760
      Width           =   375
   End
   Begin VB.TextBox Text10 
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
      TabIndex        =   3
      Text            =   "Texmate Data "
      Top             =   1920
      Visible         =   0   'False
      Width           =   1695
   End
   Begin VB.TextBox Text8 
      Appearance      =   0  'Flat
      BackColor       =   &H80000004&
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
      Left            =   3600
      TabIndex        =   2
      Text            =   " File Name  -->"
      Top             =   1920
      Visible         =   0   'False
      Width           =   1455
   End
   Begin VB.CommandButton Command8 
      Caption         =   "EXIT"
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
      Left            =   480
      TabIndex        =   1
      Top             =   7440
      Width           =   1215
   End
   Begin VB.DriveListBox Drive1 
      Height          =   315
      Left            =   2400
      TabIndex        =   0
      Top             =   1920
      Visible         =   0   'False
      Width           =   1095
   End
   Begin MSCommLib.MSComm MSComm1 
      Left            =   4920
      Top             =   6600
      _ExtentX        =   1005
      _ExtentY        =   1005
      _Version        =   393216
      DTREnable       =   -1  'True
   End
End
Attribute VB_Name = "Base"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit
Private Declare Sub Sleep Lib "kernel32.DLL" (ByVal dwMilliseconds As Long)

Dim RW, XX, KK, LL, JJ, cnt, result As Integer             'Dim statements here are local in this form only
Dim ports, cont As Single
Dim Baud, Port, length As Single
Dim volt, MVolt As Double
Dim FileName As String
Dim StringVolt As String
Dim BaudRate(3) As String
Dim InBuff, InBuffer As String
Dim Format7(4) As String
Dim CMDRead As String
Dim CMD As String
Dim AllPorts As Boolean
Dim StopRecording As Boolean
Dim DriveDev As String
Private Sub Command1_Click()            'Single R/W
    RW = 1
    Text4.Visible = True
    Text5.Visible = True
    Text6.Visible = True
    Text7.Visible = True
    Text13.Visible = False
    Text14.Visible = False
    Command5.Visible = True
    Port = Val(Text2.Text)
    Text5.SetFocus
    If Port = 5 Then
        Text4.Text = "Read -> $1RD"
        Text5.Text = "$1RD"
        Text21.Visible = True
    Else
        Text4.Text = "Read -> SR22"
        Text21.Visible = False
    End If
End Sub
Private Sub Command11_Click()           '+   D/A Output
    volt = volt + 0.1
    If volt < 0 Then volt = 0
    If volt > 10 Then volt = 10
    MVolt = volt * 1000
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
    MSComm1.Output = CMD
    Call Sleep(100)
    InBuffer = MSComm1.Input
    MSComm1.Output = Chr(27) + Chr(2) + "E$1RD" + Chr(13)       'Read port E
    Call Sleep(200)
    InBuffer = MSComm1.Input
    length = Len(InBuffer)
    Text22.Text = Mid(InBuffer, 3, 9)
    If length = 0 Then Text22.Text = "No D/A read"
End Sub
Private Sub Command12_Click()           '-  D/A Output
    volt = volt - 0.1
    If volt < 0 Then volt = 0
    If volt > 10 Then volt = 10
    MVolt = volt * 1000
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
    MSComm1.Output = CMD
    Call Sleep(100)
    InBuffer = MSComm1.Input
    MSComm1.Output = Chr(27) + Chr(2) + "E$1RD" + Chr(13)       'Read port E
    Call Sleep(200)
    InBuffer = MSComm1.Input
    length = Len(InBuffer)
    Text22.Text = Mid(InBuffer, 3, 9)
    If length = 0 Then Text22.Text = "No D/A read"
End Sub
Private Sub Command2_Click()            'READ 20 Addreses
    RW = 0
    cnt = 0
    Text11.Visible = True
    Text12.Visible = True
    Text13.Visible = False
    Text14.Visible = True
    Text21.Visible = False
    Text4.Visible = False
    Text5.Visible = False
    Text6.Visible = False
    Text7.Visible = False
    Command5.Visible = False
    Port = Val(Text2.Text)
    Text14.Text = "Port # " + Right(Str(Port), 1)
    If Port < 0 Then Port = 0: Text2.Text = "1"
    If Port > 4 Then Port = 4: Text2.Text = "4"
    
    If Port = 1 Then CMDRead = Chr(27) + Chr(2) + "A"
    If Port = 2 Then CMDRead = Chr(27) + Chr(2) + "B"
    If Port = 3 Then CMDRead = Chr(27) + Chr(2) + "C"
    If Port = 4 Then CMDRead = Chr(27) + Chr(2) + "D"
    
    Text7.Text = ""
    For XX = 0 To 19
        Text20(XX).Visible = True
        Text30(XX).Visible = True
    Next XX
    For LL = 48 To 57
    For KK = 48 To 57
    For JJ = 48 To 57
        CMD = CMDRead + "SR" + Chr(LL) + Chr(KK) + Chr(JJ) + "*"
        Text20(cnt).Text = "Skipped"
        Select Case Chr(LL) + Chr(KK) + Chr(JJ)
            Case "015": GoTo 40
            Case "038": GoTo 40
            Case "047": GoTo 40
            Case "048": GoTo 40
            Case "052": GoTo 40
            Case "053": GoTo 40
            Case "061": GoTo 40
            Case "062": GoTo 40
            Case "063": GoTo 40
            Case "064": GoTo 40
            Case "123": GoTo 40
            Case "124": GoTo 40
            Case "125": GoTo 40
            Case "126": GoTo 40
            Case "127": GoTo 40
            Case "128": GoTo 40
            Case "140": GoTo 40
            Case "141": GoTo 40
            Case "234": GoTo 40
            Case "235": GoTo 40
            Case "236": GoTo 40
            Case "237": GoTo 40
            Case "238": GoTo 40
            Case "239": GoTo 40
            Case "240": GoTo 40
            Case "241": GoTo 40
            Case "242": GoTo 40
            Case "243": GoTo 40
            Case "244": GoTo 40
        End Select
        MSComm1.Output = CMD
        Sleep (30)
        DoEvents
        length = Len(InBuffer)
        If length < 2 Then length = 0 Else length = length - 2
        Text20(cnt).Text = Left(InBuffer, length)
40      Text30(cnt).Text = Right(CMD, 7)
        cnt = cnt + 1
        If cnt = 20 Then
            result = MsgBox("Read Next 20 Registers", 3)
            If result = 2 Then GoTo 100         'result = CANCEL
            If result = 6 Then cnt = 0: GoTo 50 'result = YES
            If result = 7 Then GoTo 100         'result = NO
            cnt = 0
50     End If
    Next JJ
    Next KK
    Next LL
100 Text1.Visible = True
    Text2.Visible = True
    Text2.SetFocus                     'Move curser to Text2
End Sub
Private Sub Command3_Click()            'Record All Addreses
    RW = 0
    StopRecording = False
    'Text1.Visible = False
    'Text2.Visible = False
    Text8.Visible = True
    Text9.Visible = True
    Drive1.Visible = True
    Text10.Visible = True              'Show (Text30 for File Name)
    Text10.Text = "Texmate Data "
    Text11.Visible = True
    Text12.Visible = True
    Text13.Visible = False          'remove Finished Writing DATA
    Text14.Visible = True
    Text21.Visible = False
    Command6.Visible = True
    Port = Text2.Text
    length = Len(Text10.Text)
    Text10.Text = Mid(Text10.Text, 1, length - 1)
    Text10.Text = Text10.Text + Right(Str(Port), 1)
    Text10.SetFocus                    'Move curser to Text30
End Sub
Private Sub Command4_Click()                    'Another Port
    Port = Val(Text2.Text)
    Text1.Visible = True
    Text2.Visible = True
    Text13.Visible = False
    Text14.Visible = False
    Text21.Visible = False
    Port = Port + 1
    If Port < 1 Then Port = 1: Text2.Text = "1"
    
    Text5.Text = "SR22"
    Text4.Text = "Read -> SR22"
    Text21.Visible = False
    If ports = -1 Then GoTo 100
    If Port = 5 Then
        Text5.Text = "$1RD"
        Text4.Text = "Read -> $1RD"
        If RW = 1 Then Text21.Visible = True
    End If
100 If Port > 5 + ports Then Port = 1: Text2.Text = "1"
    length = Len(Text10.Text)
    Text10.Text = Mid(Text10.Text, 1, length - 1)
    Text10.Text = Text10.Text + Right(Str(Port), 1)
    Text2.Text = Port
    Text2.SetFocus                     'Move curser to Text2
    Text7.Text = ""
    cnt = 0
End Sub
Private Sub Command6_Click()                'OK to file name
    StopRecording = False
    cnt = 0
    'Text10.Text = Text10.Text + Right(Str(Port), 1)
    Text14.Visible = True
    Text14.Text = "Port # " + Right(Str(Port), 1)
    FileName = Text10.Text
    Command5.Visible = False
    Text4.Visible = False
    Text5.Visible = False
    Text6.Visible = False
    Text7.Visible = False
    Text9.Visible = False       'Remove (Write Data To -->)
    If DriveDev = "C:" Then DriveDev = "C:/DATA"
    If AllPorts = True Then
        Open DriveDev + "/" + Text10.Text + ".DAT" For Output As #5
        Write #5, "Data from               Port 1            Port 2            Port 3            Port 4"
    Else
        Open DriveDev + "/" + FileName + ".DAT" For Output As #5
        Write #5, Now, "Register Data from Port "; Port
    End If
    Text7.Text = ""
    For XX = 0 To 19
        Text20(XX).Visible = True
        Text30(XX).Visible = True
    Next XX
    For LL = 48 To 57
    For KK = 48 To 57
    For JJ = 48 To 57
    If AllPorts = True Then
        For Port = 1 To 4
            InBuffer = ""
            If Port = 1 Then CMDRead = Chr(27) + Chr(2) + "A"
            If Port = 2 Then CMDRead = Chr(27) + Chr(2) + "B"
            If Port = 3 Then CMDRead = Chr(27) + Chr(2) + "C"
            If Port = 4 Then CMDRead = Chr(27) + Chr(2) + "D"
            CMD = CMDRead + "SR" + Chr(LL) + Chr(KK) + Chr(JJ) + "*"
            Text20(cnt).Text = "Skipped"
            Select Case Chr(LL) + Chr(KK) + Chr(JJ)
                Case "015": GoTo 40
                Case "038": GoTo 40
                Case "047": GoTo 40
                Case "048": GoTo 40
                Case "052": GoTo 40
                Case "053": GoTo 40
                Case "061": GoTo 40
                Case "062": GoTo 40
                Case "063": GoTo 40
                Case "064": GoTo 40
                Case "123": GoTo 40
                Case "124": GoTo 40
                Case "125": GoTo 40
                Case "126": GoTo 40
                Case "127": GoTo 40
                Case "128": GoTo 40
                Case "140": GoTo 40
                Case "141": GoTo 40
                Case "234": GoTo 40
                Case "235": GoTo 40
                Case "236": GoTo 40
                Case "237": GoTo 40
                Case "238": GoTo 40
                Case "239": GoTo 40
                Case "240": GoTo 40
                Case "241": GoTo 40
                Case "242": GoTo 40
                Case "243": GoTo 40
                Case "244": GoTo 40
            End Select
            MSComm1.Output = CMD
            Sleep (50)
            DoEvents
            Format7(Port) = StrFormat7(InBuffer)
            Text20(cnt).Text = Format7(Port)
40          Text30(cnt).Text = Right(CMD, 6)
            If StopRecording = True Then GoTo 200
        Next Port
        DoEvents                                    'needed for windows refresh
        Write #5, "CMD = "; Right(CMD, 6); Chr(9) + Format7(1) + Chr(9) + Chr(9) + Format7(2) + Chr(9) + Chr(9) + Format7(3) + Chr(9) + Chr(9) + Format7(4)
        cnt = cnt + 1
        If cnt = 20 Then cnt = 0      ': GoTo 200
    End If
        
        If AllPorts = False Then
            Port = Val(Text2.Text)
            If Port < 0 Then Port = 0: Text2.Text = "1"
            If Port > 3 Then Port = 3: Text2.Text = "4"
        
            If Port = 1 Then CMDRead = Chr(27) + Chr(2) + "A"
            If Port = 2 Then CMDRead = Chr(27) + Chr(2) + "B"
            If Port = 3 Then CMDRead = Chr(27) + Chr(2) + "C"
            If Port = 4 Then CMDRead = Chr(27) + Chr(2) + "D"
    
            CMD = CMDRead + "SR" + Chr(LL) + Chr(KK) + Chr(JJ) + "*"
            MSComm1.Output = CMD
            Sleep (50)
            DoEvents
            length = Len(InBuffer)
            If length < 2 Then length = 0 Else length = length - 2
            Text20(cnt).Text = Left(InBuffer, length)
            Text30(cnt).Text = Right(CMD, 6)
            cnt = cnt + 1
            
            If StopRecording = True Then GoTo 200
            DoEvents                                    'needed for windows refresh
            Write #5, "CMD = "; CMD, "       Register Data = "; Left(InBuffer, length)
            If cnt = 20 Then cnt = 0      ': GoTo 200
        End If
    Next JJ
    Next KK
    Next LL
150 Text13.Visible = True             'Show Finished Writing DATA
200 Close #5
End Sub
Private Sub Command7_Click()                'Stop Recording
    StopRecording = True
End Sub

Private Sub Command9_Click()                'Record all 4 Ports
    RW = 0
    AllPorts = True
    StopRecording = False
    Text8.Visible = True
    Text9.Visible = True
    Drive1.Visible = True
    Text10.Visible = True              'Show (Text30 for File Name)
    Text11.Visible = True
    Text12.Visible = True
    Text13.Visible = False          'remove Finished Writing DATA
    Text14.Visible = True
    Text21.Visible = False
    Command6.Visible = True
    Text10.Text = "All 4 Ports"
    Text10.SetFocus                    'Move curser to Text30
End Sub

Private Sub Command10_Click()               'Initilize the OMEGA  D3181 D/A?
    cont = MsgBox("Initilize the OMEGA  D3181 D/A?", 4 + 16)
    If cont = 6 Then
        GoTo 100
    Else
        MSComm1.PortOpen = False                            'Close COM #1
        Command10.Visible = False
        ports = -1
        GoTo 200
    End If
100    Port = 5
    For XX = 0 To 6
        Text20(XX).Visible = True
        Text30(XX).Visible = True
    Next XX
    'Text7.Visible = True
    MSComm1.Output = Chr(27) + Chr(2) + "E$1RD" + Chr(13)       'Read port E
    Call Sleep(1000)
    InBuffer = MSComm1.Input
    If InBuffer = "" Then
        MsgBox "BAUD rate Not found -- EXIT"
        MSComm1.PortOpen = False
        GoTo 200
    End If
    Text30(0).Text = "$1RD"
    Text20(0).Text = Mid(InBuffer, 3, 9)
    DoEvents                                    'needed for windows refresh
    MSComm1.Output = Chr(27) + Chr(2) + "E$1RS" + Chr(13)       'READ SETUP
    Call Sleep(1000)
    InBuffer = MSComm1.Input
    Text30(1).Text = "$1RS"
    Text20(1).Text = Mid(InBuffer, 3, 8)
    DoEvents                                     'needed for windows refresh
    MSComm1.Output = Chr(27) + Chr(2) + "E$1WE" + Chr(13)       'WRITE ENABLE
    Call Sleep(1000)
    InBuffer = MSComm1.Input
    Text30(2).Text = "$1WE"
    Text20(2).Text = Mid(InBuffer, 3, 8)
    DoEvents                                     'needed for windows refresh
    MSComm1.Output = Chr(27) + Chr(2) + "E$1SU31020180" + Chr(13) 'Change to 9600 Baud
    Call Sleep(1000)
    InBuffer = MSComm1.Input
    Text30(20).Visible = True
    Text30(20).Text = "$1SU31020180"
    Text20(3).Text = Mid(InBuffer, 3, 8)
    DoEvents                                     'needed for windows refresh
    MSComm1.Output = Chr(27) + Chr(2) + "E$1RS" + Chr(13)       'READ SETUP
    Call Sleep(1000)
    InBuffer = MSComm1.Input
    Text30(4).Text = "$1RS"
    Text20(4).Text = Mid(InBuffer, 3, 8)
    DoEvents                                     'needed for windows refresh
    MSComm1.Output = Chr(27) + Chr(2) + "E$1WE" + Chr(13)       'WRITE ENABLE
    Call Sleep(1000)
    InBuffer = MSComm1.Input
    Text30(5).Text = "$1WE"
    Text20(5).Text = Mid(InBuffer, 3, 8)
    DoEvents                                     'needed for windows refresh
    MSComm1.Output = Chr(27) + Chr(2) + "E$1RR" + Chr(13)       'REMOTE RESET
    Call Sleep(1000)                                            'BAUD RATE NOW SET TO 9600
    InBuffer = MSComm1.Input
    Text30(6).Text = "$1RR"
    Text20(6).Text = Mid(InBuffer, 3, 8)
    DoEvents                                     'needed for windows refresh
    Command10.Visible = False
    MsgBox "BAUD rate for D3181 set to 9600"
    MSComm1.PortOpen = False
    For XX = 0 To 6
        Text20(XX).Visible = False
        Text30(XX).Visible = False
    Next XX
    Text30(20).Visible = False
200 Call Form_Load                              'Start up again using 9600 Baud
End Sub
Private Sub Text2_KeyUP(KeyCode As Integer, Shift As Integer)
    If KeyCode = 13 Then                'Wait for Port Number
        Port = Val(Text2.Text)
        If Port < 1 Then Port = 1: Text2.Text = "1"
        If Port > 5 Then Port = 5: Text2.Text = "5"
        Text7.Text = ""
        Text13.Visible = False          'remove Finished Writing DATA
        
        length = Len(Text10.Text)
        Text10.Text = Mid(Text10.Text, 1, length - 1)
        Text10.Text = Text10.Text + Right(Str(Port), 1)
        
    End If
End Sub
Private Sub Drive1_Change()                 'Select Drive
    DriveDev = Drive1.Drive
    If DriveDev = "a:" Then DriveDev = "A:"
    Drive1.Visible = False
    Text10.SetFocus                     'Move curser to Text10
End Sub
Private Sub text10_KeyUP(KeyCode As Integer, Shift As Integer)  'File name <CR>
    If KeyCode = 13 Then
        StopRecording = False
        cnt = 0
        'Text10.Text = Text10.Text + Right(Str(Port), 1)
        Text14.Visible = True
        Text14.Text = "Port # " + Right(Str(Port), 1)
        FileName = Text10.Text
        Command5.Visible = False
        Text4.Visible = False
        Text5.Visible = False
        Text6.Visible = False
        Text7.Visible = False
        Text9.Visible = False       'Remove (Write Data To -->)
        If DriveDev = "C:" Then DriveDev = "C:/DATA"
        If AllPorts = True Then
            Open DriveDev + "/" + Text10.Text + ".DAT" For Output As #5
            Write #5, "Data from               Port 1            Port 2            Port 3            Port 4"
        Else
            Open DriveDev + "/" + FileName + ".DAT" For Output As #5
            Write #5, Now, "Register Data from Port "; Port + 1
        End If
        Text7.Text = ""
        For XX = 0 To 19
            Text20(XX).Visible = True
            Text30(XX).Visible = True
        Next XX
        For LL = 48 To 57
        For KK = 48 To 57
        For JJ = 48 To 57
        If AllPorts = True Then
            For Port = 1 To 4
                InBuffer = ""
                If Port = 1 Then CMDRead = Chr(27) + Chr(2) + "A"
                If Port = 2 Then CMDRead = Chr(27) + Chr(2) + "B"
                If Port = 3 Then CMDRead = Chr(27) + Chr(2) + "C"
                If Port = 4 Then CMDRead = Chr(27) + Chr(2) + "D"
                CMD = CMDRead + "SR" + Chr(LL) + Chr(KK) + Chr(JJ) + "*"
                Text20(cnt).Text = "Skipped"
                Select Case Chr(LL) + Chr(KK) + Chr(JJ)
                    Case "015": GoTo 40
                    Case "038": GoTo 40
                    Case "047": GoTo 40
                    Case "048": GoTo 40
                    Case "052": GoTo 40
                    Case "053": GoTo 40
                    Case "061": GoTo 40
                    Case "062": GoTo 40
                    Case "063": GoTo 40
                    Case "064": GoTo 40
                    Case "123": GoTo 40
                    Case "124": GoTo 40
                    Case "125": GoTo 40
                    Case "126": GoTo 40
                    Case "127": GoTo 40
                    Case "128": GoTo 40
                    Case "140": GoTo 40
                    Case "141": GoTo 40
                    Case "234": GoTo 40
                    Case "235": GoTo 40
                    Case "236": GoTo 40
                    Case "237": GoTo 40
                    Case "238": GoTo 40
                    Case "239": GoTo 40
                    Case "240": GoTo 40
                    Case "241": GoTo 40
                    Case "242": GoTo 40
                    Case "243": GoTo 40
                    Case "244": GoTo 40
                End Select
                MSComm1.Output = CMD
                Sleep (50)
                DoEvents
                Format7(Port) = StrFormat7(InBuffer)
                Text20(cnt).Text = Format7(Port)
40              Text30(cnt).Text = Right(CMD, 6)
                If StopRecording = True Then GoTo 200
            Next Port
            DoEvents                                    'needed for windows refresh
            Write #5, "CMD = "; Right(CMD, 6); Chr(9) + Format7(1) + Chr(9) + Chr(9) + Format7(2) + Chr(9) + Chr(9) + Format7(3) + Chr(9) + Chr(9) + Format7(4)
            cnt = cnt + 1
            If cnt = 20 Then cnt = 0      ': GoTo 200
        End If
        
        If AllPorts = False Then
            Port = Val(Text2.Text)
            If Port < 0 Then Port = 0: Text2.Text = "1"
            If Port > 3 Then Port = 3: Text2.Text = "4"
        
            If Port = 1 Then CMDRead = Chr(27) + Chr(2) + "A"
            If Port = 2 Then CMDRead = Chr(27) + Chr(2) + "B"
            If Port = 3 Then CMDRead = Chr(27) + Chr(2) + "C"
            If Port = 4 Then CMDRead = Chr(27) + Chr(2) + "D"
    
            CMD = CMDRead + "SR" + Chr(LL) + Chr(KK) + Chr(JJ) + "*"
            MSComm1.Output = CMD
            Sleep (50)
            DoEvents
            length = Len(InBuffer)
            If length < 2 Then length = 0 Else length = length - 2
            Text20(cnt).Text = Left(InBuffer, length)
            Text30(cnt).Text = Right(CMD, 6)
            cnt = cnt + 1
            
            If StopRecording = True Then GoTo 200
            DoEvents                                    'needed for windows refresh
            Write #5, "CMD = "; CMD, "       Register Data = "; Left(InBuffer, length)
            If cnt = 20 Then cnt = 0      ': GoTo 200
        End If
        Next JJ
        Next KK
        Next LL
150     Text13.Visible = True             'Show Finished Writing DATA
200     Close #5
    End If
End Sub
Private Sub Command8_Click()                '(EXIT) Unload form
    Unload Base
    End
End Sub
Private Sub Form_unload(Cancel As Integer)          'Unload form from X
    Unload Base
    End
End Sub
Private Sub Form_Load()
    With MSComm1
        .CommPort = 1
        .Settings = "9600,n,8,1"
        .RThreshold = 1
        .SThreshold = 1
        .PortOpen = True
    End With
    DriveDev = "C:"
    StopRecording = False
    
    For Port = 1 To 5 + ports
        If Port = 1 Then CMD = Chr(27) + Chr(2) + "ASR*"
        If Port = 2 Then CMD = Chr(27) + Chr(2) + "BSR*"
        If Port = 3 Then CMD = Chr(27) + Chr(2) + "CSR*"
        If Port = 4 Then CMD = Chr(27) + Chr(2) + "DSR*"
        If Port = 5 Then CMD = Chr(27) + Chr(2) + "E$1RD" + Chr(13)       'Read port E
        MSComm1.Output = CMD
        Sleep (100)
        InBuffer = MSComm1.Input
        If InBuffer <> "" Then Text50(Port - 1).Text = "9600" Else Text50(Port - 1).Text = "No Port"
        If Port = 5 And Text50(Port - 1) = "No Port" Then
            MSComm1.PortOpen = False                            'Close COM #1
            With MSComm1
                .CommPort = 1
                .Settings = "300,n,8,1"
                .RThreshold = 1
                .SThreshold = 1
                .PortOpen = True
            End With
            MSComm1.Output = Chr(27) + Chr(2) + "E$1RD" + Chr(13)       'Read port E
            Call Sleep(1000)
            InBuffer = MSComm1.Input
            If InBuffer = "" Then
                MSComm1.PortOpen = False                            'Close COM #1
                With MSComm1
                    .CommPort = 1
                    .Settings = "9600,n,8,1"
                    .RThreshold = 1
                    .SThreshold = 1
                    .PortOpen = True
                End With
                Else
                Command10.Visible = True
            End If
        End If
        If Port = 5 And Text50(Port - 1) = "9600" Then Command10.Visible = False
    Next Port
End Sub
Private Sub MSComm1_OnComm()
    Select Case MSComm1.CommEvent
        Case comEvReceive
        InBuffer = MSComm1.Input
        length = Len(InBuffer)
        If length < 2 Then length = 0 Else length = length - 2
        Text7.Text = Left(InBuffer, length)
        If Port = 5 Then
            Text7.Text = Mid(InBuffer, 3, length - 3)
        End If
        If Port = 5 And Command10.Visible = True Then
            Text7.Text = InBuffer
        End If
    End Select
End Sub
Private Sub Text5_KeyUP(KeyCode As Integer, Shift As Integer)
    If KeyCode = 13 Then                'Wait for Port Number
        Text7.Text = ""
        Port = Val(Text2.Text)
        If Port = 1 Then CMD = Chr(27) + Chr(2) + "A" + Text5.Text + "*"
        If Port = 2 Then CMD = Chr(27) + Chr(2) + "B" + Text5.Text + "*"
        If Port = 3 Then CMD = Chr(27) + Chr(2) + "C" + Text5.Text + "*"
        If Port = 4 Then CMD = Chr(27) + Chr(2) + "D" + Text5.Text + "*"
        If Port = 5 Then
            CMD = Chr(27) + Chr(2) + "E" + Text5.Text + Chr(13)
            MSComm1.Output = CMD
            Call Sleep(100)
            InBuffer = MSComm1.Input
            If Mid(CMD, 6, 2) = "AO" Then
                MSComm1.Output = Chr(27) + Chr(2) + "E$1RD" + Chr(13)       'Read port E
                Call Sleep(100)
                InBuffer = MSComm1.Input
            End If
            length = Len(InBuffer)
            Text7.Text = Mid(InBuffer, 3, length - 3)
        Else
            MSComm1.Output = CMD
            Call Sleep(50)
            InBuffer = MSComm1.Input
            length = Len(InBuffer)
            If length < 2 Then length = 0 Else length = length - 2
            Text7.Text = Left(InBuffer, length)
        End If
    End If
End Sub


Private Sub Command5_Click()                'SEND
    Text7.Text = ""
    Port = Val(Text2.Text)
    If Port = 1 Then CMD = Chr(27) + Chr(2) + "A" + Text5.Text + "*"
    If Port = 2 Then CMD = Chr(27) + Chr(2) + "B" + Text5.Text + "*"
    If Port = 3 Then CMD = Chr(27) + Chr(2) + "C" + Text5.Text + "*$"
    If Port = 4 Then CMD = Chr(27) + Chr(2) + "D" + Text5.Text + "*$"
    If Port = 5 Then
        CMD = Chr(27) + Chr(2) + "E" + Text5.Text + Chr(13)
        MSComm1.Output = CMD
        Call Sleep(100)
        InBuffer = MSComm1.Input
        If Mid(CMD, 6, 2) = "AO" Then
            MSComm1.Output = Chr(27) + Chr(2) + "E$1RD" + Chr(13)       'Read port E
            Call Sleep(100)
            InBuffer = MSComm1.Input
        End If
        length = Len(InBuffer)
        If length = 0 Then Text7.Text = "No D/A read": GoTo 100
        Text7.Text = Mid(InBuffer, 3, length - 3)
    Else
        MSComm1.Output = CMD
        Call Sleep(50)
        InBuffer = MSComm1.Input
        length = Len(InBuffer)
        If length < 2 Then length = 0 Else length = length - 2
        Text7.Text = Left(InBuffer, length)
100 End If
End Sub
Function StrFormat7(ByVal InBuffer As String) As String
    length = Len(InBuffer)
    If length < 2 Then length = 0 Else length = length - 2  'strips CR,LF
    InBuff = Left(InBuffer, length)
    If Len(InBuff) = 0 Then InBuff = "       " + InBuff
    If Len(InBuff) = 1 Then InBuff = "      " + InBuff
    If Len(InBuff) = 2 Then InBuff = "     " + InBuff
    If Len(InBuff) = 3 Then InBuff = "    " + InBuff
    If Len(InBuff) = 4 Then InBuff = "   " + InBuff
    If Len(InBuff) = 5 Then InBuff = "  " + InBuff
    If Len(InBuff) = 6 Then InBuff = " " + InBuff
    If Len(InBuff) = 7 Then InBuff = "" + InBuff
    StrFormat7 = InBuff
End Function
