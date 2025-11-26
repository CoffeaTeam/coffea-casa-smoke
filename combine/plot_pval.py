import ROOT
import styling
import sys

if(len(sys.argv)<4):
    print("Usage: python3 plot_pval.py [data fit's root file] [toy fit's root file] [output file]")
    sys.exit()

ROOT.gROOT.SetBatch() #No prompt

chain = ROOT.TChain("limit")
chain.Add(sys.argv[1]) #The fit with "data"
chain.Add(sys.argv[2]) #The fit with toy "data"

hist_2nll = ROOT.TH1F("hist_2nll","",151,-0.1,15.) #Histogram to fill the -2 times log-likelihood

#Fill the negative log-likelihood times 2
dat_2nll = 0 #2NLL from fit to data
N_toys = int(chain.GetEntries()/2)
for i_toy in range(N_toys):
    chain.GetEntry(i_toy*2+1) #The even entries has deltaNLL = 0 as it has r derived from the fit with floating r
    deltaNLL = getattr(chain,"deltaNLL")
    if i_toy == 0: #The first one is the fit with "data"
        dat_2nll = 2*deltaNLL
    else:
        hist_2nll.Fill(2*deltaNLL)

#Create a histogram to show the regions where the 2NLL is equal or larger than data
hist_gros = hist_2nll.Clone("hist_gros")
for i in range(1,hist_gros.GetNbinsX()+1):
    bin_val = hist_gros.GetBinCenter(i)
    if bin_val < dat_2nll:
        hist_gros.SetBinContent(i,0)
p_value = hist_gros.Integral(0,152)/hist_2nll.Integral(0,152)
print('p-value = {:.3f}'.format(p_value))

#Plotting
styling.set_style()
hist_2nll.SetLineWidth(2)
hist_2nll.SetLineColor(1)
hist_2nll.GetXaxis().SetTitle("-2#DeltalogL")
hist_2nll.GetXaxis().SetTitleSize(0.05)
hist_2nll.GetYaxis().SetTitle("Events")
hist_2nll.GetYaxis().SetTitleSize(0.05)
color = ROOT.TColor.GetColor(112./256.,161./256.,200./256.)
hist_gros.SetLineColor(color)
hist_gros.SetFillColor(color)
can = ROOT.TCanvas("can","",800,600)
can.SetLogy()
can.cd()
hist_2nll.Draw()
hist_gros.Draw("same")
can.RedrawAxis()

#Create a line to marker the 2NLL of data
line = ROOT.TArrow(dat_2nll,hist_2nll.GetMaximum()*0.8,dat_2nll,0,10./can.GetWw(),"|>")
line.SetFillColor(1)
line.SetLineColor(1)
line.SetLineWidth(2)
line.SetAngle(40)
line.Draw()

#Show the p-value
text = ROOT.TLatex()
text.SetTextSize(0.0375)
text.SetTextColor(1)
text.DrawLatex(dat_2nll,hist_2nll.GetMaximum()*0.9,'p-value = {:.2f}'.format(p_value))

can.Print(sys.argv[3])
