import psrm_ci_ft_base as psrm


def id_check(a,  nymfid):
    af, un, ud = a.get_by_id(nymfid)
    print(af)
    print('\n')
    print(un)
    print('\n')
    print(ud)
    print('\n')
    print('Sum of AFR: %.2f' % af.sum_amount)
    print('Sum of UND: %.2f' % un.sum_amount)
    print('Sum of UDT: %.2f' % ud.sum_amount)
    
a = psrm.PSRM_CI_FT_BASE(path='../Data')

