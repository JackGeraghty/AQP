DEFAULT_DRAW_OPTIONS = {'shape': 'box', 'style': 'filled', 'fillcolor': 'white'}
DEFAULT_AQP_OPTIONS = {'fillcolor': '#008900B3'}
DEFAULT_VISQOL_OPTIONS = {'fillcolor': '#6495EDB3'}

class DrawOptionsBuilder:
    
    def __init__(self, options: dict=None):
        self.draw_options = {}
        self.with_options(DEFAULT_DRAW_OPTIONS)
        
        if options:
            self.with_options(options)
            
    def with_option(self, key, value):
        self.draw_options[key] = value
        return self

        
    def with_options(self, options: dict):
        self.draw_options.update(options)
        return self
    

class AQPOptionsBuilder(DrawOptionsBuilder):
    
    def __init__(self, draw_options=None):
        super().__init__(DEFAULT_AQP_OPTIONS)
        if draw_options:
            self.with_options(draw_options)
        

class ViSQOLOptionsBuilder(DrawOptionsBuilder):
    
    def __init__(self, draw_options=None):
        super().__init__(DEFAULT_VISQOL_OPTIONS)
        if draw_options:
            self.with_options(draw_options)