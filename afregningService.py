from udligning.afregning import Afregning
from udligning.afregning import BeloebStruktur
from udligning.afregning import IndbetalingOplysninger
from udligning.afregning import KundeStruktur
from udligning.afregning import OmfattetAfUdligningAfregning
from udligning.afregning import UdligningAfregning
from udligning.afregning import UdligningAfregningListe
from udligning.enums.aktivitettype import AktivitetType
from udligning.enums.artkode import ArtKode
from udligning.enums.kundetype import KundeType
from udligning.enums.typekategori import TypeKategori
from udligning.enums.typekode import TypeKode


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
