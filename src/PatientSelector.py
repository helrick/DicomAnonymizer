'''
Defines functions to sort through a given folder
and create Patient objects when dicom file with new
patient name encountered. Sends dicom files with
pre-exisiting patients to their respective Patient object
Stores a library of Patients for display to windows
'''

import dicom
import os
import magic


class PatientLibrary():

    '''
    Initializes a patient library with a
    path to the folder to be anonymized
    '''
    def __init__(self, folderPath):

        self.sourceDir = folderPath
        #store Patient objects in dict
        self.PatientObjects = {}


        # dict for how to anonymize tags, # indicated remove tag altogether
        '''
        self.tagsAnon = {'AccessionNumber': '00000000',
                         'PatientID': '100000',
                         'PatientAddress': 'Unknown',
                         'StudyID': '00000000',
                         'PerformedProcedureStepID': '#',
                         'ScheduledProcedureStepID': '#',
                         'RequestAttributesSequence': '#'}
        '''

        self.tagsAnon = {(0x0008, 0x0050): '00000000',
                         (0x0018, 0x4000): '#',
                         (0x0010, 0x21B0): '#',
                         (0x0010, 0x1000): '#',
                         (0x0010, 0x1001): '#',
                         (0x0010, 0x1005): '#',
                         (0x0010, 0x1060): '#',
                         (0x0010, 0x2154): '#',
                         (0x0038, 0x0300): '#',
                         (0x0038, 0x0400): '#',
                         (0x0040, 0xA123): '#',
                         (0x0008, 0x009D): '#',
                         (0x0008, 0x0092): '#',
                         (0x0008, 0x0094): '#',
                         (0x0010, 0x0020): '100000',
                         (0x0010, 0x1040): 'Anonymized',
                         (0x0020, 0x0010): '00000000',
                         (0x0040, 0x0253) : '#',
                         (0x0040, 0x0009) : '#',
                         (0x0040, 0x0275) : '#',
                         (0x0010, 0x0030) : '00000101',
                         (0x0040, 0x0244) : '#',
                         (0x0040, 0x0245) : '#',
                         (0x0020, 0x000E) : '00000000',
                         (0x0040, 0x2017): '0'
                         }

        '''Tags according to DICOM standard:
        
        self.tagsAnon = {
                            (0x0008, 0x0050) : '00000000',
                            (0x0018, 0x4000) : '#',
                            (0x0040, 0x0555) : '#',
                            (0x0008, 0x0022) : '00000000',
                            (0x0008, 0x002A) : '#',
                            (0x0018, 0x1400) : '#',
                            (0x0018, 0x9424) : '#',
                            (0x0008, 0x0032) : '#',
                            (0x0040, 0x4035) : '#',
                            (0x0010, 0x21B0) : '#',
                            (0x0040, 0xA353) : '#',
                            (0x0038, 0x0010) : '#',
                            (0x0038, 0x0020) : '#',
                            (0x0008, 0x1084) : '#',
                            (0x0008, 0x1080) : '#',
                            (0x0038, 0x0021) : '#',
                            (0x0000, 0x1000) : '#',
                            (0x0010, 0x2110) : '#',
                            (0x4000, 0x0010) : '#',
                            (0x0040, 0xA078) : '#',
                            (0x0010, 0x1081) : '#',
                            (0x0018, 0x1007) : '#',
                            (0x0040, 0x0280) : '#',
                            (0x0020, 0x9161) : '00000000',
                            (0x0040, 0x3001) : '#',
                            (0x0008, 0x009D) : '#',
                            (0x0008, 0x009C) : 'Anonymized',
                            (0x0070, 0x0084) : 'Anonymized',
                            (0x0070, 0x0086) : '00000000',
                            (0x0008, 0x0023) : '00000101',
                            (0x0040, 0xA730) : '#',
                            (0x0008, 0x0033) : '000000.000000',
                            (0x0018, 0x0010) : 'UNKNOWN',
                            (0x0018, 0xA003) : '#',
                            (0x0010, 0x2150) : '#',
                            (0x0040, 0xA307) : '#',
                            (0x0038, 0x0300) : '#',
                            (0x0008, 0x0025) : '#',
                            (0x0008, 0x0035) : '#',
                            (0x0040, 0xA07C) : '#',
                            (0xFFFC, 0xFFFC) : '#',
                            (0x0008, 0x2111) : '#',
                            (0x0018, 0x700A) : '00000000',
                            (0x0018, 0x1000) : '00000000',
                            (0x0018, 0x1002) : '#',
                            (0x0400, 0x0100) : '#',
                            (0xFFFA, 0xFFFA) : '#',
                            (0x0038, 0x0040) : '#',
                            (0x4008, 0x011A) : '#',
                            (0x4008, 0x0119) : '#',
                            (0x0018, 0x9517) : '#',
                            (0x0010, 0x2160) : '#',
                            (0x0040, 0x4011) : '#',
                            (0x0040, 0x2017) : '0',
                            (0x0020, 0x9158) : '#',
                            (0x0018, 0x1008) : '#',
                            (0x0018, 0x1005) : '#',
                            (0x0040, 0x4037) : '#',
                            (0x0040, 0x4036) : '#',
                            (0x0088, 0x0200) : '#',
                            (0x0008, 0x4000) : '#',
                            (0x0020, 0x4000) : '#',
                            (0x0028, 0x4000) : '#',
                            (0x0040, 0x2400) : '#',
                            (0x4008, 0x0300) : '#',
                            (0x0008, 0x0015) : '00000000',
                            (0x0008, 0x0014) : '#',
                            (0x0008, 0x0081) : '#',
                            (0x0008, 0x0082) : '00001',
                            (0x0008, 0x0080) : 'Anonymized',
                            (0x0008, 0x1040) : '#',
                            (0x0010, 0x1050) : '#',
                            (0x0040, 0x1011) : '#',
                            (0x4008, 0x0111) : '#',
                            (0x4008, 0x010C) : '#',
                            (0x4008, 0x0115) : '#',
                            (0x4008, 0x0202) : '#',
                            (0x4008, 0x0102) : '#',
                            (0x4008, 0x010B) : '#',
                            (0x4008, 0x010A) : '#',
                            (0x0008, 0x3010) : '00000000',
                            (0x0038, 0x0011) : '#',
                            (0x0010, 0x0021) : '#',
                            (0x0038, 0x0061) : '#',
                            (0x0028, 0x1214) : '00000000',
                            (0x0010, 0x21D0) : '#',
                            (0x0400, 0x0404) : '#',
                            (0x0002, 0x0003) : '00000000',
                            (0x0010, 0x2000) : '#',
                            (0x0010, 0x1090) : '#',
                            (0x0010, 0x1080) : '#',
                            (0x0400, 0x0550) : '#',
                            (0x0020, 0x3406) : '#',
                            (0x0020, 0x3401) : '#',
                            (0x0008, 0x1060) : '#',
                            (0x0040, 0x1010) : '#',
                            (0x0040, 0xA192) : '#',
                            (0x0040, 0xA402) : '00000000',
                            (0x0040, 0xA193) : '#',
                            (0x0040, 0xA171) : '00000000',
                            (0x0010, 0x2180) : '#',
                            (0x0008, 0x1072) : '#',
                            (0x0008, 0x1070) : '#',
                            (0x0400, 0x0561) : '#',
                            (0x0040, 0x2010) : '#',
                            (0x0040, 0x2011) : '#',
                            (0x0040, 0x2008) : '#',
                            (0x0040, 0x2009) : '#',
                            (0x0010, 0x1000) : '#',
                            (0x0010, 0x1002) : '#',
                            (0x0010, 0x1001) : '#',
                            (0x0008, 0x0024) : '#',
                            (0x0008, 0x0034) : '#',
                            (0x0028, 0x1199) : '00000000',
                            (0x0040, 0xA07A) : '#',
                            (0x0010, 0x1040) : '#',
                            (0x0010, 0x4000) : '#',
                            (0x0010, 0x0020) : '00000000',
                            (0x0010, 0x2203) : '#',
                            (0x0038, 0x0500) : '#',
                            (0x0040, 0x1004) : '#',
                            (0x0010, 0x1010) : '#',
                            (0x0010, 0x0030) : '00000101',
                            (0x0010, 0x1005) : '#',
                            (0x0010, 0x0032) : '#',
                            (0x0038, 0x0400) : '#',
                            (0x0010, 0x0050) : '#',
                            (0x0010, 0x1060) : '#',
                            (0x0010, 0x0101) : '#',
                            (0x0010, 0x0102) : '#',
                            (0x0010, 0x21F0) : '#',
                            (0x0010, 0x0040) : 'X',
                            (0x0010, 0x1020) : '#',
                            (0x0010, 0x2155) : '#',
                            (0x0010, 0x2154) : '#',
                            (0x0010, 0x1030) : '#',
                            (0x0040, 0x0243) : '#',
                            (0x0040, 0x0254) : '#',
                            (0x0040, 0x0250) : '#',
                            (0x0040, 0x4051) : '#',
                            (0x0040, 0x0251) : '#',
                            (0x0040, 0x0253) : '#',
                            (0x0040, 0x0244) : '#',
                            (0x0040, 0x4050) : '#',
                            (0x0040, 0x0245) : '#',
                            (0x0040, 0x0241) : '#',
                            (0x0040, 0x4030) : '#',
                            (0x0040, 0x0242) : '#',
                            (0x0040, 0x4028) : '#',
                            (0x0008, 0x1052) : '#',
                            (0x0008, 0x1050) : '#',
                            (0x0040, 0x1102) : '#',
                            (0x0040, 0x1101) : '#',
                            (0x0040, 0xA123) : '#',
                            (0x0040, 0x1104) : '#',
                            (0x0040, 0x1103) : '#',
                            (0x4008, 0x0114) : '#',
                            (0x0008, 0x1062) : '#',
                            (0x0008, 0x1048) : '#',
                            (0x0008, 0x1049) : '#',
                            (0x0040, 0x2016) : '00000000',
                            (0x0018, 0x1004) : '#',
                            (0x0040, 0x0012) : '#',
                            (0x0010, 0x21C0) : '#',
                            (0x0070, 0x1101) : '00000000',
                            (0x0070, 0x1102) : '00000000',
                            (0x0040, 0x4052) : '#',
                            (0x0018, 0x1030) : '#',
                            (0x300C, 0x0113) : '#',
                            (0x0040, 0x2001) : '#',
                            (0x0032, 0x1030) : '#',
                            (0x0400, 0x0402) : '#',
                            (0x0008, 0x1140) : '#',
                            (0x0040, 0xA172) : '00000000',
                            (0x0038, 0x0004) : '#',
                            (0x0010, 0x1100) : '#',
                            (0x0008, 0x1120) : '#',
                            (0x0008, 0x1111) : '#',
                            (0x0400, 0x0403) : '#',
                            (0x0008, 0x1155) : '00000000',
                            (0x0004, 0x1511) : '00000000',
                            (0x0008, 0x1110) : '#',
                            (0x0008, 0x0092) : '#',
                            (0x0008, 0x0096) : '#',
                            (0x0008, 0x0090) : 'Anonymized',
                            (0x0008, 0x0094) : '#',
                            (0x0010, 0x2152) : '#',
                            (0x0040, 0x0275) : '#',
                            (0x0032, 0x1070) : '#',
                            (0x0040, 0x1400) : '#',
                            (0x0032, 0x1060) : '#',
                            (0x0040, 0x1001) : '#',
                            (0x0040, 0x1005) : '#',
                            (0x0000, 0x1001) : '#',
                            (0x0032, 0x1032) : '#',
                            (0x0032, 0x1033) : '#',
                            (0x0010, 0x2299) : '#',
                            (0x0010, 0x2297) : '#',
                            (0x4008, 0x4000) : '#',
                            (0x4008, 0x0118) : '#',
                            (0x4008, 0x0042) : '#',
                            (0x300E, 0x0008) : '#',
                            (0x0040, 0x4034) : '#',
                            (0x0038, 0x001E) : '#',
                            (0x0040, 0x000B) : '#',
                            (0x0040, 0x0006) : '#',
                            (0x0040, 0x0004) : '#',
                            (0x0040, 0x0005) : '#',
                            (0x0040, 0x0007) : '#',
                            (0x0040, 0x0011) : '#',
                            (0x0040, 0x4010) : '#',
                            (0x0040, 0x0002) : '#',
                            (0x0040, 0x4005) : '#',
                            (0x0040, 0x0003) : '#',
                            (0x0040, 0x0001) : '#',
                            (0x0040, 0x4027) : '#',
                            (0x0040, 0x0010) : '#',
                            (0x0040, 0x4025) : '#',
                            (0x0032, 0x1020) : '#',
                            (0x0032, 0x1021) : '#',
                            (0x0008, 0x0021) : '#',
                            (0x0008, 0x103E) : '#',
                            (0x0020, 0x000E) : '#',
                            (0x0008, 0x0031) : '#',
                            (0x0038, 0x0062) : '#',
                            (0x0038, 0x0060) : '#',
                            (0x0010, 0x21A0) : '#',
                            (0x0008, 0x0018) : '#',
                            (0x0008, 0x2112) : '#',
                            (0x3008, 0x0105) : '#',
                            (0x0038, 0x0050) : '#',
                            (0x0018, 0x9516) : '#',
                            (0x0008, 0x1010) : '#',
                            (0x0088, 0x0140) : '#',
                            (0x0032, 0x4000) : '#',
                            (0x0008, 0x0020) : '00000101',
                            (0x0008, 0x1030) : '#',
                            (0x0020, 0x0010) : '00000000',
                            (0x0032, 0x0012) : '#',
                            (0x0020, 0x000D) : '00000000',
                            (0x0008, 0x0030) : '#',
                            (0x0040, 0xA354) : '#',
                            (0x0040, 0xDB0D) : '#',
                            (0x0040, 0xDB0C) : '#',
                            (0x4000, 0x4000) : '#',
                            (0x2030, 0x0020) : '#',
                            (0x0008, 0x0201) : '#',
                            (0x0088, 0x0910) : '#',
                            (0x0088, 0x0912) : '#',
                            (0x0088, 0x0906) : '#',
                            (0x0088, 0x0904) : '#',
                            (0x0062, 0x0021) : '00000000',
                            (0x0008, 0x1195) : '00000000',
                            (0x0040, 0xA124) : '00000000',
                            (0x0040, 0xA352) : '#',
                            (0x0040, 0xA358) : '#',
                            (0x0040, 0xA088) : '00000000',
                            (0x0040, 0xA075) : 'Anonymized',
                            (0x0040, 0xA027) : '#',
                            (0x0038, 0x4000) : '#'}
        '''

        self.tagsAnon_nums = ['(0008, 0050)', '(0018, 4000)', '(0010, 21B0)', '(0010, 1000)', '(0010, 1001)',
                              '(0010, 1005)', '(0010, 1060)', '(0010, 2154)', '(0038, 0300)', '(0038, 0400)',
                              '(0040, a123)', '(0008, 009D)', '(0008, 0092)', '(0008, 0094)', '(0010, 0020)',
                              '(0010, 1040)', '(0020, 0010)', '(0040, 0253)', '(0040, 0009)', '(0040, 0275)',
                              '(0010, 0030)', '(0020, 000e)', '(0040, 2017)']



        '''Anonymized Tags According to DICOM Standard
        
        self.tagsAnon_nums = ['(0008, 0050)', '(0018, 4000)', '(0040, 0555)', '(0008, 0022)', '(0008, 002A)', '(0018, 1400)',
                              '(0018, 9424)', '(0008, 0032)', '(0040, 4035)', '(0010, 21B0)', '(0040, A353)', '(0038, 0010)',
                              '(0038, 0020)', '(0008, 1084)', '(0008, 1080)', '(0038, 0021)', '(0000, 1000)', '(0010, 2110)',
                              '(4000, 0010)', '(0040, A078)', '(0010, 1081)', '(0018, 1007)', '(0040, 0280)', '(0020, 9161)',
                              '(0040, 3001)', '(0008, 009D)', '(0008, 009C)', '(0070, 0084)', '(0070, 0086)', '(0008, 0023)',
                              '(0040, A730)', '(0008, 0033)', '(0018, 0010)', '(0018, A003)', '(0010, 2150)', '(0040, A307)',
                              '(0038, 0300)', '(50xx, xxxx)', '(0008, 0025)', '(0008, 0035)', '(0040, A07C)', '(FFFC, FFFC)',
                              '(0008, 2111)', '(0018, 700A)', '(0018, 1000)', '(0018, 1002)', '(0400, 0100)', '(FFFA, FFFA)',
                              '(0020, 9164)', '(0038, 0040)', '(4008, 011A)', '(4008, 0119)', '(300A, 0013)', '(0018, 9517)',
                              '(0010, 2160)', '(0040, 4011)', '(0008, 0058)', '(0070, 031A)', '(0040, 2017)', '(0020, 9158)',
                              '(0020, 0052)', '(0018, 1008)', '(0018, 1005)', '(0070, 0001)', '(0040, 4037)', '(0040, 4036)',
                              '(0088, 0200)', '(0008, 4000)', '(0020, 4000)', '(0028, 4000)', '(0040, 2400)', '(4008, 0300)',
                              '(0008, 0015)', '(0008, 0014)', '(0008, 0081)', '(0008, 0082)', '(0008, 0080)', '(0008, 1040)',
                              '(0010, 1050)', '(0040, 1011)', '(4008, 0111)', '(4008, 010C)', '(4008, 0115)', '(4008, 0202)',
                              '(4008, 0102)', '(4008, 010B)', '(4008, 010A)', '(0008, 3010)', '(0038, 0011)', '(0010, 0021)',
                              '(0038, 0061)', '(0028, 1214)', '(0010, 21D0)', '(0400, 0404)', '(0002, 0003)', '(0010, 2000)',
                              '(0010, 1090)', '(0010, 1080)', '(0400, 0550)', '(0020, 3406)', '(0020, 3401)', '(0008, 1060)',
                              '(0040, 1010)', '(0040, A192)', '(0040, A402)', '(0040, A193)', '(0040, A171)', '(0010, 2180)',
                              '(0008, 1072)', '(0008, 1070)', '(0400, 0561)', '(0040, 2010)', '(0040, 2011)', '(0040, 2008)',
                              '(0040, 2009)', '(0010, 1000)', '(0010, 1002)', '(0010, 1001)', '(60xx, 4000)', '(60xx, 3000)',
                              '(0008, 0024)', '(0008, 0034)', '(0028, 1199)', '(0040, A07A)', '(0010, 1040)', '(0010, 4000)',
                              '(0010, 0020)', '(0010, 2203)', '(0038, 0500)', '(0040, 1004)', '(0010, 1010)', '(0010, 0030)',
                              '(0010, 1005)', '(0010, 0032)', '(0038, 0400)', '(0010, 0050)', '(0010, 1060)', '(0010, 0010)',
                              '(0010, 0101)', '(0010, 0102)', '(0010, 21F0)', '(0010, 0040)', '(0010, 1020)', '(0010, 2155)',
                              '(0010, 2154)', '(0010, 1030)', '(0040, 0243)', '(0040, 0254)', '(0040, 0250)', '(0040, 4051)',
                              '(0040, 0251)', '(0040, 0253)', '(0040, 0244)', '(0040, 4050)', '(0040, 0245)', '(0040, 0241)',
                              '(0040, 4030)', '(0040, 0242)', '(0040, 4028)', '(0008, 1052)', '(0008, 1050)', '(0040, 1102)',
                              '(0040, 1101)', '(0040, A123)', '(0040, 1104)', '(0040, 1103)', '(4008, 0114)', '(0008, 1062)',
                              '(0008, 1048)', '(0008, 1049)', '(0040, 2016)', '(0018, 1004)', '(0040, 0012)', '(0010, 21C0)',
                              '(0070, 1101)', '(0070, 1102)', '(0040, 4052)', '(0018, 1030)', '(300C, 0113)', '(0040, 2001)',
                              '(0032, 1030)', '(0400, 0402)', '(3006, 0024)', '(0040, 4023)', '(0008, 1140)', '(0040, A172)',
                              '(0038, 0004)', '(0010, 1100)', '(0008, 1120)', '(0008, 1111)', '(0400, 0403)', '(0008, 1155)',
                              '(0004, 1511)', '(0008, 1110)', '(0008, 0092)', '(0008, 0096)', '(0008, 0090)', '(0008, 0094)',
                              '(0010, 2152)', '(3006, 00C2)', '(0040, 0275)', '(0032, 1070)', '(0040, 1400)', '(0032, 1060)',
                              '(0040, 1001)', '(0040, 1005)', '(0000, 1001)', '(0032, 1032)', '(0032, 1033)', '(0010, 2299)',
                              '(0010, 2297)', '(4008, 4000)', '(4008, 0118)', '(4008, 0042)', '(300E, 0008)', '(0040, 4034)',
                              '(0038, 001E)', '(0040, 000B)', '(0040, 0006)', '(0040, 0004)', '(0040, 0005)', '(0040, 0007)',
                              '(0040, 0011)', '(0040, 4010)', '(0040, 0002)', '(0040, 4005)', '(0040, 0003)', '(0040, 0001)',
                              '(0040, 4027)', '(0040, 0010)', '(0040, 4025)', '(0032, 1020)', '(0032, 1021)', '(0008, 0021)',
                              '(0008, 103E)', '(0020, 000E)', '(0008, 0031)', '(0038, 0062)', '(0038, 0060)', '(0010, 21A0)',
                              '(0008, 0018)', '(0008, 2112)', '(3008, 0105)', '(0038, 0050)', '(0018, 9516)', '(0008, 1010)',
                              '(0088, 0140)', '(0032, 4000)', '(0008, 0020)', '(0008, 1030)', '(0020, 0010)', '(0032, 0012)',
                              '(0020, 000D)', '(0008, 0030)', '(0020, 0200)', '(0018, 2042)', '(0040, A354)', '(0040, DB0D)',
                              '(0040, DB0C)', '(4000, 4000)', '(2030, 0020)', '(0008, 0201)', '(0088, 0910)', '(0088, 0912)',
                              '(0088, 0906)', '(0088, 0904)', '(0062, 0021)', '(0008, 1195)', '(0040, A124)', '(0040, A352)',
                              '(0040, A358)', '(0040, A088)', '(0040, A075)', '(0040, A073)', '(0040, A027)', '(0038, 4000)']
    '''

    '''
    Iterates through the files in the source directory,
    creates Patient objects and stores the dicom objects
    with the correct Patient object
    '''
    def populatePatientLibrary(self):
        #go through every file in directory
        #use magic to determine if dicom file
        #if dicom file, check if name not seen
        #if seen -> add file to correct patient in dict
        #if new -> create Patient object, add initial
        #dicom object to Patient, add Patient to dict

        from Patient import Patient

        for root, directories, filenames in os.walk(self.sourceDir):
            for filename in filenames:
                filePath = os.path.join(root, filename)
                mime = magic.Magic(mime=True)

                #determines the mime type of every file
                type = mime.from_file(filePath)

                #creates pydicom object for all files
                #with MIME type of DICOM

                if type == 'application/dicom':
                    fileValid = True
                    ds = dicom.read_file(filePath)
                    try:
                        pName = ds.PatientsName
                        pBday = ds.PatientBirthDate
                        sDate = ds.AcquisitionDate
                    except (AttributeError):
                        print "File: '" + filename + "' did not have the required attributes so it was not imported"
                        fileValid = False

                    if fileValid:
                        pIdent = pName+pBday+sDate
                        #if patient already seen, add ds to Patient
                        if pIdent in self.PatientObjects:
                            self.PatientObjects[pIdent].add_dicomObject(ds)
                        #if unseen patient name, create new Patient with ds
                        else:
                            patient = Patient(ds)
                            self.PatientObjects[pIdent] = patient

    def basicAnonymizeLibrary(self):
        # iterate through every patient in library
        idCount = 100000
        for name, patient in self.PatientObjects.iteritems():
            # increments the id
            self.tagsAnon[(0x0010, 0x0020)] = str(idCount)
            idCount = idCount + 1

            # iterate through every dicom file selected for anonymization
            for ds in patient.usedFiles:
                for tag, value in self.tagsAnon.iteritems():
                    if value == '#':
                        try:
                            del ds[tag]
                        except:
                            # the tag didn't exist in the first place
                            pass
                    else:
                        try:
                            ds[tag].value = value
                        except:
                            # tag didn't exist
                            pass

    def testLibrary(self):
        import os.path
        for name, value in self.PatientObjects.iteritems():
            files = value.unusedFiles
            for f in files:
                print os.path.basename(os.path.normpath(f.filename))


def main():
    # for CLI
    path = input("Enter dir path: ")
    pLib = PatientLibrary(path)
    pLib.populatePatientLibrary()
    pLib.testLibrary()


if __name__ == "__main__":
    main()