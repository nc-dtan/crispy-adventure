from psrm.korrektion.afregning import Afregning
from psrm.korrektion.afregning import BeloebStruktur
from psrm.korrektion.afregning import IndbetalingOplysninger
from psrm.korrektion.afregning import KundeStruktur
from psrm.korrektion.afregning import OmfattetAfUdligningAfregning
from psrm.korrektion.afregning import UdligningAfregning
from psrm.korrektion.afregning import UdligningAfregningListe
from psrm.enums.aktivitettype import AktivitetType
from psrm.enums.artkode import ArtKode
from psrm.enums.kundetype import KundeType
from psrm.enums.typekategori import TypeKategori
from psrm.enums.typekode import TypeKode


def convert_to_xml(df, fname=None):
    if fname is None:
            fname = 'test_sample.xml'
    
    # TODO: Fill out these fields from data from the df
    kunde = KundeStruktur('0505784618', KundeType.CPR, 'SKAT Test person 9961')
    indbetalingOplysninger = IndbetalingOplysninger(938953219519, AktivitetType.DAEKNING, 'Some text', kunde)
    afregningBeloeb = BeloebStruktur('FordringAfregning', 142, 142, 'DKK')
    restBeloeb = BeloebStruktur('DMIFordringRest', 716.45, 716.45, 'DKK')
    omfattetAfUdligningAfregning = OmfattetAfUdligningAfregning(1337, 1337, 4224,
                        ArtKode.INDR, TypeKode.PSRESTS, TypeKategori.HF, '2018-05-01+02:00',
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
    xml = convert_to_xml(None, fname='tralala.xml')
    print(xml)
