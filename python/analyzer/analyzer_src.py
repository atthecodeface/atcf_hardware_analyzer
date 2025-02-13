#c AnalyzerSrc
class AnalyzerSrc:
    data_cfg = [1,1,1,1]
    tgt_mode = 1
    def __init__(self, data=None, data_cfg=None):
        self.data = [0,0,0,0]
        if data is not None:
            self.data = data[:]
            pass
        if data_cfg is not None:
            self.data_cfg = data_cfg
            pass
        pass
    #f apb_writes
    def apb_writes(self, map):
        cfg = self.tgt_mode
        for i in range(4):
            cfg = cfg | (self.data_cfg[i] << (16+i*4))
            pass
        writes = []
        writes.append( (map.cfg, 0) )
        writes.append( (map.data0, self.data[0] ) )
        writes.append( (map.data1, self.data[1] ) )
        writes.append( (map.data2, self.data[2] ) )
        writes.append( (map.data3, self.data[3] ) )
        # Write the cfg last so that the data does not start changing
        writes.append((map.cfg, cfg))
        return writes

    def next_data(cfg, d):
        if cfg == 1:
            return d+1
        return d
    def next_valid(self):
        while True:
            for i in range(4):
                self.data[i] = AnalyzerSrc.next_data(self.data_cfg[i], self.data[i])
                pass
            break
        return tuple(self.data)
    pass

