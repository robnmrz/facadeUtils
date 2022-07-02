import numpy as np

class BaseWindow():
    """
    Class to define a basic windows
    Example steps of defining a window
    ----------
    (1) window = BaseWindow()
    ----------
    Necessary Parameters:
    (1) height: window height in mm
    (2) width: window width in mm
    (3) glazing: total glas thickness in mm
    (4) opening_direction:  "inward", "outward"
    (5) window_type: type of window 1: roof, 2: bottom-hung, 3: top-hung, 4: side-hung
    """
    
    def __init__(
        self,
        height: int, 
        width: int, 
        glazing: float, 
        opening_direction: str,
        window_type: int,
        hinge_position: tuple = (10.,10.),
        wind_value: float = 0.,
        wind_type: str = "speed"
    ):
        # geometry and glas
        self.height = height
        self.width = width
        self.surface = self.height*self.width/1000000
        
        # load
        self.glazing = glazing
        self.sash_weight = self.surface*(self.glazing/1000)*2500
        self.filling_weight = self.sash_weight/self.surface if self.surface != 0 else 0
        
        # opening direction
        self.direction = opening_direction
        
        # window type
        self.type = window_type
        
        # environmental influences
        self.set_wind_load(value=wind_value, load_type=wind_type)
        
        # hinge position
        self.hinge_position = hinge_position
        
    def set_wind_load(self, value, load_type):
        
        if load_type == 'speed':
            self.wind_speed = value
            self.wind_pressure = 0.5 * 1.25 * value**2
            self.wind_load_N = self.wind_pressure * self.surface
        elif load_type == 'pressure':
            self.wind_pressure = value
            self.wind_load_N = self.wind_pressure * self.surface
            self.wind_speed = np.sqrt(self.wind_pressure/(0.5 * 1.25))
        else:
            raise ValueError("Unexpected load type please select either 'speed' (default) or 'pressure'")
    
    def load_moment(
        self,
        opening_angle=None,
        i_dim=57,
        inclination=90,
        max_angle=60
    ):
        if opening_angle is None:
            opening_angle = np.linspace(
                0, 
                max_angle,
                max_angle + 1
            )
        else:
            opening_angle = np.linspace(
                0, 
                opening_angle,
                opening_angle + 1
            )
            
        angle_rad = np.radians(opening_angle)
        weight_force = self.sash_weight * 9.81
        self.inclination = inclination
        
        if self.direction == "outward":
            self.wind_load_N = self.wind_load_N*(-1)
        
        if self.type == 2:
            self.inclination = self.inclination*(-1)
        
        inclination_rad = np.radians(self.inclination)
        
        inclination_red = {
        "sin": np.sin(inclination_rad),
        "cos": np.cos(inclination_rad)
        }
        
        centre_shift = {
        "sin": i_dim * np.sin(angle_rad),
        "cos": i_dim * np.cos(angle_rad)
        }
        
        lever_arm = {
            "sin": (
                self.height / 2 + self.hinge_position[1]
            )*np.sin(angle_rad),
            
            "cos": (
                -self.height / 2 + self.hinge_position[1]
            )*np.cos(angle_rad)
        }
        
        # force component in x direction
        load_comp_x = weight_force * inclination_red["sin"]\
                    *(lever_arm["sin"]-centre_shift["cos"])
        
        # force component in y direction
        load_comp_y = weight_force * inclination_red["cos"]\
                    *(lever_arm["cos"]-centre_shift["sin"])
        
        load_moment = (load_comp_x + load_comp_y) / 1000
        load_moment_with_wind = (load_comp_x + load_comp_y) / 1000
        
        if self.wind_load_N:
            if (180.0001-(self.inclination % 360)) < 0:
                self.wind_load_N = self.wind_load_N*(-1) 
            
            load_moment_with_wind = load_moment + self.wind_load_N * self.height / 2000 *\
                          abs(np.sin(inclination_rad+angle_rad))*np.sin(inclination_rad+angle_rad)
        
        load = dict(enumerate(np.round(load_moment.flatten(),2), 0))
        load_with_wind = dict(enumerate(np.round(load_moment_with_wind.flatten(),2), 0))

        return load, load_with_wind