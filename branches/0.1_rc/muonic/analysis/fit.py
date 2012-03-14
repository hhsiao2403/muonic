#! /usr/bin/env python

"""
Script for performing a fit to a histogramm of recorded 
time differences for the use with QNet
"""


import scipy.optimize as optimize
import numpy
import pylab
import sys
import optimalbins

def main(bincontent=None):

    def decay(p,x):
        return p[0]*numpy.exp(-x/p[1])+p[2]
    
    def error(p,x,y):
        return decay(p,x)-y
    
    if bincontent == None:
    
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
        
        #hist=hist[:-1]
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
        
        # vim: ai ts=4 sts=4 et sw=4

    else:

        # this is then used for the mudecaywindow
        # in muonic
        # we have to adjust the bins
        # to the values of the used histogram

        bins = numpy.linspace(0,20,84)
        bin_centers = bins[:-1] + 0.5*(bins[1]-bins[0])


        p0 = numpy.array([200,2.0,5])

        #try: 
        print bincontent

        output = optimize.leastsq(error,p0,args=(bin_centers,bincontent),full_output=1)
        #except:
        #    print "Fit failed!"
        #    return

        p = output[0]
        covar = output[1]
        
        print "Fit parameters:",p
        print "Covariance matrix:",covar
        
        chisquare=0.
        deviations=error(p,bin_centers,bincontent)
        for i,d in enumerate(deviations):
            chisquare += d*d/decay(p,bin_centers[i])
        
        params = {'legend.fontsize': 13}
        pylab.rcParams.update(params)
        
        nbins = 84
        xmin = bin_centers[0]
        xmax = bin_centers[-1]

        fitx=numpy.linspace(xmin,xmax,100)

        return (bin_centers,bincontent,fitx,decay,p,covar,chisquare,nbins)
        
        #pylab.plot(bin_centers,bincontent,"b^",fitx,decay(p,fitx),"b-")
        #pylab.ylim(0,max(bincontent)+100)
        #pylab.xlabel("Decay time in microseconds")
        #pylab.ylabel("Events in time bin")
        #pylab.legend(("Data","Fit: (%4.2f +- %4.2f) microsec,chisq/ndf=%4.2f"%(p[1],numpy.sqrt(covar[1][1]),chisquare/(nbins-len(p)))))
        #pylab.savefig("fit.png")
        
        # vim: ai ts=4 sts=4 et sw=4


if __name__ == '__main__':
    main()