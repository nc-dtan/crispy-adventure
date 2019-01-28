import pytest
from psrm.enums.aktivitettype import AktivitetType
from psrm.enums.artkode import ArtKode
from psrm.enums.fordringshaver import FordringsHaver
from psrm.enums.justeringstype import JusteringsType
from psrm.enums.kundetype import KundeType
from psrm.enums.typekategori import TypeKategori
from psrm.enums.typekode import TypeKode


def test_aktivitetsType():
    assert AktivitetType.DAEKNING.value == 'DÆKNING'
    with pytest.raises(AttributeError):
        AktivitetType.ERROR


def test_artKode():
    assert ArtKode.INDR.value == 'INDR'
    assert ArtKode.MODR.value == 'MODR'
    with pytest.raises(AttributeError):
        ArtKode.ERROR


def test_fordringshaver():
    dr = FordringsHaver.DR
    assert isinstance(dr.value, dict)
    assert len(dr.value.keys()) == 2
    assert dr.value.get('Name') == 'DR'
    assert dr.value.get('Claimant_ID') == 1229
    with pytest.raises(AttributeError):
        FordringsHaver.ERROR


def test_justeringsType():
    assert JusteringsType.DKHFEX.value == 'DKHFEX'
    assert JusteringsType.DKOGEX.value == 'DKOGEX'
    assert JusteringsType.DKOREX.value == 'DKOREX'
    assert JusteringsType.DKIGEX.value == 'DKIGEX'
    assert JusteringsType.DKCSHACT.value == 'DKCSHACT'
    with pytest.raises(AttributeError):
        JusteringsType.ERROR


def test_kundeType():
    assert KundeType.CPR.value == 'CPR'
    assert KundeType.CVR.value == 'CVR'
    assert KundeType.SE.value == 'SE'
    with pytest.raises(AttributeError):
        KundeType.ERROR


def test_typeKategori():
    assert TypeKategori.HF.value == 'HF'
    assert TypeKategori.IR.value == 'IR'
    with pytest.raises(AttributeError):
        TypeKategori.ERROR


def test_typeKode():
    assert TypeKode.PSARBMB.value == 'PSARBMB'
    assert TypeKode.PSBSKAT.value == 'PSBSKAT'
    assert TypeKode.PSRESTS.value == 'PSRESTS'
    assert TypeKode.LIMEDIE.value == 'LIMEDIE'
    assert TypeKode.POBØDPO.value == 'POBØDPO'
    assert TypeKode.GEOPKRÆ.value == 'GEOPKRÆ'
    assert TypeKode.REINDGI.value == 'REINDGI'
    assert TypeKode.UHFORSK.value == 'UHFORSK'
    assert TypeKode.UHÆGTEF.value == 'UHÆGTEF'
    assert TypeKode.REOPKRÆ.value == 'REOPKRÆ'
    assert TypeKode.PSBSKRE.value == 'PSBSKRE'
    assert TypeKode.VSMOMSE.value == 'VSMOMSE'
    assert TypeKode.PACHOKO.value == 'PACHOKO'
    assert TypeKode.KFDAGIN.value == 'KFDAGIN'
    assert TypeKode.DFDOBBE.value == 'DFDOBBE'
    assert TypeKode.OPREGU.value == 'OPREGU'
    assert TypeKode.VSARBMB.value == 'VSARBMB'
    assert TypeKode.REINDDR.value == 'REINDDR'
    with pytest.raises(AttributeError):
        TypeKode.ERROR