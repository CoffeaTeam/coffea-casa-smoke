from ROOT import gROOT, gPad, gStyle, ROOT, TLatex

def set_style():
    #setStyle
    icol=0
    gStyle.SetFrameBorderMode(icol)
    gStyle.SetFrameFillColor(icol)
    gStyle.SetCanvasBorderMode(icol)
    gStyle.SetCanvasColor(icol)
    gStyle.SetPadBorderMode(icol)
    gStyle.SetPadColor(icol)
    gStyle.SetStatColor(icol)
    
    # set the paper & margin sizes
    gStyle.SetPaperSize(20,26)
    
    # set margin sizes
    gStyle.SetPadTopMargin(0.05)
    gStyle.SetPadRightMargin(0.05)
    gStyle.SetPadBottomMargin(0.16)
    gStyle.SetPadLeftMargin(0.20)
    
    #  set title offsets (for axis label)
    gStyle.SetTitleXOffset(1.4)
    gStyle.SetTitleYOffset(1.4)
    
    #  use large fonts
    # Int_t font=72 #  Helvetica italics
    font=42 #  Helvetica
    tsize=0.05
    gStyle.SetTextFont(font)
    
    gStyle.SetTextSize(tsize)
    gStyle.SetLabelFont(font,"x")
    gStyle.SetTitleFont(font,"x")
    gStyle.SetLabelFont(font,"y")
    gStyle.SetTitleFont(font,"y")
    gStyle.SetLabelFont(font,"z")
    gStyle.SetTitleFont(font,"z")
    
    gStyle.SetLabelSize(tsize,"x")
    gStyle.SetTitleSize(tsize,"x")
    gStyle.SetLabelSize(tsize,"y")
    gStyle.SetTitleSize(tsize,"y")
    gStyle.SetLabelSize(tsize,"z")
    gStyle.SetTitleSize(tsize,"z")
    
    #  use bold lines and markers
    #gStyle.SetMarkerStyle(20)
    gStyle.SetMarkerSize(0.8)
    #gStyle.SetHistLineWidth(3)
    gStyle.SetLineStyleString(2,"[12 12]") #  postscript dashes
    
    #  get rid of X error bars (as recommended in ATLAS figure guidelines)
    # gStyle.SetErrorX(0.0001) #  this prevents the E2 draw option from working, use X0 option instead
    #  get rid of error bar caps
    gStyle.SetEndErrorSize(0.)
    
    #  do not display any of the standard histogram decorations
    gStyle.SetOptTitle(0)
    # gStyle.SetOptStat(1111)
    gStyle.SetOptStat(0)
    # gStyle.SetOptFit(1111)
    gStyle.SetOptFit(0)
    
    #  put tick marks on top and RHS of plots
    gStyle.SetPadTickX(1)
    gStyle.SetPadTickY(1)

def OutCMS(pad,extraText):
    l = gPad.GetLeftMargin()
    t = gPad.GetTopMargin()
    r = gPad.GetRightMargin()
    posY_ =   1-t+0.2*t
    latex = TLatex()
    latex.SetNDC()
    latex.SetTextFont(61)
    latex.SetTextSize(0.75*t)
    pad.cd()
    latex.DrawLatex(l, posY_, "CMS")
    latex.SetTextFont(52)
    latex.SetTextSize(0.76*0.75*t)
    latex.DrawLatex(l+3*0.75*t, posY_, extraText)

def myText(x,y,color,text,size):
    l = TLatex()
    l.SetNDC()
    l.SetTextSize(size)
    l.SetTextColor(color)
    l.DrawLatex(x,y,text)

def myBoxText(x,y,boxsize,mcolor,text):
    Tsize = 0.05
    l = TLatex()
    l.SetTextAlign(12)
    l.SetNDC()
    l.DrawLatex(x,y,text)
    
    y1=y-0.25*Tsize
    y2=y+0.25*Tsize
    x2=x-0.3*Tsize
    x1=x2-boxsize
    
    mbox = TPave(x1,y1,x2,y2,0,"NDC")
    mbox.SetFillColor(mcolor)
    mbox.SetFillStyle(1001)
    mbox.Draw()
    
    mline = TLine()
    mline.SetLineWidth(4)
    mline.SetLineColor(1)
    mline.SetLineStyle(1)
    y_new = (y1+y2)/2.
    mline.DrawLineNDC(x1,y_new,x2,y_new)

def myMarkerText(x,y,color,mstyle,text,msize):
    Tsize = 0.06
    marker = TMarker(x-(0.4*Tsize),y,8)
    marker.SetMarkerColor(color)
