import numpy as np

# recession curve models

### REALLY SIMPLE MODELS
# fit the data
def func(x, a, b, c):
    return a * np.exp(-b * x) + c

def exponential(x, a, b):
    return a*np.exp(b*x)

def model(x,m,b):
    return m*x+b

def modelPor(t,y0,v0,a):
    return y0 + v0*t + 0.5*a*t**2

### MODELS FROM CARLOTTE AND CHAFFE 2019
# Maillet (1905) Linear relationship between storage and flow (S=kQ) -> exponential relationship
def exponentialM(t,Qo,a):
    return Qo*np.exp(-a*t)

# ^^ shifting the exponential, shifting the exponential storage by some soft of steady storage...
def exponentialMshift(t,Qo,Qf,a):
    Qdiff = Qo-Qf
    return Qdiff*np.exp(-a*t) + Qf

# Boussinesq (1904) non-linear differential frlow equation assumin a depuit-Boussinesq aquifer
def boussinesq(t,Qo,n):
    return Qo*(1+n*t)**(-2)

# ^^^ Boussinesq Shifted
def boussinesqshift(t,Qo,Qf,n):
    Qdiff = Qo-Qf
    return Qdiff*(1+n*t)**(-2) + Qf

# Coutagne(1984): dq/dt = 
def coutagne(t,Qo,a,b):
    c = 1-b
    return (Qo**c - c*a*t)**(1/c)

# ^^^^ Coutagne(1984) Shifted
def coutagneshift(t,Qo,Qf,a,b):
    c = 1-b
    Qdiff = Qo-Qf
    return (Qdiff**c - c*a*t)**(1/c) + Qf

# Wittenberg(1999) non-linear resvoir S=aQb
def wittenberg(t,Qo,a,b):
    c = 1-b
    return Qo * (1 + (c*Qo**c)/(a*b)*t)**(1/c)

# ^^^ Shifted Wittenberg
def wittenbergshift(t,Qo,Qf,a,b):
    c = 1-b
    Qdiff = Qo-Qf
    return Qdiff * (1 + (c*Qdiff**c)/(a*b)*t)**(1/c) + Qf