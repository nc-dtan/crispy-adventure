from lxml import etree
from dicttoxml import dicttoxml

from .enums.artkode import ArtKode
from .enums.typekategori import TypeKategori
from .enums.typekode import TypeKode
from .enums.aktivitettype import AktivitetType
from .enums.kundetype import KundeType


class Afregning:
    def __init__(self, udligningAfregningListe=None):
        self.udligningAfregningListe = udligningAfregningListe

    @property
    def __dict__(self):
        return {'UdligningAfregningListe': self.udligningAfregningListe.__dict__}

    def to_xml(self, fname=None) -> str:
        if fname is None:
            fname = 'test_sample.xml'
        xml = dicttoxml(self.__dict__, root=False, attr_type=False)

        root = etree.fromstring(xml.decode())
        xml_pretty = etree.tostring(root, pretty_print=True).decode()
        with open(fname, 'w') as f:
            f.write(xml_pretty)
        return xml_pretty


class UdligningAfregningListe:
    def __init__(self, udligningAfregning=None):
        self.udligningAfregning = udligningAfregning

    @property
    def __dict__(self):
        return {'UdligningAfregning': self.udligningAfregning.__dict__}


class UdligningAfregning:
    def __init__(self, afregningId=None,
                       afregningBeloebStruktur=None,
                       afregningDato=None,
                       afregningPerFra=None,
                       afregningPerTil=None,
                       fordringListe=None):
        self.afregningId = afregningId
        self.afregningBeloebStruktur = afregningBeloebStruktur
        self.afregningDato = afregningDato
        self.afregningPerFra = afregningPerFra
        self.afregningPerTil = afregningPerTil
        self.fordringListe = fordringListe

    @property
    def __dict__(self):
        return {'FordringHaverAfregningID': self.afregningId,
                'FordringHaverAfregningBeloebStruktur': self.afregningBeloebStruktur.__dict__,
                'FordringHaverAfregningDato': self.afregningDato,
                'FordringHaverAfregningPerFra': self.afregningPerFra,
                'FordringHaverAfregningPerTil': self.afregningPerTil,
                'FordringHaverFordringListe': self.fordringListe.__dict__}


class BeloebStruktur:
    def __init__(self, name=None, amount=None, amountDKK=None, currency=None):
        self.name = name
        self.amount = amount
        self.amountDKK = amountDKK
        self.currency = currency

    @property
    def __dict__(self):
        return {f'{self.name}Beloeb': self.amount,
                f'{self.name}BeloebDKK': self.amountDKK,
                'ValutaKode': self.currency}


class OmfattetAfUdligningAfregning:
    def __init__(self, efiFordringID=None, efiHFFordringID=None,
                       fordringhaverRef=None, fordringArtKode=None,
                       typeKode=None, typeKategori=None,
                       virkningsDato=None,
                       indbetalingOplysninger=None,
                       afregningBeloebStruktur=None,
                       restBeloebStruktur=None):
        self.efiFordringID = efiHFFordringID
        self.efiHFFordringID = efiHFFordringID
        self.fordringhaverRef = fordringhaverRef
        self.fordringArtKode = fordringArtKode.value
        self.typeKode = typeKode.value
        self.typeKategori = typeKategori.value
        self.virkningsDato = virkningsDato
        self.indbetalingOplysninger = indbetalingOplysninger
        self.afregningBeloebStruktur = afregningBeloebStruktur
        self.restBeloebStruktur = restBeloebStruktur

    @property
    def __dict__(self):
        return {'FordringerOmfattetAfUdligningenAfregningen':
                    {'DMIFordringEFIFordringID': self.efiFordringID,
                      'DMIFordringEFIHovedFordringID': self.efiHFFordringID,
                      'DMIFordringFordringHaverRef': self.fordringhaverRef,
                      'DMIFordringFordringArtKode': self.fordringArtKode,
                      'DMIFordringTypeKode': self.typeKode,
                      'DMIFordringTypeKategori': self.typeKategori,
                      'DMITransaktionVirkningDato': self.virkningsDato,
                      'SupplerendeIndbetalingOplysninger': self.indbetalingOplysninger.__dict__,
                      'FordringAfregningBeloebStruktur': self.afregningBeloebStruktur.__dict__,
                      'FordringRestBeloebStruktur': self.restBeloebStruktur.__dict__}
                }


class IndbetalingOplysninger:
    def __init__(self, indbetalingID=None,
                       aktivitetType=None,
                       aktivitetTekst=None,
                       kundeStruktur=None):
        self.indbetalingID = indbetalingID
        self.aktivitetType = aktivitetType.value
        self.aktivitetTekst = aktivitetTekst
        self.kundeStruktur = kundeStruktur

    @property
    def __dict__(self):
        return {'DMIIndbetalingID': self.indbetalingID,
                'DMIIndbetalingAktivitetType': self.aktivitetType,
                'DMIIndbetalingAktivitetTekst': self.aktivitetTekst,
                'KundeStruktur': self.kundeStruktur.__dict__}


class KundeStruktur:
    def __init__(self, kundeNummer=None, kundeType=None, navn=None):
        self.KundeNummer = kundeNummer
        self.KundeType = kundeType.value
        self.KundeNavn = navn
