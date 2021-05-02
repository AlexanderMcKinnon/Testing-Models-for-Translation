import numpy as np

def transcription_or_translation(target, machinery, initiation, elongation, product, kp, km, k, kc):
    #                1p------------------,  1n------------,   2-----------,
    dtarget_dt =     -target*machinery*kp   +initiation*km    +initiation*k
    
    #                1p------------------,  1n------------,                    3-------------,
    dmachinery_dt =  -target*machinery*kp   +initiation*km                     +elongation*kc
    
    #                1p------------------,  1n------------,   2-----------,
    dinitiation_dt =  target*machinery*kp   -initiation*km    -initiation*k
    
    #                                                         2-----------,    3-------------,
    delongation_dt =                                           initiation*k    -elongation*kc
    
    #                                                                          3------------,
    dproduct_dt =                                                               elongation*kc
    return np.array([dtarget_dt, dmachinery_dt, dinitiation_dt, delongation_dt, dproduct_dt])

def mRNA_3miRNAdegradation_fullpathway( target, mi, X, R, L, Y, Nm, target_inv, k1, k2, k3, m_or_C):
    scale  = Nm /(target+target_inv + (1*10**(-50)) )
    dNm_dt, dCm_dt = 0, 0
    dtarget_dt, dmi_dt ,  dL_dt_1                     = mRNA_binding_SIMP2(target, mi, scale, k1)
    dL_dt_2   , dX_dt_1, dNm_dt, dY_dt_1            = mRNA_binding_SIMP(L, X, scale, k2)
    dY_dt_2   , dX_dt_2, dR_dt                       = mRNA_degradation_SIMP(Y, scale, k3, m_or_C)
    return np.array([dtarget_dt, dmi_dt, sum([dX_dt_1, dX_dt_2]), dR_dt, sum([dL_dt_1, dL_dt_2]), sum([dY_dt_1, dY_dt_2]), dNm_dt, dCm_dt])

def mRNA_5miRNAdegradation_fullpathway(target, mi, X, R, L, Y, Nm, K, target_inv, k1, k2, k3, m_or_C):
    scale  = Nm /(target+target_inv + (1*10**(-50)) )
    dNm_dt, dtarget_inv_dt = 0, 0
    dtarget_dt, dmi_dt , dNm_dt  , dL_dt_1, dK_dt_1 = mRNA_binding(target, mi, scale, k1)
    dL_dt_2   , dX_dt_1, dK_dt_2, dY_dt_1          = mRNA_binding_SIMP(L, X, scale, k2)
    dY_dt_2   , dX_dt_2, dR_dt                     = mRNA_degradation_SIMP(Y, scale, k3, m_or_C)
    return np.array([dtarget_dt, dmi_dt, sum([dX_dt_1, dX_dt_2]), dR_dt, sum([dL_dt_1, dL_dt_2]), sum([dY_dt_1, dY_dt_2]), dNm_dt, sum([dK_dt_1, dK_dt_2]), dtarget_inv_dt])


######### Full mRNA production and normaldegradation pathway
def production_full_pathway( D, Cd, Nd, m, Cm, Nm, Ym, YC, P, Pol, R, X, km_p, km_m, km, km_c, kd_p, kd_m, kd, kd_c, kX_m, kdeg, lam_P):
    gamma  = Nm /(Cm+m + (1*10**(-50)) )
    # Transcription
    dD_dt  , dPol_dt, dCd_dt  , dNd_dt  , dm_dt_1 = transcription_or_translation(D, Pol, Cd, Nd, m, kd_p, kd_m, kd, kd_c)
    # Translation
    dm_dt_2, dR_dt_1, dCm_dt_1, dNm_dt_1, dP_dt_1 = transcription_or_translation(m, R, Cm, Nm, P, km_p, km_m, km, km_c)
    # Free mRNA normaldegradation
    dm_dt_3 , dYm_dt, dX_dt_1, dR_dt_2, dNm_dt_2 = mRNA_selfdegradation_fullpathway_SIMP(m , X, Ym, gamma, kX_m, kdeg, 0)
    # Initating mRNA normaldegradation
    dCm_dt_2, dYC_dt, dX_dt_2, dR_dt_3, dNm_dt_3 = mRNA_selfdegradation_fullpathway_SIMP(Cm, X, YC, gamma, kX_m, kdeg, 1)
    # Protein Dilution
    dP_dt_2 = -lam_P*P
    return np.array([dD_dt, dCd_dt, dNd_dt, sum([dm_dt_1, dm_dt_2, dm_dt_3]), sum([dCm_dt_1, dCm_dt_2]), sum([dNm_dt_1, dNm_dt_2, dNm_dt_3]), dYm_dt, dYC_dt, sum([dP_dt_1, dP_dt_2]), dPol_dt, sum([dR_dt_1, dR_dt_2, dR_dt_3]), sum([dX_dt_1, dX_dt_2])])

