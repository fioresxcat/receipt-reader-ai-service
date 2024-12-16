import os
import pdb
import cv2
import numpy as np

from modules.base_module import BaseModule
from utils.utils import total_time

from .post_process_coopmart.post_processor import PostProcessorCOOPMART
from .post_process_nova.post_processor import PostProcessorNOVA
from .post_process_brg.post_processor import PostProcessorBRG
from .post_process_dmx.post_processor import PostProcessorDMX
from .post_process_emart.post_processor import PostProcessorEMART
from .post_process_hc.post_processor import PostProcessorHC
from .post_process_lamthao.post_processor import PostProcessorLAMTHAO
from .post_process_nuty.post_processor import PostProcessorNUTY
from .post_process_tgsf.post_processor import PostProcessorTGSF
from .post_process_711.post_processor import PostProcessor711
from .post_process_bhx.post_processor import PostProcessorBHX
from .post_process_newbigc.post_processor import PostProcessorNEWBIGC
from .post_process_go.post_processor import PostProcessorGO
from .post_process_topmarket.post_processor import PostProcessorTOPMARKET
from .post_process_gs25.post_processor import PostProcessorGS25
from .post_process_newgs25.post_processor import PostProcessorNewGS25
from .post_process_vinmart.post_processor import PostProcessorVINMART
from .post_process_winmart.post_processor import PostProcessorWINMART
from .post_process_base.post_processor import PostProcessorBASE
from .post_process_aeon.post_processor import PostProcessorAEON
from .post_process_aeoncitimart.post_processor import PostProcessorAEONCITIMART
from .post_process_lotte.post_processor import PostProcessorLOTTE
from .post_process_mega.post_processor import PostProcessorMEGA
from .post_process_tgs.post_processor import PostProcessorTGS
from .post_process_satra.post_processor import PostProcessorSATRA
from .post_process_lanchi.post_processor import PostProcessorLANCHI
from .post_process_oldbigc.post_processor import PostProcessorOLDBIGC
from .post_process_guardian.post_processor import PostProcessorGUARDIAN
from .post_process_nguyenkim.post_processor import PostProcessorNGUYENKIM
from .post_process_fujimart.post_processor import PostProcessorFUJIMART
from .post_process_heineken.post_processor import PostProcessorHEINEKEN
from .post_process_heineken_2024.post_processor import PostProcessorHEINEKEN2024
from .post_process_bitis.post_processor import PostProcessorBITIS
from .post_process_coopfood.post_processor import PostProcessorCOOPFOOD
from .post_process_ministop.post_processor import PostProcessorMINISTOP
from .post_process_familymart.post_processor import PostProcessorFAMILYMART
from .post_process_circlek.post_processor import PostProcessorCIRCLEK
from .post_process_pizzacompany.post_processor import PostProcessorPIZZACOMPANY
from .post_process_donchicken.post_processor import PostProcessorDONCHICKEN
from .post_process_lotteria.post_processor import PostProcessorLOTTERIA
from .post_process_bhd.post_processor import PostProcessorBHD
from .post_process_kfc.post_processor import PostProcessorKFC
from .post_process_okono.post_processor import PostProcessorOKONO
from .post_process_galaxy_cinema.post_processor import PostProcessorGALAXYCINEMA
from .post_process_pepperlunch.post_processor import PostProcessorPEPPERLUNCH
from .post_process_cheers.post_processor import PostProcessorCHEERS
from .post_process_bsmart.post_processor import PostProcessorBSMART
from .post_process_lottecinema.post_processor import PostProcessorLOTTECINEMA
from .post_process_bonchon.post_processor import PostProcessorBONCHON
from .post_process_bhx_2024.post_processor import PostProcessorBHX2024
from .post_process_kingfood.post_processor import PostProcessorKINGFOOD
from .post_process_globalx.post_processor import PostProcessorGLOBALX
from .post_process_sukiya.post_processor import PostProcessorSUKIYA
from .post_process_launuongmai.post_processor import PostProcessorLAUNUONGMAI
from .post_process_tiemlaunho.post_processor import PostProcessorTIEMLAUNHO
from .post_process_sayaka.post_processor import PostProcessorSAYAKA
from .post_process_ushimania.post_processor import PostProcessorUSHIMANIA
from .post_process_yoshinoya.post_processor import PostProcessorYOSHINOYA



