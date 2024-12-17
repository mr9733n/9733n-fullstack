from app.utils.cache_manager import CacheManager
from app.helpers.common_helper import CommonHelper
from app.helpers.onlinesim_helper import OnlinesimHelper

def setup_dependencies(service_configs):
    common_helper = CommonHelper()
    onlinesim_helper = OnlinesimHelper()
    cache_manager = CacheManager(service_configs)
    return cache_manager, common_helper, onlinesim_helper
