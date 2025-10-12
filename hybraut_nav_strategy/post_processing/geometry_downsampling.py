""" 
Geometric Downsampling

This is a post processing method for the strategic global path,
We utilize (RDP) Simplification.
    -   This removes intermediate waypoints that don't significantly
        change the path shape
    -   Parameter: epsilon (maximum allowed perpendicular deviation)
    -   Ideal for open-water/global paths where you want to maintain overall shape but 
        lose the small fluctuations which are insignificat when tactical and controller 
        layers are running
    -   Preserves coreners/turns automatically if epsilon is tuner right
    
    
"""

""" 

maybe I should do curature based downsampling (maneuver fidelity)
"""


