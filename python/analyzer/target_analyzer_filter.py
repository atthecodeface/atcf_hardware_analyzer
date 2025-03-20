#a Documentation
"""
CSRs for apb_target_analyzer_cfg and Filter classes
"""

#a Imports
from cdl.utils.csr   import Csr, CsrField, CsrFieldZero, Map, MapCsr

#a Filter classes
#c Filter
class Filter:
    """Analyzer trace filter configuration

    Create with mask-match-value for those bits that must match, and a
    must-change bit set for those that must change (which is distinct
    from the ones that must be a certain value)

    """
    match_mask = (0,0,0,0)
    match_value = (0,0,0,0)
    must_change = (0,0,0,0)
    must_be_nonzero = None
    #f __init
    def __init__(self, mm=None, mv=None, mc=None, nz=None):
        if mm is not None: self.match_mask = mm
        if mv is not None: self.match_value = mv
        if mc is not None: self.must_change = mc
        if nz is not None: self.must_be_nonzero = nz
        self.data = (0,0,0,0)
        self.accept_unchanging = 1
        if self.must_be_nonzero == (0,0,0,0):
            self.must_be_nonzero = None
            pass
        if self.must_change[0]!=0:self.accept_unchanging = 0 
        if self.must_change[1]!=0:self.accept_unchanging = 0 
        if self.must_change[2]!=0:self.accept_unchanging = 0 
        if self.must_change[3]!=0:self.accept_unchanging = 0
        self.match_value = (self.match_mask[0] & self.match_value[0],
                            self.match_mask[1] & self.match_value[1],
                            self.match_mask[2] & self.match_value[2],
                            self.match_mask[3] & self.match_value[3],
                            )
        for i in range(4):
            assert(self.match_mask[i] & self.must_change[i] == 0, "Bad mask / match change combination in {i}")
            pass
        if self.must_be_nonzero is not None:
            for i in range(4):
                assert(self.match_mask[i] & self.must_be_nonzero[i] == 0, "Bad mask / match non-zero combination in {i}")
                pass
            pass
        assert( (self.accept_unchanging==0) or (self.must_be_nonzero == None),
                "Cannot require changing data and some as must be nonzero" )
        pass
    #f reset
    def reset(self):
        self.data = (0,0,0,0)
        pass
    #f write_filter_cfg
    def write_filter_cfg(self, o, pfx):
        getattr(o, pfx+"__accept_unchanging").drive(self.accept_unchanging)
        getattr(o, pfx+"__mask__data_0").drive(self.match_mask[0])
        getattr(o, pfx+"__mask__data_1").drive(self.match_mask[1])
        getattr(o, pfx+"__mask__data_2").drive(self.match_mask[2])
        getattr(o, pfx+"__mask__data_3").drive(self.match_mask[3])
        value = [(self.match_value[i] & self.match_mask[i]) | self.must_change[i]
                 for i in range(4)]
        if self.must_be_nonzero is not None:
            value = [value[i] | self.must_be_nonzero[i]
                     for i in range(4)]
            pass
        getattr(o, pfx+"__value__data_0").drive(value[0])
        getattr(o, pfx+"__value__data_1").drive(value[1])
        getattr(o, pfx+"__value__data_2").drive(value[2])
        getattr(o, pfx+"__value__data_3").drive(value[3])
        pass
    #f apb_writes
    def apb_writes(self, map):
        writes = []
        if self.accept_unchanging:
            writes.append((map.filter_base, 3))
            pass
        else:
            writes.append((map.filter_base, 1))
            pass
        writes.append( (map.filter_mask0, self.match_mask[0] ) )
        writes.append( (map.filter_mask1, self.match_mask[1] ) )
        writes.append( (map.filter_mask2, self.match_mask[2] ) )
        writes.append( (map.filter_mask3, self.match_mask[3] ) )

        value = [(self.match_value[i] & self.match_mask[i]) | self.must_change[i]
                 for i in range(4)]
        if self.must_be_nonzero is not None:
            value = [value[i] | self.must_be_nonzero[i]
                     for i in range(4)]
            pass

        writes.append( (map.filter_match0, value[0]) )
        writes.append( (map.filter_match1, value[1]) )
        writes.append( (map.filter_match2, value[2]) )
        writes.append( (map.filter_match3, value[3]) )
        return writes

    #f apply
    def apply(self, data):
        mismatches = False
        for i in range(4):
            if data[i] & self.match_mask[i] != self.match_value[i]: mismatches = True
            pass
        if mismatches:
            return False
        if self.accept_unchanging:
            if self.must_be_nonzero is not None:
                matched = False
                for i in range(4):
                    if (data[i] & self.must_be_nonzero[i]) != 0:
                        matched = True
                        pass
                    pass
                if not matched:
                    return False
                pass
            self.data = data
            return True
        changed = False
        for i in range(4):
            if data[i] & self.must_change[i] != self.data[i] & self.must_change[i]: changed = True
            pass
        if changed:
            self.data = data
            pass
        return changed
    pass

class FilterAcceptAll(Filter):
    """
    An analyzer trace filter configuration that accepts everything
    """
    match_mask = (0,0,0,0)
    match_value = (0,0,0,0)
    must_change = (0,0,0,0)

class FilterChanging(Filter):
    """
    An analyzer trace filter configuration that accepts all changing
    """
    match_mask = (0,0,0,0)
    match_value = (0,0,0,0)
    must_change = (0xffffffff,0xffffffff,0xffffffff,0xffffffff)
    
