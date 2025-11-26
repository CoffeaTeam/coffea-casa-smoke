from ROOT import TH1D,TFile,TCanvas,THStack,TColor,TPad,TLegend
from ROOT import gROOT
import array
import styling

#Make bin contents. Since we will use the SetContent() and SetError(), we have included the underflow
sig_bins = [0,0,1,2,1,0]
sig_errs = [0,0,0.05,0.1,0.05,0] #MC-stats errors
bkg_bins = [0,50,40,30,20,10]
bkg_errs = [0.0,0.5,0.4,0.3,0.2,0.1] #MC-stats errors
dat_bins = [0,51,41,32,20,10]

#Create histograms for mock signal, backround, and data
h_sig = TH1D("sig","",len(sig_bins)-1,0.,len(sig_bins)-1)
h_bkg = TH1D("bkg","",len(bkg_bins)-1,0.,len(bkg_bins)-1)
h_dat = TH1D("dat","",len(dat_bins)-1,0.,len(dat_bins)-1)

h_sig.SetContent(array.array('d',sig_bins))
h_sig.SetError(array.array('d',sig_errs))
h_bkg.SetContent(array.array('d',bkg_bins))
h_bkg.SetError(array.array('d',bkg_errs))
h_dat.SetContent(array.array('d',dat_bins))

#Make systematic variations by ratios
sys_up   = [1.0,1.01,1.02,1.03,1.04,1.05]
sys_down = [1.0,0.99,0.98,0.97,0.96,0.95]
h_sys_up   = TH1D("bkg_QCDscaleUp","",len(sys_up)-1,0.,len(sys_up)-1)
h_sys_down = TH1D("bkg_QCDscaleDown","",len(sys_down)-1,0.,len(sys_down)-1)
h_sys_up.SetContent(array.array('d',sys_up))
h_sys_down.SetContent(array.array('d',sys_down))
h_sys_up.Multiply(h_bkg)
h_sys_down.Multiply(h_bkg)

#Write the histograms into a root-file
f = TFile("shape.root","RECREATE")
h_sig.Write()
h_bkg.Write()
h_dat.Write()
h_sys_up.Write()
h_sys_down.Write()
f.Close()

gROOT.SetBatch() #Prevent the prompt of TCanvas

#plotting part
styling.set_style() #Some custom parameters stored in a separate python file
#Some of my favourite colours
g0 = TColor.GetColor(225,110,101)
g1 = TColor.GetColor(205,75,147)
g2 = TColor.GetColor(234,62,36)
g3 = TColor.GetColor(106,196,162)
g4 = TColor.GetColor(20,175,208)
g5 = TColor.GetColor(0,121,115)
g6 = TColor.GetColor(104,103,175)
g7 = TColor.GetColor(65,84,214)
g8 = TColor.GetColor(44,33,104)

#Add histograms into a stack
hs = THStack()
hs.Add(h_bkg)
hs.Add(h_sig)
h_bkg.SetFillColor(g4)
h_sig.SetFillColor(g0)
h_bkg.SetLineColor(g4)
h_sig.SetLineColor(g0)

#Even though we only have one panel, we still use TPad as these are simplified from the 2-panel codes
c = TCanvas("c","",600,600)
c.SetFillStyle(4000)
pup = TPad("pad","",0.,0.,1.0,0.99)
pup.SetFillStyle(4000)
c.cd()
pup.Draw()

#Plot the comparison between our mock data, signal and background
pup.cd()
pup.SetLeftMargin(0.14)
hs.Draw("HIST")
hs.GetXaxis().SetNdivisions(505)
hs.GetXaxis().SetTitle("Variable")
hs.GetYaxis().SetTitle("Events")
h_dat.SetMarkerStyle(20)
h_dat.SetMarkerColor(1)
h_dat.SetLineColor(1)
h_dat.Draw("EX0same")
sig_max = h_sig.GetBinContent(h_sig.GetMaximumBin())
bkg_max = h_bkg.GetBinError(h_bkg.GetMaximumBin())+h_bkg.GetBinContent(h_bkg.GetMaximumBin())
dat_max = h_dat.GetBinContent(h_dat.GetMaximumBin())
hs.SetMaximum(max(sig_max,bkg_max,dat_max)*1.1)

#Legend
lg0 = TLegend(0.65,0.7,0.99,0.9)
lg0.SetBorderSize(0)
lg0.SetFillStyle(4000)
lg0.AddEntry(h_dat,"Data","P")
lg0.AddEntry(h_sig,"sig","F")
lg0.AddEntry(h_bkg,"bkg","F")
lg0.Draw()

