# -*- coding: utf-8 -*-
from __future__ import division

from pylab import *
from numpy import *
import scipy.integrate as integrate
import scipy.signal as sig
from scipy import constants as k
#import bigfloat


class MagneT(object):
    """
    Set of function to calculate the magnetisation in QHE with and without spin splitting.
    """
    def __init__(self,**kwarg):

        self._Xi = kwarg['Xi'] if 'Xi' in kwarg else 0.2
        self._m = kwarg['mass'] if 'mass' in kwarg else 0.067*k.m_e
        self._T = kwarg['Temp'] if 'Temp' in kwarg else 15e-3
        self._p = kwarg['power'] if 'power' in kwarg else 0
        self._N = kwarg['N-LL'] if 'N-LL' in kwarg else 50
        self._ns = kwarg['density'] if 'density' in kwarg else 2.75e15*0.99
        self._mu = self._ns*pi*k.hbar**2/self._m
        self._EF = self._ns*pi*k.hbar**2/self._m
        self._E = linspace(0,2*self._mu,1002)[:, newaxis]
        self._Gam = kwarg['Gamma'] if 'Gamma' in kwarg else self._EF/15
        self._s_default = 0
        self._B = kwarg['Bfield'] if 'Bfield' in kwarg else linspace(0.25,8,5000)

    def fd(self,E = None ,T = None, mu = None):
        """
        Parameters:
            E = energy range over wich to compute fd
            T = electron temperature
            mu = chemical potential (can be an np.array)
        return: the Fermi-Dirac distrubution
        """
        if E: self._E = E
        if T: self.T = T
        if mu: self.mu = mu
        bet = (self._E-self._mu)/(k.k*self._T)
        if shape(self._mu) == ():
            for n in range(shape(self._E)[0]):
                if abs(bet[n]) < 100:
                    bet[n] = 1/(1+exp(bet[n]))
                elif bet[n] < -100:
                    bet[n] = 1
                else:
                    bet[n] = 0               
        else:
            for p in range(shape(self._mu)[0]):
                for n in range(shape(E)[0]):
                    if abs(bet[n,p]) < 100:
                        bet[n,p] = 1/(1+exp(bet[n,p]))
                    elif bet[n,p] < -100:
                        bet[n,p] = 1
                    else:
                        bet[n,p] = 0           
        return bet


    def gEgaussian(self,B = None, E = None, Gam = None, Nmax = None):
        """       
        B is a vector of M elements
        E is a vector of L elements
        Return: the density of state for LL with Gaussian Broadening without 
        spin splitting (M by L matrix)
        """
        if B: self._B = B
        if isinstance(E,(np.ndarray, float,int)) : self._E = E
        if Gam: self._Gam = Gam
        if Nmax: self._N = Nmax
        wc = k.e*self._B/self._m     # M elements
        l = sqrt(k.hbar/(k.e*self._B))  # M elements
        # n = arange(self._N+1)[:, newaxis, newaxis] # N,1 elements (N=Nmax+1)
        n = arange(self._N+1)[:, newaxis, newaxis] # N,1 elements (N=Nmax+1)
        En = k.hbar*wc*(n+1./2) # NxM elements)
        return 1./(pi*l**2) * 1/(sqrt(2*pi)*self._Gam) * sum(exp(-(self._E-En)**2
                                                                 /(2*self._Gam**2)), axis=0)

    def gElorentzian(self,B = None, E = None, Gam = None, Nmax = None):
        """
        return: the density of state for LL with Lorenzian Broadening without spin splitting
        B is a vector of M elements
        E is a vector of L elements
        """

        if isinstance(E,(np.ndarray, float,int)) : self._E = E
        if B: self._B = B
        if Gam: self._Gam = Gam
        if Nmax: self._N = Nmax
        wc = k.e*self._B/self._m     # M elements
        l = sqrt(k.hbar/(k.e*self._B))  # M elements
        n = arange(self._N+1)[:, newaxis, newaxis] # N,1 elements (N=Nmax+1)
        En = k.hbar*wc*(n+1./2) # NxM elements)
        return 1./(pi*l**2) * sum(self._Gam/((self._E-En)**2 + self._Gam**2), axis=0)
    
    def gESS(self,B = None, E = None,  Gam = None , Xi = None, Nmax = None, Bs = 2, alpha = 0, GL = 0):     
        """
        return: the density of state for LL with spin splitted with Gaussian or Lorentzian Broadening
        B is a vector of M elements
        E is a vector of L elements
        """
        if B: self._B = B
        if Gam: self._Gam = Gam
        if Nmax: self._N = Nmax
        if Xi: self._Xi = Xi
        Bp = self._B*cos(alpha)
        Bt = self._B
        gp = 0.44+0.9*(1-1/(1+exp((self._B-Bs)/1)))
        gn = 0.44+0.5*(1-1/(1+exp((self._B-Bs)/0.6)))
        mub = k.e*k.hbar/(2*self._m)
        wc = k.e*Bp/self._m     # M elements
        ws = k.e*Bt/self._m     # M elements
        Dn = gn*mub*Bt/2
        Dp = gp*mub*Bt/2
        p=0
        self._Gam = self._Gam*self._B**self._p
        #    ep = 0.05e-23*B**3
        ep = 0
        l = sqrt(k.hbar/(k.e*Bp))  # M elements
        #    n = arange(Nmax+1)[:, newaxis, newaxis, newaxis] # N,1 elements (N=Nmax+1)
        n = arange(self._N+1)[:, newaxis, newaxis] 
        #    nS = arange((Nmax+1)*2)[:, newaxis] # N,1 elements (N=Nmax+1)
        En = k.hbar*wc*(n+1./2)
        EnP = k.hbar*wc*(n+1./2)+Dp+ep
        EnN = k.hbar*wc*(n+1./2)-Dn
        if GL == 1:
            dos = self._Xi*self._m/(pi*k.hbar**2)+(1-self._Xi)/2* ((1./(pi*l**2) * 1/(sqrt(2*pi)*self._Gam) 
                                                  * sum(exp(-(self._E-EnP)**2/(2*self._Gam**2)),
                                                        axis=0))+ (1./(pi*l**2) * 1/(sqrt(2*pi)*self._Gam) 
                                                                   *sum(exp(-(self._E-EnN)**2/(2*self._Gam**2)), axis=0)))
        else:
            dos = self._Xi*self._m/(pi*k.hbar**2)+(1-self._Xi)*1./(pi*l**2)/2 *(sum(self._Gam/((self._E-EnP)**2 + self._Gam**2), axis=0) +
             sum(self._Gam/((self._E-EnN)**2 + self._Gam**2), axis=0))
        return dos
    
    

    def Dbe(self,B = None, E = None, Gam = None, Xi = None, Nmax = None, gE=gEgaussian):
        """
        returns the density of state (Gaussian or Lorentzian with
        a constant background tuned by Xi
        B is a vector on M elements
        E can also be a vector of L elements
        """
        if B: self._B = B
        if Gam: self._Gam = Gam
        if Nmax: self._N = Nmax
        if Xi: self._Xi = Xi
        single = False
        if not isinstance(B, (list, ndarray)) and not isinstance(E, (list, ndarray)):
            single = True
            Ggi = self.gE()
            ret = self._Xi*m/(pi*k.hbar**2)+(1-self._Xi)*2*k.e*B/(pi*k.h)*Ggi
            if single:
                return ret[0]
            return ret

    def fermi_weight(self,E = None, EF = None, T = None):
        """
        Fermi-Dirac function
        """
        if EF: self._EF = EF
        a = (self._E-self._EF)/(k.k*self._T)
        ret = log( 1. - 1./(1+exp(a)) )
        return ret

    def Omega(self,B = None, EF = None, T = None, Gam = None, Xi = None,  Nmax = None, gE=gEgaussian):
        """
        return: numerical calculation of the thermodynamic grand potential without spin splitting
        B is a vector
        T is the temperature (single value)
        """
        if B: self._B = B
        if EF: self._EF = EF
        if Gam: self._Gam = Gam
        if T: self._T = T
        if Nmax: self._N = Nmax
        if Xi: self._Xi = Xi
        integ_result = empty_like(B)
        integrand = lambda E: self.Dbe(gE = gE)*self.fermi_weight()
        for i,b in enumerate(B):
            integ_result[i], error = integrate.quad(integrand, 0, EF*10)
        return k.k*T * integ_result 
    
    def Om2(self, B = None, mu = None, T = None, Gam = None, Xi = None, m = None, Nmax = None):
        """
        Return: analytical calculation of the Grand thermodynamic potential based on Fourrier decomposition without spin splitting
        """
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if T: self._T = T
        if Nmax: self._N = Nmax
        if Xi: self._Xi = Xi
        wc = k.e*B/m
        hwc = k.hbar*wc
        n = arange(1,Nmax+1)[:, newaxis] # N,1 elements (N=Nmax+1)
        I3 = -(self._mu**2/(2*k.k*self._T)+pi**2*k.k*self._T/6)
        I4 = -(hwc)**2/(4*pi**2*n**2*k.k*self._T) + hwc/(2*n)*cos(2*pi*n*mu/hwc)/sinh(2*pi**2*n*k.k*self._T/hwc)
        return m*k.k*self._T/(pi*k.hbar**2)*(I3+2*(1-self._Xi)*sum((-1)**n*exp(-2*(n*pi*self._Gam)**2/(hwc)**2)*I4, axis=0))

    def OmegaC(self, B = None, T = None, mu = None, Gam = None, Xi = None, Nmax = None, Bs = 2, GL = 1, alpha = 0):
        """
        Numeric calculation of the thermodynamic grand potential, 
        Bs is the field for spin splitting (if Bs = 0 no spin splitting )
        """
        if B: self._B = B
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if T: self._T = T
        if Nmax: self._N = Nmax
        if Xi: self._Xi = Xi
        if shape(self._mu) == ():
            E = linspace(0,2*self._mu,1002)[:, newaxis]
        else:
            E = linspace(0,2*self._mu[0],1002)[:, newaxis]
        bet = (self._mu-E)/(k.k*self._T)
        if shape(self._mu) == ():
            for n in range(shape(E)[0]):
                if abs(bet[n]) < 50:
                    bet[n] = log(1+exp(bet[n]))
                elif (bet[n]) < -50:
                    bet[n] = 0
        else:
            for p in range(shape(self._mu)[0]):
                for n in range(shape(E)[0]):
                    if abs(bet[n,p]) < 50:
                        bet[n,p] = log(1+exp(bet[n,p]))
                    elif (bet[n,p]) < -50:
                        bet[n,p] = 0
                    
        if Bs == 0:
            Z = self.gEgaussian(E = E)*bet
        else:
            Z = self.gESS(E = E, Bs = Bs, alpha = alpha , GL = GL)*bet
        S = sum(Z, axis = 0)
        self._Om = -S*(max(E)-min(E))/shape(E)[0]*k.k*self._T
        return self._Om 
   

    def Mag( self, B = None, ns = None, mu = None, T = None, Gam = None, Xi = None,  p = None, Nmax = None, s = None, phi = 0):
        """
        Return: the Magnetisation in QHE with Gaussian broadening without spin splitting
        calculated with the analytical expression based on the Fourier decomposition
        """
        if B: self._B = B
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if T: self._T = T
        if Nmax: self._N = Nmax
        if Xi: self._Xi = Xi
        if ns: self._ns = ns
        if p: self._p = p
        if self._s_default: self._s_default = s
        wc = k.e*self._B/self._m
        n = arange(1,self._N+1)[:, newaxis] # N,1 elements (N=Nmax+1)
        hwc = k.hbar*wc    
        smu = 2*pi*n*self._mu/(hwc) + phi*2*pi*n #2nd term is a Berry phase 
        skt = 2*pi**2*n*k.k*self._T/(hwc)
        Gam = self._Gam*self._B**self._p
        I4 =  -(hwc)**2/(4*pi**2*n**2*k.k*self._T) + hwc/(2*n)*cos(smu)/sinh(2*pi**2*n*k.k*self._T/hwc)
        DI4 =  1/self._B*(-hwc**2/(2*pi**2*n**2*k.k*self._T)+pi*self._mu*sin(smu)/sinh(skt)+cos(smu)/sinh(skt)*(hwc/(2*n)+pi**2*k.k*self._T*1/tanh(skt)))   
        return -2*self._m*k.k*self._T/(pi*k.hbar**2)*(1-self._Xi)*sum((-1)**n*exp(-2*(n*pi*Gam)**2/(hwc)**2)*(DI4+(1-self._p)*(2*pi*n*Gam/hwc)**2*I4/self._B), axis=0)

    def MagL(self, B = None, ns = None, mu = None, T = None, Gam = None, Xi = None, p = None, Nmax = None, s = None, phi = 0):
        """
        Return: the Magnetisation in QHE with Lorentzian broadening without spin splitting
        calculated by the analytical expression based on the Fourier decomposition
        """
        if B: self._B = B
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if T: self._T = T
        if Nmax: self._N = Nmax
        if ns: self._ns = ns
        if p: self._p = p
        if self._s_default: self._s_default = s
        wc = k.e*self._B/self._m
        n = arange(1,self._N+1)[:, newaxis] # N,1 elements (N=Nmax+1)
        hwc = k.hbar*wc    
        smu = 2*pi*n*self._mu/(hwc) + phi*2*pi*n #2nd term is a Berry phase 
        skt = 2*pi**2*n*k.k*self._T/(hwc)
        Gam = self._Gam*self._B**self._p
        I4 =  -(hwc)**2/(4*pi**2*n**2*k.k*self._T) + hwc/(2*n)*cos(smu)/sinh(2*pi**2*n*k.k*self._T/hwc)
        DI4 =  1/self._B*(-hwc**2/(2*pi**2*n**2*k.k*self._T)+pi*self._mu*sin(smu)/sinh(skt)+cos(smu)/sinh(skt)*(hwc/(2*n)+pi**2*k.k*self._T*1/tanh(skt)))   
        return -2*m*k.k*self._T/(pi*k.hbar**2)*(1-self._Xi)*sum((-1)**n*exp(-2*(n*pi*Gam)/(hwc))*(DI4+(1-self._p)*(2*pi*n*Gam/hwc)*I4/self._B), axis=0)

    def MagC(self,  Om = None, B = None):
        """
        Calculate Magnetization from Grand Potential Omega. 
        Omega needs to be calculated before hands with one of the class function.
        """
        if Om : self._Om = Om
        OmC = sig.savgol_filter(self._Om,21,3)
        self._MagC = -diff(OmC)/diff(self._B)
        return  self._MagC

    def MagCmu(self, Om = None, B = None, mu = None, ns = None):
        """
        Calculate Magnetization from Grand Potential Omega for a constant chemical potential
        """
        if Om : self._Om = Om
        OmC = sig.savgol_filter(self._Om,21,3)
        self._MagCmu = -diff(OmC+self._mu*self._ns)/diff(self._B)
        return self._MagCmu
    
    def nsb(self, B = None, mu = None, T = None, Gam = None, Xi = None, p = None, Nmax = None, s = None, phi = 0):
        """
        Calculates the density of state analytically (for Gaussian LL )
        """
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if T: self._T = T
        if Nmax: self._N = Nmax
        if p: self._p = p
        if self._s_default: self._s_default = s
        wc = k.e*B/self._m
        n = arange(1,self._N+1)[:, newaxis, newaxis] # N,1 elements (N=Nmax+1)
        hwc = k.hbar*wc    
        smu = 2*pi*n*self._mu/(hwc) + phi*2*pi*n #2nd term is a Berry phase 
        skt = 2*pi**2*n*k.k*self._T/(hwc)
        Gam = self._Gam*self._B**self._p
        I1 = self._mu+k.k*self._T*log(1+exp(-self._mu/(k.k*self._T)))
        I2 = pi*k.k*self._T*sin(smu)/sinh(2*pi**2*n*k.k*self._T/hwc)
        return self._m/(pi*k.hbar**2)*(I1+2*(1-self._Xi)*sum((-1)**n*exp(-2*(n*pi*self._Gam)**2/(hwc)**2)*I2, axis=0))

    def nsbL(self, B = None, mu = None, T = None, Gam = None, Xi = None,
             p = None, Nmax = None, s = None, phi = 0):
        """
        Calculates the density of state analytically (for Lorenzian LL )
        """
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if T: self._T = T
        if Nmax: self._N = Nmax
        if self._s_default: self._s_default = s
        wc = k.e*B/self._m
        n = arange(1,self._Nmax+1)[:, newaxis, newaxis] # N,1 elements (N=Nmax+1)
        hwc = k.hbar*wc    
        smu = 2*pi*n*self._mu/(hwc) + phi*2*pi*n #2nd term is a Berry phase 
        skt = 2*pi**2*n*k.k*self._T/(hwc)
        Gam = self._Gam*self._B**self._p
        I1 = mu+k.k*self._T*log(1+exp(-self._mu/(k.k*T)))
        I2 = pi*k.k*self._T*sin(smu)/sinh(2*pi**2*n*k.k*self._T/hwc)
        return m/(pi*k.hbar**2)*(I1+2*(1-self._Xi)*sum((-1)**n*exp(-2*(n*pi*Gam)/(hwc))*I2, axis=0))

    def nsbC(self, B = None, mu = None, T = None, Gam = None, Xi = None, p = None,
             Nmax = None, alpha = 0, GL = 1, Bs = 2):
        """
        Calculates the density of state numerically
        """
        if mu: self._mu = mu
        if Gam: self._Gam = Gam
        if T: self._T = T
        if Nmax: self._N = Nmax
        E = linspace(0,1.1*mu,500)[:, newaxis]
        a = self.fd(E = E)*self.gESS(E = E,Bs = Bs, alpha = alpha, GL = GL)
        return sum(a, axis = 0)*(max(E)-min(E))/shape(E)[0]

    def find_nearest(self,array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return (idx,array[idx])
    

    def update_progress(self,progress):
        barLength = 10 
        status = ""
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float\r\n"
        if progress < 0:
            progress = 0
            status = "Halt...\r\n"
        if progress >= 1:
            progress = 1
            status = "Done...\r\n"
        block = int(round(barLength*progress))
        text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
        sys.stdout.write(text)
        sys.stdout.flush()

#mul = linspace(1.5e-21,3e-21,1100)[:,newaxis]
#N = nsb(B, mu = mul)

#Mat = np.zeros((1000,2))
#for i in range(1000):
#    Mat[i] = find_nearest(N[:,i],ns)
#    
#for i in range(1000):
#    mub[i] = mul[int(Mat[i,0])]
#    
#M2 = Mag(B, mu = mub)



#def MagS(B,ns = ns, phi = 0, T=T_default, Gam=Gam_default, Xi=Xi_default, m=m_default, p = p_default, Nmax=Nmax_default ):
#    wc = k.e*B/m
#    n = arange(1,Nmax+1)[:, newaxis] # N,1 elements (N=Nmax+1)
#    hwc = k.hbar*wc
#    mu = ns*pi*k.hbar**2/m_default    
#    smu = 2*pi*n*mu/(hwc) + phi*2*pi*n #2nd term is a Berry phase 
#    skt = 2*pi**2*n*k.k*T/(hwc)
#    Gam = Gam*B**p
#    I4 =  -(hwc)**2/(4*pi**2*n**2*k.k*T) + hwc/(2*n)*cos(smu)/sinh(2*pi**2*n*k.k*T/hwc)
#    DI4 =  1/B*(-hwc**2/(2*pi**2*n**2*k.k*T)+pi*mu*sin(smu)/sinh(skt)+cos(smu)/sinh(skt)*(hwc/(2*n)+pi**2*k.k*T*1/tanh(skt)))   
#    return -2*m*k.k*T/(pi*k.hbar**2)*(1-Xi)*sum((-1)**n*exp(-2*(n*pi*Gam)**2/(hwc)**2)*(DI4+(1-p)*(2*pi*n*Gam/hwc)**2*I4/B), axis=0)

# def main():
        
#     if __name__ == '__main__': main()        # -*- coding: utf-8 -*-

      