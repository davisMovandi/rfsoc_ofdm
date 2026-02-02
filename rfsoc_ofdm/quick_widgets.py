import ipywidgets as ipw

class DropDown():
    """Helper class for dropdown widgets.
    """
    def __init__(self,
                 callback,
                 options,
                 value,
                 description,
                 dict_id = '',
                 description_width='150px',
                 layout_width='300px'):
    
        def on_value_change(change):
            callback(change['new'])
            
        self._dict_id = dict_id
        self._dropdown = ipw.Dropdown(options=options,
                                      value=value,
                                      description=description,
                                      style={'description_width': description_width},
                                      layout = {'width': layout_width},)
        self._dropdown.observe(on_value_change, names='value')
        
    @property
    def value(self):
        return self._dropdown.value
    
    @value.setter
    def value(self, value):
        self._dropdown.value = value
        
    @property
    def description(self):
        return self._dropdown.description
    
    @description.setter
    def description(self, value):
        self._dropdown.description = value
        
    @property
    def options(self):
        return self._dropdown.options
    
    @options.setter
    def options(self, value):
        self._dropdown.options = value
        
    def get_widget(self):
        return self._dropdown
    

class UserInput():
    """
    Helper class for user input widgets.
    """

    def __init__(self,
                 callback,
                 value,
                 description,
                 dict_id = '',
                 min=0,
                 max=100.0,
                 step=0.1,
                 readout_format='.3f'):
    
        def on_value_change(change):
            callback(change['new'])
            
        self._dict_id = dict_id
        self._user_input = ipw.FloatSlider(value=value,
                                           min=min,
                                           max=max,
                                           step=step,
                                           description=description,
                                           disabled=False,
                                           continuous_update=True,
                                           orientation='horizontal',
                                           readout=True,
                                           readout_format=readout_format)
        
        self._user_input.observe(on_value_change, names='value')

        callback(self._user_input.value)
        
    @property
    def value(self):
        return self._user_input.value
    
    @value.setter
    def value(self, value):
        self._user_input.value = value
        
    @property
    def description(self):
        return self._user_input.description
    
    @description.setter
    def description(self, value):
        self._user_input.description = value
        
    def get_widget(self):
        return self._user_input