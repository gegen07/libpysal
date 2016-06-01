import numpy as np
import numpy.linalg as la
import families


def _compute_betas(y, x):
    """
    compute MLE coefficients using iwls routine

    Methods: p189, Iteratively (Re)weighted Least Squares (IWLS),
    Fotheringham, A. S., Brunsdon, C., & Charlton, M. (2002).
    Geographically weighted regression: the analysis of spatially varying relationships.
    """
    xT = x.T
    xtx = np.dot(xT, x)
    xtx_inv = la.inv(xtx)
    xtx_inv_xt = np.dot(xtx_inv, xT)
    betas = np.dot(xtx_inv_xt, y)
    return betas

def _compute_betas_gwr(y, x, wi):
    """
    compute MLE coefficients using iwls routine

    Methods: p189, Iteratively (Re)weighted Least Squares (IWLS),
    Fotheringham, A. S., Brunsdon, C., & Charlton, M. (2002).
    Geographically weighted regression: the analysis of spatially varying relationships.
    """
    xT = np.dot(x.T, wi)
    xtx = np.dot(xT, x)
    xtx_inv = la.inv(xtx)
    xtx_inv_xt = np.dot(xtx_inv, xT)
    betas = np.dot(xtx_inv_xt, y)
    return betas, xtx_inv_xt

def iwls(y, x, family, offset, y_fix,
    ini_betas=None, tol=1.0e-6, max_iter=200, wi=None):
    """
    Iteratively re-weighted least squares estimation routine

    """
    diff = 1.0e6
    n_iter = 0
    link_y = family.link(y)

    if isinstance(family, families.Binomial):
        link_y = family.link._clean(link_y)
    if ini_betas is None:
        betas = _compute_betas(link_y, x)
    else:
        betas = ini_betas
    v = np.dot(x, betas)
   
    while diff > tol and n_iter < max_iter:
        n_iter += 1
       
        mu = family.link.inverse(v)
        w = family.weights(mu)
        z = v + (family.link.deriv(mu)*(y-mu))
        w = np.sqrt(w)
        wx = x * w
        wz = z * w
        if wi is None:
            n_betas = _compute_betas(wz, wx)
        else:
            n_betas, xtx_inv_xt = _compute_betas_gwr(wz, wx, wi)
        v_new = np.dot(x, n_betas)
	    #if family == 'Gaussian':
            #diff = 0.0
	        #v = v_new
	    #else
        
        diff = min(abs(n_betas-betas))
        v = v_new
        betas = n_betas
    
    y_hat = family.fitted(v)

    if wi is None:
        return betas, y_hat, w, n_iter
    else:
        return betas, y_hat, n_iter, xtx_inv_xt
