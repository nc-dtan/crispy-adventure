import pandas as pd

from psrm.enums.aktivitettype import AktivitetType
from psrm.enums.artkode import ArtKode
from psrm.enums.kundetype import KundeType
from psrm.enums.typekategori import TypeKategori
from psrm.enums.typekode import TypeKode
from psrm.korrektion.afregning import (Afregning, BeloebStruktur,
                                       IndbetalingOplysninger, KundeStruktur,
                                       OmfattetAfUdligningAfregning,
                                       UdligningAfregning,
                                       UdligningAfregningListe)


def convert_to_xml(s: pd.Series, fordringType: TypeKategori, fname: str=None) -> str:
    if fname is None:
            fname = 'test_sample.xml'
    
    # TODO: Fill out these fields from data from the df
    kunde = KundeStruktur('', '', '')
    indbetalingOplysninger = IndbetalingOplysninger(s.NYMFID, AktivitetType.KORREKTION,
                                                    'Korrektion på fordring', kunde)
    afregningBeloeb = BeloebStruktur('FordringAfregning', 142, 142, 'DKK')
    restBeloeb = BeloebStruktur('DMIFordringRest', 716.45, 716.45, 'DKK')
    omfattetAfUdligningAfregning = OmfattetAfUdligningAfregning(1337, 1337, 4224,
                        ArtKode.INDR, TypeKode.PSRESTS, fordringType, '2018-05-01+02:00',
                        indbetalingOplysninger, afregningBeloeb, restBeloeb)
    fordringBeloeb = BeloebStruktur('FordringHaverAfregning', 200.00, 200.00, 'DKK')
    udligningAfregning = UdligningAfregning('11', fordringBeloeb, '2018-05-01+02:00',
                        '2018-05-01+02:00',
                        '2018-05-01+02:00',
                        omfattetAfUdligningAfregning)
    udligningAfregningListe = UdligningAfregningListe(udligningAfregning)
    afregning = Afregning(udligningAfregningListe)

    # Save the xml
    print(f'Saving the XML file in {fname}\n')
    xml = afregning.to_xml(fname=fname)
    return xml


if __name__ == '__main__':
    import pandas as pd
    fname = lambda s, fordringType: f'{fordringType}-korrektion-{s}.xml'
    path = '../../../underret-report-example-Daniel-test.xlsx'
    df = pd.read_excel(path)
    for row in df.iloc[0:2].iterrows():
        s = row[1]
        if not s.UDL_HF_OK:
            fordringType = TypeKategori.HF
        else:
            fordringType = TypeKategori.IR
        xml = convert_to_xml(s, fordringType, fname=fname(s.NYMFID, fordringType.value))