class PostProcessor(BaseModule):
    instance = None
    
    def __init__(self, common_config, model_config):
        super(PostProcessor, self).__init__(common_config, model_config)
        self.post_processor = {
            'coopmart': PostProcessorCOOPMART(common_config, model_config),
            'coopfood': PostProcessorCOOPFOOD(common_config, model_config),
            'nova': PostProcessorNOVA(common_config, model_config),
            'emart': PostProcessorEMART(common_config, model_config),
            'brg': PostProcessorBRG(common_config, model_config),
            'dmx': PostProcessorDMX(common_config, model_config),
            'hc': PostProcessorHC(common_config, model_config),
            'lamthao': PostProcessorLAMTHAO(common_config, model_config),
            'nuty': PostProcessorNUTY(common_config, model_config),
            'tgsf': PostProcessorTGSF(common_config, model_config),
            '711': PostProcessor711(common_config, model_config),
            'bhx': PostProcessorBHX(common_config, model_config),
            'new_bigc': PostProcessorNEWBIGC(common_config, model_config),
            'go': PostProcessorGO(common_config, model_config),
            'topmarket': PostProcessorTOPMARKET(common_config, model_config),
            'vinmart': PostProcessorVINMART(common_config, model_config),
            'vinmartplus': PostProcessorWINMART(common_config, model_config),
            'gs25': PostProcessorGS25(common_config, model_config),
            'new_gs25': PostProcessorNewGS25(common_config, model_config),
            'aeon': PostProcessorAEON(common_config, model_config),
            'aeoncitimart': PostProcessorAEONCITIMART(common_config, model_config),
            'lotte': PostProcessorLOTTE(common_config, model_config),
            'mega': PostProcessorMEGA(common_config, model_config),
            'thegioisua': PostProcessorTGS(common_config, model_config),
            'satra': PostProcessorSATRA(common_config, model_config),
            'old_bigc': PostProcessorOLDBIGC(common_config, model_config),
            'lanchi': PostProcessorLANCHI(common_config, model_config),
            'guardian': PostProcessorGUARDIAN(common_config, model_config),
            'nguyenkim': PostProcessorNGUYENKIM(common_config, model_config),
            'fujimart': PostProcessorFUJIMART(common_config, model_config),
            'heineken': PostProcessorHEINEKEN(common_config, model_config),
            'heineken_2024': PostProcessorHEINEKEN2024(common_config, model_config),
            'bitis': PostProcessorBITIS(common_config, model_config),
            'ministop': PostProcessorMINISTOP(common_config, model_config),
            'family_mart': PostProcessorFAMILYMART(common_config, model_config),
            'circlek': PostProcessorCIRCLEK(common_config, model_config),
            'pizza_company': PostProcessorPIZZACOMPANY(common_config, model_config),
            'don_chicken': PostProcessorDONCHICKEN(common_config, model_config),
            'lotteria': PostProcessorLOTTERIA(common_config, model_config),
            'bhd': PostProcessorBHD(common_config, model_config),
            'kfc': PostProcessorKFC(common_config, model_config),
            'okono': PostProcessorOKONO(common_config, model_config),
            'galaxy_cinema': PostProcessorGALAXYCINEMA(common_config, model_config),
            'pepper_lunch': PostProcessorPEPPERLUNCH(common_config, model_config),
            'cheers': PostProcessorCHEERS(common_config, model_config),
            'bsmart': PostProcessorBSMART(common_config, model_config),
            'lotte_cinema': PostProcessorLOTTECINEMA(common_config, model_config),
            'bonchon': PostProcessorBONCHON(common_config, model_config),
            'bhx_2024': PostProcessorBHX2024(common_config, model_config),
            'kingfood': PostProcessorKINGFOOD(common_config, model_config),
            'globalx': PostProcessorGLOBALX(common_config, model_config),
            'sukiya': PostProcessorSUKIYA(common_config, model_config),
            'launuongmai': PostProcessorLAUNUONGMAI(common_config, model_config),
            'tiemlaunho': PostProcessorTIEMLAUNHO(common_config, model_config),
            'sayaka': PostProcessorSAYAKA(common_config, model_config),
            'ushimania': PostProcessorUSHIMANIA(common_config, model_config),
            'yoshinoya': PostProcessorYOSHINOYA(common_config, model_config),
            'winlife': PostProcessorVINMART(common_config, model_config)
        }


    @staticmethod
    def get_instance(common_config, model_config):
        if PostProcessor.instance is None:
            PostProcessor.instance = PostProcessor(common_config, model_config)
        return PostProcessor.instance
        

    @total_time
    def predict(self, request_id, inp, out, metadata):
        inp_data = inp.get_data()
        inp_data['result'] = {}
        result = self.post_processor[inp_data['mart_type']].predict(request_id, inp_data)
        pdb.set_trace()
        metadata = self.add_metadata(metadata, 1, 1)
        result['result']['type'] = inp_data['mart_type']
        if result['result']['type'] in ['vinmart', 'vinmartplus']:
            if '+' in result['result']['mart_name'] and 'C+' not in result['result']['mart_name']:
                result['result']['type'] = 'winmartplus'
            else:
                result['result']['type'] = 'winmart'
        elif result['result']['type'] in ['heineken', 'heineken_2024']:
            result['result']['type'] = 'heineken'
        out.set_data(result)
        return out, metadata