def production_mRNA_pathway(D, Cd, Nd, m, Pol, R, X, kd_p, kd_m, kd, kd_c, lam_mi):
    # Transcription
    dD_dt  , dPol_dt, dCd_dt  , dNd_dt  , dm_dt_1 = transcription_or_translation(D, Pol, Cd, Nd, m, kd_p, kd_m, kd, kd_c)
    
    dm_dt_2 = -m*lam_mi
    return np.array([dD_dt, dCd_dt, dNd_dt, sum([dm_dt_1, dm_dt_2]), dPol_dt])

def mRNA_selfdegradation_fullpathway_SIMP(target, X, Y, scale, k1, k2, m_or_C):    
    dtarget_dt, dX_dt_1,   dN_dt, dY_dt_1 = mRNA_binding_SIMP(target, X, scale, k1)
    dY_dt_2   , dX_dt_2,   dR_dt          = mRNA_degradation_SIMP(Y, scale, k2, m_or_C)
    return np.array([dtarget_dt, sum([dY_dt_1, dY_dt_2]), sum([dX_dt_1, dX_dt_2]), dR_dt, dN_dt])

######### General mRNA binding function
## target + binder + {scale*elongating_Ribosomes} ->[k] product + {scale*blocked_Ribosomes}
def mRNA_binding(target, binder, scale, k):
    dtarget_dt =                         -target*binder*k
    dbinder_dt =                         -target*binder*k
    delongating_Ribosomes_dt =     -scale*target*binder*k
    dproduct_dt =                                                target*binder*k
    dblocked_Ribosomes_dt =                                scale*target*binder*k
    return np.array([dtarget_dt, dbinder_dt, delongating_Ribosomes_dt, dproduct_dt, dblocked_Ribosomes_dt])
## target + binder + {scale*elongating_Ribosomes} ->[k] product
def mRNA_binding_SIMP(target, binder, scale, k):
    dtarget_dt =                         -target*binder*k
    dbinder_dt =                         -target*binder*k
    delongating_Ribosomes_dt =     -scale*target*binder*k
    dproduct_dt =                                                target*binder*k
    return np.array([dtarget_dt, dbinder_dt, delongating_Ribosomes_dt, dproduct_dt])
## target + binder ->[k] product
def mRNA_binding_SIMP2(target, binder, scale, k):
    dtarget_dt =                         -target*binder*k
    dbinder_dt =                         -target*binder*k
    dproduct_dt =                                                target*binder*k
    return np.array([dtarget_dt, dbinder_dt, dproduct_dt])


######### General mRNA degradation
## Y + {scale*blocked_Ribosomes}->[k] X + scale*Ribosomes
def mRNA_degradation(Y, scale, k, m_or_C):
    dY_dt =                                -Y*k
    dblocked_Ribosomes_dt =          -scale*Y*k
    dX_dt =                                 Y*k
    dRibosomes_dt =          (scale+m_or_C)*Y*k
    return np.array([dY_dt, dblocked_Ribosomes_dt, dX_dt, dRibosomes_dt])

def mRNA_degradation_SIMP(Y, scale, k, m_or_C):
    dY_dt =                                -Y*k
    dX_dt =                                 Y*k
    dRibosomes_dt =          (scale+m_or_C)*Y*k
    return np.array([dY_dt, dX_dt, dRibosomes_dt])