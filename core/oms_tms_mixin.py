"""
###############################################################################
# OMSTMSMixin - Lazy initialization pattern for OMS/TMS at highest level
###############################################################################
"""

import logging

# Set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OMSTMSMixin:
    """
    ###############################################################################
    # OMS/TMS Mixin - Lazy initialization at highest hierarchy level
    # 
    # Pattern:
    # - If no parent: Create OMS/TMS (this is highest level)
    # - If parent exists: Inherit parent's OMS/TMS
    # 
    # This ensures ONE OMS/TMS instance per hierarchy branch
    ###############################################################################
    """
    
    def _initialize_or_inherit_systems(self, parent=None, enable_event_log=False):
        """
        Initialize OMS/TMS if this is the highest level,
        otherwise inherit from parent
        
        Args:
            parent: Parent object (TradeAccount, Fund, or Portfolio)
            enable_event_log: If True, enables internal event logging (for debugging)
        """
        if parent is not None:
            # Inherit from parent
            self._oms = parent._oms
            self._tms = parent._tms
            self._is_oms_tms_owner = False
            
            # Log inheritance
            parent_name = getattr(parent, 'name', None) or \
                         getattr(parent, 'account_name', None) or \
                         getattr(parent, 'fund_name', None) or \
                         getattr(parent, 'portfolio_name', None)
            
            logger.debug(f"{self.__class__.__name__} '{self.name}' "
                        f"inherited OMS/TMS from {parent.__class__.__name__} '{parent_name}'")
        else:
            # This is the highest level - create OMS/TMS
            from .trade_management import TradeManagementSystem
            from .order_management import OrderManagementSystem
            
            self._tms = TradeManagementSystem(enable_event_log=enable_event_log)
            self._oms = OrderManagementSystem(self._tms, enable_event_log=enable_event_log)
            self._is_oms_tms_owner = True
            
            # Log creation
            logger.info(f"✅ {self.__class__.__name__} '{self.name}' "
                       f"created OMS/TMS (highest level)")
    
    @property
    def oms(self):
        """
        Get OMS instance
        Note: This is internal - users should not access directly
        """
        return self._oms
    
    @property
    def tms(self):
        """
        Get TMS instance
        Note: This is internal - users should not access directly
        """
        return self._tms
    
    @property
    def is_oms_tms_owner(self):
        """Check if this instance owns the OMS/TMS"""
        return self._is_oms_tms_owner
    
    def _get_oms_tms_owner(self):
        """
        Find who owns the OMS/TMS in hierarchy
        
        Returns:
            Object that owns the OMS/TMS
        """
        if self._is_oms_tms_owner:
            return self
        
        # Walk up hierarchy to find owner
        if hasattr(self, 'portfolio') and self.portfolio:
            return self.portfolio._get_oms_tms_owner()
        if hasattr(self, 'fund') and self.fund:
            return self.fund._get_oms_tms_owner()
        if hasattr(self, 'trade_account') and self.trade_account:
            return self.trade_account._get_oms_tms_owner()
        
        return self

