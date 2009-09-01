import scipy.optimize as optimize
import numpy
import pylab
import sys
import optimalbins

def decay(p,x):
    return p[0]*numpy.exp(-x/p[1])+p[2]

def error(p,x,y):
    return decay(p,x)-y

nbins = 10
xmin = 0.05
xmax = 11.0

times = [float(l) for l in open(sys.argv[1]).readlines() if xmin<float(l)<xmax]
print len(times),"decay times"

#nbins = optimalbins.optbinsize(times,1,30)
print "Nbins:",nbins

bin_edges = numpy.linspace(xmin,xmax,nbins)
bin_centers = bin_edges[:-1] + 0.5*(bin_edges[1]-bin_edges[0])

hist,edges = numpy.histogram(times,bin_edges)

hist=hist[:-1]
p0 = numpy.array([200,2.0,5])

output = optimize.leastsq(error,p0,args=(bin_centers,hist),full_output=1)
p = output[0]
covar = output[1]

print "Fit parameters:",p
print "Covariance matrix:",covar

chisquare=0.
deviations=error(p,bin_centers,hist)
for i,d in enumerate(deviations):
    chisquare += d*d/decay(p,bin_centers[i])

params = {'legend.fontsize': 13}
pylab.rcParams.update(params)

fitx=numpy.linspace(xmin,xmax,100)
pylab.plot(bin_centers,hist,"b^",fitx,decay(p,fitx),"b-")
pylab.ylim(0,max(hist)+100)
pylab.xlabel("Decay time in microseconds")
pylab.ylabel("Events in time bin")
pylab.legend(("Data","Fit: (%4.2f +- %4.2f) microsec,chisq/ndf=%4.2f"%(p[1],numpy.sqrt(covar[1][1]),chisquare/(nbins-len(p)))))
pylab.savefig("fit.png")