c.Print("dist_var.png")

#Now switch to plot the systematic variation of the background
h_bkg.SetLineColor(1)
h_bkg.SetMarkerColor(1)
h_bkg.SetMarkerSize(2)
h_bkg.SetFillStyle(4000)
h_sys_up.SetLineColor(2)
h_sys_down.SetLineColor(4)
h_bkg.SetLineWidth(2)
h_sys_up.SetLineWidth(2)
h_sys_down.SetLineWidth(2)

#Create a 2 panel canvas
c = TCanvas("c1","",600,800)
c.SetFillStyle(4000)
pup = TPad("pad_up","",0.,0.2,1.0,1.0,0,0,0)
pup.SetTopMargin(0.05*(700./600.))
pup.SetBottomMargin(0.1)
pup.SetLeftMargin(0.14)
pup.SetRightMargin(0.05)
pup.SetFrameBorderMode(0)
pup.SetFillStyle(4000)
plo = TPad("pad_lo","",0.,0.,1.0,0.28,0,0,0)
plo.SetTopMargin(0.0)
plo.SetBottomMargin(0.37*(700./800.))
plo.SetLeftMargin(0.14)
plo.SetRightMargin(0.05)
plo.SetFrameBorderMode(0)
plo.SetFillStyle(4000)
c.cd()
plo.Draw()
pup.Draw()

#Plot the original histograms in the upper panel
pup.cd()
h_bkg.GetXaxis().SetTitle("")
h_bkg.GetXaxis().SetNdivisions(505)
h_bkg.GetXaxis().SetLabelSize(0)
h_bkg.GetXaxis().SetTickLength(0.02)
offset = 0.7*pup.GetWh()/pup.GetWw()
h_bkg.GetYaxis().SetTitle("Events")
h_bkg.GetYaxis().SetTitleOffset(offset*1.5)
h_bkg.GetYaxis().SetTitleSize(0.05)
h_bkg.GetYaxis().SetLabelSize(0.05)
h_bkg.Draw("E")
h_sys_up.Draw("HISTsame")
h_sys_down.Draw("HISTsame")
nom_max = h_bkg.GetBinContent(h_bkg.GetMaximumBin())
up_max = h_sys_up.GetBinContent(h_sys_up.GetMaximumBin())
down_max = h_sys_down.GetBinContent(h_sys_down.GetMaximumBin())
h_bkg.SetMaximum(max(nom_max,up_max,down_max)*1.2)

#Legend
lg1 = TLegend(0.50,0.7,0.99,0.9)
lg1.SetBorderSize(0)
lg1.SetFillStyle(4000)
lg1.AddEntry(h_bkg,"bkg","LP")
lg1.AddEntry(h_sys_up,"bkg_QCDscaleUp","L")
lg1.AddEntry(h_sys_down,"bkg_QCDscaleDown","L")
lg1.Draw()

#Plot the ratio of Up to nominal and Down to noninal in the lower panel
plo.cd()
r_up = h_sys_up.Clone("r_up")
r_down = h_sys_down.Clone("r_down")
r_up.Divide(h_bkg)
r_down.Divide(h_bkg)
hsr = THStack()
hsr.Add(r_up)
hsr.Add(r_down)
hsr.SetMaximum(1.17)
hsr.SetMinimum(0.83)
hsr.Draw("HISTnostack")
hsr.GetXaxis().SetTitleOffset(0.7)
hsr.GetXaxis().SetNdivisions(505)
hsr.GetXaxis().SetTitle("Variable")
hsr.GetXaxis().SetTitleSize(0.15)
hsr.GetXaxis().SetLabelSize(0.1)
hsr.GetXaxis().SetTickLength(0.04)
hsr.GetYaxis().SetTitleOffset(offset*0.5)
hsr.GetYaxis().SetTitle("Ratio")
hsr.GetYaxis().SetTitleSize(0.15)
hsr.GetYaxis().SetTickLength(0.02)
hsr.GetYaxis().SetLabelSize(0.1)
r_up_min = r_up.GetBinContent(r_up.GetMinimumBin())
r_down_min = r_down.GetBinContent(r_down.GetMinimumBin())
hsr.SetMinimum(min(r_up_min,r_down_min)*0.9)

c.Print("sys_var.png")
